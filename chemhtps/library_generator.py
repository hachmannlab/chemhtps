#!/usr/bin/env python

_MODULE_NAME = "library_generator"
_MODULE_VERSION = "v0.1.0"
_REVISION_DATE = "2019-01-10"
_AUTHORS = "Johannes Hachmann (hachmann@buffalo.edu), Mohammad Atif Faiz Afzal (m27@buffalo.edu) and Yudhajit Pal (yudhajit@buffalo.edu)"
_DESCRIPTION = "This module generates the high-throughput screening libraries."

import os
import os.path
import sys
import time
import math
import curses
import fnmatch

from misc import (banner,
                  tot_exec_time_str,
                  std_datetime_str,
                  chk_rmfile,
                  chk_mkdir)


def generate_structurelib():
    """
        This function generates a screening library of structures (SMILES).
    """


def generate_geometries(project_name,config_opts):
    """
        This function generates the guess geometries for a screening library.
    """
    logfile = open('lib_gen.log', 'a')
    error_file = open('lib_gen.err', 'w')
    cwd = os.getcwd()
    time_start = time.time()

    banner_list = banner(_MODULE_NAME, _MODULE_VERSION, _REVISION_DATE, _AUTHORS,'', _DESCRIPTION)
    for line in banner_list:
        print (line)
        logfile.write(line + '\n')

    ## Menu for the library generator options
    inp = []
    rule = []
    cluster = ['general-compute', 'beta', 'run locally']

    ## dictionary of menus for checking all available options
    menus = {0: inp, 1: rule, 2: cluster}
    options = {0: '', 1: '', 2: '', 3: ''}
    error_codes = [] 

    # Build out the inp and rule menu lists
    for root, directories, filenames in os.walk(cwd + '/screeninglib'):
        for filename in fnmatch.filter(filenames, '*building*'):
            menus[0].insert(0,os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, '*smiles.csv*'):
            menus[0].insert(0,os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, '*config*'):
            menus[1].insert(0,os.path.join(root, filename))
   
    #logfile.write(','.join(menus[0])+'\n')
    #logfile.write(','.join(menus[1])+'\n')
    #logfile.write(config_opts['building_block']+'\n')
    #logfile.write(str(os.path.isfile(config_opts['building_block']))+'\n')
    #logfile.write(config_opts['generation_file']+'\n')
    #logfile.write(str(os.path.isfile(config_opts['generation_file']))+'\n')

    # checking config file for options, if inappropriate option, then returning an error code
    if 'building_block' in config_opts:
        if config_opts['building_block'] == '' or config_opts['building_block'] == 'none':
            error_codes.append(0) 
        elif config_opts['building_block'] not in menus[0]:
            if os.path.isfile(config_opts['building_block']):   
                options[0] = config_opts['building_block']
            else:
                error_codes.append(0) 
        else:
            options[0] = config_opts['building_block']
    else:
        error_codes.append(0) 

    

    if 'generation_file' in config_opts:
        if config_opts['generation_file'] == '' or config_opts['generation_file'] == 'none':
            error_codes.append(1) 
        elif config_opts['generation_file'] not in menus[1]:
            if os.path.isfile(config_opts['generation_file']):   
                options[1] = config_opts['generation_file']
            else:
                error_codes.append(1) 
        else :
            options[1] = config_opts['generation_file']
    else:
        error_codes.append(1) 



    if 'cores' in config_opts:
        if not config_opts['cores'].isdigit() or config_opts['cores'] == '0':
            error_codes.append(2) 
        else:
            options[2] = config_opts['cores']
    else:
        error_codes.append(2) 


    if 'clusters' in config_opts:
        if config_opts['clusters'] not in menus[2]:
            error_codes.append(3)
        else:
            options[3] = config_opts['clusters']
    else:
        error_codes.append(3)


    # checking for the error_codes and reporting the corresponding error in the error_file
    if 0 in error_codes:
        error_file.write('building block file not found\n')
    if 1 in error_codes:
        error_file.write('rule file not found\n')
    if 2 in error_codes:
        error_file.write('cores not specified\n')
    if 3 in error_codes:
        error_file.write('invalid cluster specified\n')

    if error_codes:
        logfile.write('Error Termination \n')
        print ('Error Termination')
        logfile.close()
        error_file.close()
        temp_str = 'echo \"' + std_datetime_str() + '\n\" >> ' + project_name+'.err'
        os.system(temp_str)
        temp_str = 'echo \"Error from --generatelib execution: \n\" >> ' + project_name+'.err'
        os.system(temp_str)
        temp_str = 'cat lib_gen.err >> ' + project_name+'.err'
        os.system(temp_str)
        temp_str = 'echo \"---------------------------------------------------------------------\n\" >> ' + project_name + '.err'
        os.system(temp_str)
        temp_str = 'echo \"\n\n\n\" >> ' + project_name+'.err'
        os.system(temp_str)
        sys.exit()

    # section to record the module config options in the module log file
    config_lines = []
    lib_gen_lines = []
    r_switch = 0
    logfile.write('config-file with options for library generation:\n')
    with open(project_name + '.config', 'r') as config_file:
        config_lines = config_file.readlines()
    
    for line in config_lines:
        if line == '\n' or line == 'generatejobs': r_switch = 0
        if r_switch == 1: lib_gen_lines.append(line)
        if 'generatelib' in line: r_switch = 1

    logfile.writelines(lib_gen_lines)
    for lines in lib_gen_lines:
        print(lines[:-1])
    tmp_str = "---------------------------------------------------------------------\n"
    logfile.write(tmp_str)
    ops = '-i ' + options[1] + ' -b ' + options[0] + ' -o ./screeninglib/'
    logfile.write(ops+'\n')
    libgen_path = 'chemlgshell '
    tmp_str = libgen_path + ops + ' \n'
    if options[3] == 'run locally':
        os.system(tmp_str)
        logfile.write(tmp_str+'\n')
    else:
        cores = int(options[2])
        nodes = 0
        tmp_str = 'srun -n ' + options[2] + ' --mpi=pmi2 ' + tmp_str
        slurm_name = 'job_templates/' + project_name + '_generatelib.sh' 
        cluster_info = []
        if options[3] == 'beta':
            nodes = int(math.ceil(cores/16.0))
            info = ['#SBATCH --clusters=chemistry\n', '#SBATCH --partition=beta --qos=beta\n', '#SBATCH --account=hachmann\n']
            cluster_info.extend(info)
        elif options[3] == 'general-compute':
            nodes = int(math.ceil(cores/8.0))
            info = ['#SBATCH --clusters=ub-hpc\n', '#SBATCH --partition=general-compute --qos=general-compute\n']
            cluster_info.extend(info)
        with open(slurm_name, 'r') as slurm_file:
            lines = slurm_file.readlines()
            lines[1:1] = cluster_info
        for i,line in enumerate(lines):
            if line == 'Timehere\n':
                lines[i] = '#SBATCH --time=02:00:00\n'
            elif line == 'Nodeshere\n':
                lines[i] = '#SBATCH --nodes=' + str(nodes) + '\n'
            elif line == 'Cpushere\n':
                lines[i] = '#SBATCH --tasks-per-node='+options[2]+'\n'
            elif line == 'Runlinehere\n':
                lines[i] = tmp_str+'\n'
                logfile.write(tmp_str +'\n')
        with open('libtmp.sh','w') as slurm_file:
            slurm_file.writelines(lines)
        submit = "sbatch libtmp.sh"
        #LD = "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/user/m27/pkg/openbabel/2.3.2/lib"
        os.system(submit)
        os.remove("libtmp.sh")
    # end of run section
    tmp_str = "---------------------------------------------------------------------"
    print (tmp_str)
    logfile.write(tmp_str + '\n')

    print ("library_generator module completed....")
    tmp_str = tot_exec_time_str(time_start) + '\n' + std_datetime_str()
    print (tmp_str + '\n')
    logfile.write(tmp_str + '\n\n')
    tmp_str = "------------------------------------------------------------------------------ "
    print (tmp_str)
    logfile.write(tmp_str + '\n')
    error_file.close()
    logfile.close()
    return 0

    # Check whether error files contain anything
    chk_rmfile(error_file)
    return 0
