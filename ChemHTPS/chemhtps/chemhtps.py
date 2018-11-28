#!/usr/bin/env python

PROGRAM_NAME = "ChemHTPS"
PROGRAM_VERSION = "v0.0.1"
REVISION_DATE = "2015-06-24"
AUTHORS = "Johannes Hachmann (hachmann@buffalo.edu) and William Evangelista (wevangel@buffalo.edu)"
CONTRIBUTORS = """   Mohammad Atif Faiz Afzal (library generation)"""
DESCRIPTION = "ChemHTPS is a virtual high-throughput screening program suite for the chemical and materials sciences."

# Version history timeline (move to CHANGES periodically):
# v0.0.1 (2015-06-24): complete refactoring of original ChemHTPS code in new package format
# v0.1.0 (2016-02-24): alpha version

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


###################################################################################################
#TODO:
# -restructure more general functions into modules
# -put in a printlevel restriction for each print statement 
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
from feeder_options import feed_options

###################################################################################################
# Necessary Functions:


def config_read(config):
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
        count = 0
	while 1:
            line = config.readline()
            if not line: break
	    if line[0:2] == '@@': 
		opt_rflag = 0 
		continue
	    if line == '\n': continue
	    words = line.split(' = ')
            if opt_rflag == 1:
                if len(words) > 2:
                    sys.exit('Bad option in config file')
	        if len(words) == 2:
                	config_opts[words[0]] = words[1].rstrip('\n')
	    if len(words) == 1 and line[1] != '@':
		count += 1
		config_opts['run'+str(count)] = words[0][1:].rstrip('\n')
		opt_rflag = 1
        config.close()

    #print config_opts

    return config_opts



def config_log(project_name, logfile):
    # This part reads options from a .config file if your in the project directory
    cwd = os.getcwd()
    if cwd[-len(project_name):] == project_name:
        tmp_str = 'cat ' + project_name + '.config >> ' + logfile.name 
    	os.system(tmp_str)
    
    with open(project_name + '.config','r') as config:
	for line in config:
	    print line.rstrip()

    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
    logfile.write(tmp_str + '\n')
	


###################################################################################################

def main(args, commline_list):
    """
        Driver of ChemHTPS.

        :param object args: The arguments passed from argparse
        :param list commline_list: What was typed at the command line to execute the program
    """
    logfile = open(args.logfile,'a',0)
    error_file = open(args.error_file,'a',0)

    time_start = time.time()

    banner_list = banner(PROGRAM_NAME, PROGRAM_VERSION, REVISION_DATE, AUTHORS, CONTRIBUTORS, DESCRIPTION)
    for line in banner_list:
        print line
        logfile.write(line + '\n')

    try:
        user_name = config_opts['user_name']
    except:
        pass
    if args.feedjobs_remote:
        feed_jobs(args.project_name, user_name, config_opts)

    fopts_list = format_invoked_opts(args,commline_list)
    for line in fopts_list:
        print line
        logfile.write(line + '\n')
    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
    logfile.write(tmp_str + '\n')
    
    print "config options"
    logfile.write("config options\n")
    config_log(args.project_name, logfile)


    if args.setup_project:
# TODO: write test that args.project_name exists
        setup_project(args.project_name)


    if args.generatelib:
        generate_structurelib()
        populate_db("moleculegraph")
        generate_geometries(args.project_name,config_opts)
        populate_db("moleculegeom")
        logfile.write("config file after library_generator:\n")
        print "------------------------------------"
	print "config file after library_generator:"
        print "------------------------------------\n"
        config_log(args.project_name, logfile)

# TODO: we may want to put a db-based bookkeeping step in here                

    if args.generatejobs:
        generate_jobs(args.project_name,config_opts)
        logfile.write("config file after job_generator:\n")
        print "--------------------------------"
	print "config file after job_generator:"
        print "--------------------------------\n"
        config_log(args.project_name, logfile)
    
    if args.prioritizepool:
        prioritize_pool(config_opts)

    try:
        user_name = config_opts['user_name']
    except:
        pass
    if args.feedjobs and not args.feedjobs_remote:
	feed_options(args.project_name,config_opts)
        logfile.write("config file after feed_options:\n")
        print "-------------------------------"
	print "config file after feed_options:"
        print "-------------------------------\n"
        config_log(args.project_name, logfile)
	if config_opts['feed_local'] == 'FALSE':
	    tmp_str = 'sbatch job_templates/' + args.project_name + '_feedjobs.sh'
            os.system(tmp_str)
        elif config_opts['feed_local'] == 'TRUE':
            feed_jobs(args.project_name, user_name, config_opts)
    

    tmp_str = tot_exec_time_str(time_start) + "\n" + std_datetime_str()
    print tmp_str  + '\n\n\n'
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

    cwd = os.getcwd()
    dirlist = os.listdir(cwd)
    for entry in dirlist:
        if '.config' in entry:
            config = entry
    try:
        config_opts = config_read(config)
        no_config = False
        if 'project_name' in config_opts:
            defaults['project_name'] = config_opts['project_name']
	count = 0
	if 'log_file' in config_opts:
	    defaults['log'] = config_opts['log_file']
	if 'error_file' in config_opts:
	    defaults['err'] = config_opts['error_file']
	while count <= 5:
	    count += 1
	    if 'run'+str(count) in config_opts:
	   	defaults[config_opts['run'+str(count)]] = 'True'
    except NameError:
        no_config = True
		
	    
    # TODO there is still more to be done here

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
    if cwd.rsplit('/')[-1] != args.project_name and args.setup_project == False:
        sys.exit("ChemHTPS must be run from inside the project directory, or with the setup_project flag.")
    elif args.setup_project == True and args.project_name == None:
        sys.exit("Need to give the project_name flag to setup a project.")
    elif cwd[-len(args.project_name):] == args.project_name and no_config == True:
        sys.exit("There is no config file in the project directory.")

    os.environ["LD_LIBRARY_PATH"] = ":/projects/academic/hachmann/packages/Anaconda"
    main(args, sys.argv)   #numbering of sys.argv is only meaningful if it is launched as main

