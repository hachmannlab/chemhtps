#!/usr/bin/env python

_MODULE_NAME = "job_generator"
_MODULE_VERSION = "v0.1.0"
_REVISION_DATE = "2019-01-10"
_AUTHORS = "Johannes Hachmann (hachmann@buffalo.edu), William Evangelista (wevangel@buffalo.edu) and Yudhajit Pal(yudhajit@buffalo.edu)"
_DESCRIPTION = "This module generates the computational chemistry jobs."

import sys
import pybel
import openbabel
import os
import time
import shutil
import curses
import fnmatch

from misc import (banner,
                  tot_exec_time_str,
                  std_datetime_str,
                  chk_rmfile,
                  chk_mkdir)


###################################################################################################

def generate_jobs(project_name, config_opts):
    """
        This function generates the computational chemistry jobs.
    """
    logfile = open('job_gen.log', 'a')
    error_file = open('job_gen.err', 'w')
    cwd = os.getcwd()
    time_start = time.time()
   
    banner_list = banner(_MODULE_NAME, _MODULE_VERSION, _REVISION_DATE, _AUTHORS, '',_DESCRIPTION)
    for line in banner_list:
        print (line)
        logfile.write(line + '\n')

    jg_no = 0
    if os.path.isfile('job_gen.log') :
        with  open('job_gen.log','r') as log_read:
            for line in log_read:
                if 'configfile with options' in line:
                    jg_no = int(line[:-1].rsplit('.')[-1])    

    jg_no += 1

    libraries = []
    jtype = ['short', 'long', 'priority']
    programs = ['ORCA', 'QCHEM']
    templates = []
    files = []
    
    # dictionary of menus for checking options
    menus = {0: libraries, 1: jtype, 2: programs, 3: templates}
    options = {0: '', 1: '', 2: '', 3: ''}
    error_codes = []   
 
    # checking config file for options
    # adding available libraries into a list to do a check before job creation
    for root, directories, filenames in os.walk(cwd + '/screeninglib'):
        for directory in directories:
            if filter(os.path.isdir, [os.path.join(root + '/' + directory, file) for file in
                                      os.listdir(os.path.join(root, directory))]):
                files.append(os.listdir(os.path.join(root, directory))[0:10])
                libraries.append(os.path.join(root, directory))
 
    #logfile.write((',').join(menus[0])+'\n')
    
    if 'library_in' in config_opts:
        if cwd not in config_opts['library_in']:
            if './screeninglib' not in config_opts['library_in']: 
                config_opts['library_in'] = cwd + '/screeninglib/' + config_opts['library_in']
            else:
                config_opts['library_in'] = cwd + '/' + config_opts['library_in']
        #logfile.write(config_opts['library_in']+'\n')

        if (fnmatch.fnmatch(config_opts['library_in'],x) for x in menus[0]):
            options[0] = config_opts['library_in']
        else:
            error_codes.append(0)
    else:
        error_codes.append(0)


    if 'job_type' in config_opts:
        if config_opts['job_type'] not in menus[1]:
            error_codes.append(1)
        else:
            options[1] = config_opts['job_type']
    else:
        error_codes.append(1)


    if 'program' in config_opts:
        if config_opts['program'] not in menus[2]:
            error_codes.append(2)
        else:
            options[2] = config_opts['program']
            for root, directories, filenames in os.walk(cwd + '/job_templates/%s' % options[2]):
                for filename in fnmatch.filter(filenames, '*.inp'):
                    menus[3].append(os.path.join(root, filename))
    else:
        error_codes.append(2)

    if 'template' in config_opts:
        if cwd not in config_opts['template']:
            if './job_templates/'+options[2] not in config_opts['template']: 
                config_opts['template'] = cwd + '/job_templates/' + options[2] + '/' + config_opts['template']
            else:
                config_opts['template'] = cwd + '/' + config_opts['template']
        #logfile.write(config_opts['template']+'\n')
        if not os.path.isfile(config_opts['template']): error_codes.append(3)
        elif (fnmatch.fnmatch(config_opts['template'],x) for x in menus[3]):
            options[3] = config_opts['template']
        else:
            error_codes.append(3)
    else:
        error_codes.append(3)

    library = options[0]
    library_name = library.rsplit('/')[-1]
    job_type = options[1] + '/'
    prog = options[2]
    template = options[3]

    # checking for the error_codes and reporting the corresponding error in the error_file
    if 0 in error_codes:
        error_file.write('library not found\n')
    if 1 in error_codes:
        error_file.write('invalid job_type specified\n')
    if 2 in error_codes:
        error_file.write('invalid program specified\n')
    if 3 in error_codes:
        error_file.write('invalid template_file specified\n')

    if error_codes:
        logfile.write('Error Termination \n')
        print ('Error Termination') 
        logfile.close()
        error_file.close()
        sys.exit()

    # creating a record of the parameters chosen for the current round of job creation in the log_file
    config_lines = []
    job_gen_lines = []
    r_switch = 0
    logfile.write('configfile with options for job generation with id.no. '+ str(jg_no)  +':\n')
    with open(project_name + '.config', 'r') as config_file:
        config_lines = config_file.readlines()
    
    for line in config_lines:
        if line == '\n' or line == 'feedjobs': r_switch = 0
        if r_switch == 1: job_gen_lines.append(line)
        if 'generatejobs' in line: r_switch = 1

    logfile.writelines(job_gen_lines)
    for line in job_gen_lines:
        print (line[:-1])

    tmp_str = "---------------------------------------------------------------------\n"
    logfile.write(tmp_str)

    
    lib = os.listdir(library)

    # creating all the input .inp files and putting them in a job-folder along with the .xyz files
    # separate input file formats are considered for Q-chem and ORCA jobs
    with open(template, 'r') as jt:
        job_template = jt.readlines()
    job_template = tuple(job_template)
    for folder in lib:
        if '.dat' in folder or '.smi' in folder:
            pass
        else:
            folder_dir = cwd + '/jobpool/' + job_type + 'jg' + str(jg_no)  + '_'  + prog + '_'  + library_name + '_' + folder
            chk_mkdir(folder_dir)
            for geo in os.listdir(library + '/' + folder):
                temp = list(job_template)
                job_file = library + '/' + folder + '/' + geo
                job_dir = folder_dir + '/' + geo.split('.')[0]
                chk_mkdir(job_dir)
                shutil.copy(job_file, job_dir + '/' + geo)
                if prog == 'ORCA':
                    xyz_flag = 0
                    for i,line in enumerate(temp):
                        if 'xyzfile' in line:
                            temp[i] = line[:-1] + ' ' + geo + '\n'    
                            xyz_flag = 1
                    if xyz_flag == 0:
                        tmp_str = '* xyzfile 0 1 ' + geo + '\n'
                        temp.append(tmp_str)
                elif prog == 'QCHEM':
                    coords = []
                    with open(job_dir + '/' + geo, 'r', 1) as qc_xyz:
                        coords = list(qc_xyz.readlines())
                    mol_section = []
                    mol_section.extend(coords[2:])
                    length = int(coords[0][:-1])
                    count = 0
                    for i,line in enumerate(temp):
                        if count > 0 and count < length:
                            temp.insert(i,mol_section[count])
                            count += 1
                        if line == 'xyzlinehere\n':
                            temp[i] = mol_section[0]
                            count += 1    
                        elif count == 0 and i == len(temp) - 1:
                            temp.append('\n')
                            temp[i+1:i+1] =  mol_section
                with open(job_dir + '/' + geo.split('.')[0] + '.inp', 'w') as tmp:
                    tmp.writelines(temp)

    # end of run section
    tmp_str = "------------------------------------------------------------------------------ "
    print (tmp_str)
    logfile.write(tmp_str + '\n')

    print ("job_generator module completed....")
    tmp_str = tot_exec_time_str(time_start) + '\n' + std_datetime_str()
    print (tmp_str + '\n\n\n')
    logfile.write(tmp_str + '\n\n\n')
    error_file.close()
    logfile.close()
    return 0

    # Check whether error files contain anything
    chk_rmfile(error_file)

def prioritize_pool():
    """
        This function prioritizes the jobs pool.
    """

