#!/usr/bin/env python

PROGRAM_NAME = "ChemHTPS"
PROGRAM_VERSION = "v0.1.0"
REVISION_DATE = "2019-01-10"
AUTHORS = "Johannes Hachmann (hachmann@buffalo.edu), William Evangelista (wevangel@buffalo.edu) and Yudhajit Pal (yudhajit@buffalo.edu)"
CONTRIBUTORS = """   Mohammad Atif Faiz Afzal and Gaurav Vishwakarma (library generation), and Mojtabah Haghighatlari (documentation)   """
DESCRIPTION = "ChemHTPS is a virtual high-throughput screening program suite for the chemical and materials sciences."

###################################################################################################
# TASKS OF THIS MODULE:
# -main function
###################################################################################################


###################################################################################################
# Desired workflow (corresponding to modules, that can be called from this main module):
# 1) set up file/dir structure for a new project (setup_project)
# 2) create a library of structures (generate_structurelib)
# 3) read in the library of structure into database (populate_db)
# 4) create geometries (generate_geometries)
# 5) connect geometries to the library (populate_db)
# 6) create jobs, put jobs into pool (generate_jobs)
# 7) prioritize pool
# 8) run jobs
# 9) parse jobs
# 10) ...
###################################################################################################

import sys
import os
import time
import argparse

from misc import (banner,
                  format_invoked_opts,
                  tot_exec_time_str,
                  intermed_exec_timing,
                  intermed_process_timing,
                  std_datetime_str,
                  chk_rmfile,
                  chk_mkdir)

from project_setup import setup_project
from library_generator import (generate_structurelib,
                               generate_geometries)
from db_feeder import populate_db
from job_generator import (generate_jobs,
                           prioritize_pool)
from job_feeder import feed_jobs
#from feeder_options import feed_options

###################################################################################################
# Necessary Functions:


def config_read(config, args):
    """
        Reads options from the config file
        Based on options following the format
        Option_name = The option

        :param str config: The path of the config file
        :return config_opts: The options read from the config file
        :rtype: dict
    """
    opt_rflag = 1
    config_opts = {}
    with open(config, 'r') as config:
        while True:
            line = config.readline()
            if not line: break
            line = line.rstrip('\n')
            words = line.split(' = ')
            if line == '': continue
            if '--'+line not in args and len(words) == 1: 
                if '--feedjobs_remote' in args and line == 'feedjobs':
                    opt_rflag = 1
                    continue
                print ("rejected line: "+line)
                opt_rflag = 0 
                continue
            if opt_rflag == 1:
                if len(words) > 2:
                    sys.exit('Bad option in config file')
            if len(words) == 2:
                print (line)
                config_opts[words[0].strip()] = words[1].strip()
            if len(words) == 1 and '--'+line in args: opt_rflag = 1
        config.close()
    return config_opts



def config_log(project_name, logfile):
    """
        Puts the contents of the .config file into the log_file
    """
    cwd = os.getcwd()
    if cwd[-len(project_name):] == project_name:
        tmp_str = 'cat ' + project_name + '.config >> ' + logfile.name 
        os.system(tmp_str)

    with open(project_name + '.config','r') as config:
        for line in config:
            print (line.rstrip())

    tmp_str = "------------------------------------------------------------------------------ "
    print (tmp_str)
    logfile.write(tmp_str + '\n')
    return 0


###################################################################################################

def main(args, commline_list):
    """
        Driver of ChemHTPS.

        :param object args: The arguments passed from argparse
        :param list commline_list: What was typed at the command line to execute the program
    """
    logfile = open(args.logfile,'a')
    error_file = open(args.error_file,'a')

    time_start = time.time()

    banner_list = banner(PROGRAM_NAME, PROGRAM_VERSION, REVISION_DATE, AUTHORS, CONTRIBUTORS, DESCRIPTION)
    for line in banner_list:
        print (line)
        logfile.write(line + '\n')

    if args.setup_project == False:
        try:
            user_name = config_opts['user_name']
        except:
            pass
        if args.feedjobs_remote:
            feed_jobs(args.project_name, user_name, config_opts)

        fopts_list = format_invoked_opts(args,commline_list)
        for line in fopts_list:
            print (line)
            logfile.write(line + '\n')
        tmp_str = "------------------------------------------------------------------------------ "
        print (tmp_str)
        logfile.write(tmp_str + '\n')
  
        config_log(args.project_name, logfile)

    if args.setup_project:
        setup_project(args.project_name)

    if args.generatelib:
        generate_structurelib()
        populate_db("moleculegraph")
        generate_geometries(args.project_name,config_opts)
        populate_db("moleculegeom")

    # TODO: we may want to put a db-based bookkeeping step in here                

    if args.generatejobs:
        generate_jobs(args.project_name,config_opts)
    
    if args.prioritizepool:
        prioritize_pool(config_opts)

    try:
        user_name = config_opts['user_name']
    except:
        pass
    if args.feedjobs and not args.feedjobs_remote:
        if config_opts['feed_local'] == 'FALSE':
            tmp_str = 'sbatch job_templates/' + args.project_name + '_feedjobs.sh'
            os.system(tmp_str)
        elif config_opts['feed_local'] == 'TRUE':
            feed_jobs(args.project_name, user_name, config_opts)
    
    print ("Chemhtps Execution Done !")
    tmp_str = tot_exec_time_str(time_start) + "\n" + std_datetime_str()
    print (tmp_str  + '\n\n\n')
    logfile.write(tmp_str + '\n\n\n\n')
    logfile.close()    
    error_file.close()
        
    # check whether error_file contains content
    chk_rmfile(args.error_file)
    
    return 0    #successful termination of program
    
##################################################################################################

if __name__ == "__main__":
    usage_str = "usage: %(prog)s [options] arg"
    version_str = "%(prog)s " + PROGRAM_VERSION
    parser = argparse.ArgumentParser(usage=usage_str)

    defaults = {'project_name':None, 'setup':False, 'generatelib':False, 'generatejobs':False, 'prioritize':False,
                'feedjobs':False, 'feedjobs_remote':False, 'job_sched':'SLURM',  'log':'ChemHTPS.log', 'err':'ChemHTPS.err', 'print':3}

    parser.add_argument('--version',
                        action='version',
                        version=version_str)

    parser.add_argument('--project_name',
                        dest='project_name',
                        default=defaults['project_name'],
                        help='name of the current project [default: %(default)s]')

    parser.add_argument('--setup_project',
                        dest='setup_project',
                        action='store_true',
                        default=defaults['setup'],
                        help='sets up the infrastructure for a new project [default: %(default)s]')

    parser.add_argument('--generatelib',
                        dest='generatelib',
                        action='store_true',
                        default=defaults['generatelib'],
                        help='generates a new screening library [default: %(default)s]')

    parser.add_argument('--generatejobs',
                        dest='generatejobs',
                        action='store_true',
                        default=defaults['generatejobs'],
                        help='generates computational chemistry jobs [default: %(default)s]')

    parser.add_argument('--prioritizepool',
                        dest='prioritizepool',
                        action='store_true',
                        default=defaults['prioritize'],
                        help='prioritizes the jobs pool [default: %(default)s]')

    parser.add_argument('--feedjobs',
                        dest='feedjobs',
                        action='store_true',
                        default=defaults['feedjobs'],
                        help='Runs the jobs from on the cluster [default: %(default)s]')

    parser.add_argument('--feedjobs_remote',
                        dest='feedjobs_remote',
                        action='store_true',
                        default=defaults['feedjobs_remote'],
                        help='Runs the jobs locally [default: %(default)s]')


    # specify log files 
    parser.add_argument('--logfile',
                        dest='logfile',
                        default=defaults['log'],
                        help='specifies the name of the log-file [default: %(default)s]')

    parser.add_argument('--errorfile',
                        dest='error_file',
                        default=defaults['err'],
                        help='specifies the name of the error-file [default: %(default)s]')

    parser.add_argument('--print_level',
                        dest='print_level',
                        default=defaults['print'],
                        help='specifies the print level for on screen and the logfile [default: %(default)s]')

    args = parser.parse_args(sys.argv[1:])
    cwd = os.getcwd()
    dirlist = os.listdir(cwd)
    # reading the config options by calling config_read function and getting the necessary config options
    if args.setup_project == False:
        for entry in dirlist:
            if '.config' in entry:
                config = entry
                try:
                    config_opts = config_read(config, sys.argv[1:])
                    print (config_opts)
                    no_config = False
                    if 'project_name' in config_opts:
                        args.project_name = config_opts['project_name']
                    if 'log_file' in config_opts:
                        args.logfile = config_opts['log_file']
                    if 'error_file' in config_opts:
                        args.errorfile = config_opts['error_file']
                except NameError:
                    no_config = True

    if cwd.rsplit('/')[-1] != args.project_name and args.setup_project == False:
        sys.exit("ChemHTPS must be run from inside the project directory, or with the setup_project flag.")
    elif args.setup_project == True and args.project_name == None:
        sys.exit("Need to give the project_name flag to setup a project.")
    elif cwd[-len(args.project_name):] == args.project_name and no_config == True:
        sys.exit("There is no config file in the project directory.")

    os.environ["LD_LIBRARY_PATH"] = ":/projects/academic/hachmann/packages/Anaconda"
    main(args, sys.argv)   #numbering of sys.argv is only meaningful if it is launched as main

