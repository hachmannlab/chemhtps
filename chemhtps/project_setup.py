#!/usr/bin/env python

_MODULE_NAME = "project_setup"
_MODULE_VERSION = "v0.1.0"
_REVISION_DATE = "2019-01-10"
_AUTHORS = "Johannes Hachmann (hachmann@buffalo.edu), William Evangelista (wevangel@buffalo.edu) and Yudhajit Pal(yudhajit@buffalo.edu"
_DESCRIPTION = "This module sets up the project, including the file and directory structure."

import os
import fnmatch

###################################################################################################

def setup_project(project_name):
    """
        This function sets up the project, including the file and directory structure.
    """
    dir_list = ['/archive', '/db', '/jobpool/short', '/jobpool/long', '/lost+found', '/screeninglib']
    cwd = os.getcwd()  # just in case we need this
    user = os.getlogin()

    for dirs in dir_list:
        os.makedirs(project_name + dirs)

    # Copy template files into the project directory
    current_path = os.path.realpath(__file__).rsplit('/', 2)[0]    # this takes the folder path and divides it by the last /, so the first part is the whole thing minus the current chemhtps folder path
    job_templates = current_path + '/chemhtps/metadata/job_templates'
    tmp_str = 'cp -r ' + job_templates + ' ' + cwd + '/' + project_name + '/'
    os.system(tmp_str)
    #building_blocks = current_path + '/chemlg/chemlg/templates/building_blocks.dat'
    #gener_rules = current_path + '/chemlg/chemlg/templates/config.dat'
    #tmp_str = 'cp ' + building_blocks + ' ' + gener_rules + ' ' + cwd + '/' + project_name + '/screeninglib'
    #os.system(tmp_str)
    for root, directories, filenames in os.walk(cwd + '/' + project_name + '/job_templates'):
        for filename in fnmatch.filter(filenames, '*.sh'):
            current_name = os.path.join(root, filename)
            tmp = project_name + '_' +  filename  # prepend project name to slurm scripts
            new_name = os.path.join(root, tmp)
            tmp = 'mv ' + current_name + ' ' + new_name
            os.system(tmp)

    # creates a new config file for the project with blank/default values for the config options
    with open(project_name + '/' + project_name + '.config', 'w') as config:
        config.write('project_name = ' + project_name + '\n')
        config.write('user_name = ' + user + '\n')
        config.write('log_file = ' + project_name + '.log' + '\n')
        config.write('error_file = ' + project_name + '.err' + '\n\n')
        config.write('generatelib' + '\n')
        config.write('generation_file = none' + '\n')
        config.write('building_block = none' + '\n')
        config.write('cores = 0' + '\n')
        config.write('clusters = none' + '\n\n')
        config.write('generatejobs' + '\n')
        config.write('library_in = none' + '\n')
        config.write('job_type = none' + '\n')
        config.write('program = none' + '\n')
        config.write('template = none' + '\n\n')
        config.write('feedjobs' + '\n')
        config.write('feed_local = TRUE' + '\n')
        config.write('job_sched = SLURM' + '\n\n')
        config.write('postprocess' + '\n\n')
        config.write('populatedb' + '\n\n')

    # creates a new queue_list file for the project with blank/default values for the maximum loads on the various queues
    with open(project_name + '/queue_list.dat', 'w') as queue_list:
        lines = ['#cluster partition limit type\n', 'ub-hpc general-compute 0 long\n', 'ub-hpc debug 3 short\n',
                 'ub-hpc gpu 0 long\n', 'ub-hpc largemem 0 long\n', 'faculty beta 0 long\n']
        queue_list.writelines(lines)
        queue_list.close()
