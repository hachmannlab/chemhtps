#!/usr/bin/env python

_MODULE_NAME = "feeder_options"
_MODULE_VERSION = "v0.0.1"
_REVISION_DATE = "2015-06-24"
_AUTHORS = "Johannes Hachmann (hachmann@buffalo.edu) and Mohammad Atif Faiz Afzal (m27@buffalo.edu)"
_DESCRIPTION = "This module takes in the options for the job_feeder module."

# Version history timeline:
# v0.0.1 (2015-06-24): basic implementation
# v0.1.0 (2016-02-24): fixed menu to use curses

###################################################################################################
# TASKS OF THIS MODULE:
# -generate screening libraries
###################################################################################################

###################################################################################################
# TODO:
# 
###################################################################################################

import os
import sys
import math
import curses
import fnmatch
from template_generator import runmenu, showresult
from misc import menu_input

def feed_options(project_name,config_opts):
    """
        This function generates the guess geometries for a screening library.
    """
    logfile = open('feed_opts.log', 'a', 0)
    error_file = open('feed_opts.err', 'a', 0)
    cwd = os.getcwd()

    menu = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    curses.start_color()
    menu.keypad(1)

    # Menu for the library generator options
    local = ['Execution of job feeder', 'Please enter the options for local execution: ', 'TRUE', 'FALSE']
    job_sched = ['Job Scheduler', 'Please enter the name of the job scheduler: ', 'SLURM']
    # dictionary of menus for navigation purposes
    
    menus = {0: local, 1: job_sched}
    menu_names = {0: 'local_opt', 1: 'job_scheduler'}
    options = {0: '', 1: ''}
    menu_id = []  
 
    # checking config file for options, if not using CUI for user to supply them
    error_code = 0
 
    if 'feed_local' in config_opts:
	if config_opts['feed_local'] not in menus[0][2:]:
	    options[0] = ''
	    menu_id.append(0)
	else:
	    options[0] = config_opts['feed_local']
    else:
	options[0] = ''
	menu_id.append(0)


    if 'job_sched' in config_opts:
	if config_opts['job_sched'] not in menus[1][2:]:
	    options[1] = ''
	    menu_id.append(1)
	else:
	    options[1] = config_opts['job_sched']
    else:
	options[1] = ''
	menu_id.append(1)

    if len(menu_id) > 0:
        for j in range(len(menu_id)):
            if j == 0:
                menus[menu_id[j]].append('Exit Program')
            else :
                menus[menu_id[j]].append('Previous Menu')

    # running the menus 

    i = 0
    j = 0 
    while j <= len(menu_id):
        if j == len(menu_id):
            pos = showresult(menu, menu_names, options)
            if pos == 1:
                j = 0
		if len(menu_id) == 0:
                    error_file.write("job generator terminated by user\n")
                    error_file.write("no creation of job folders or changes recorded to " + project_name + ".config\n")
                    error_code = 1 #end program
                    break
            else:
                break
	i = menu_id[j]
        pos = runmenu(menu, menus[i])
        options[i] = menus[i][pos]
        if j == 0 and pos == menus[i].index('Exit Program'):
            error_file.write("job generator terminated by user\n")
            error_file.write("no creation of job folders or changes recorded to " + project_name + ".config\n")
            error_code = 1 #end program
            break
        elif j != 0 and pos == menus[i].index('Previous Menu'):
            j += -1
        else:
            j += 1

    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)
    menu.keypad(0)
    curses.endwin()

    if error_code == 1:
        logfile.close()
	error_file.close()
	sys.exit('termination by user')

    # making necessary additions to config file
    new_lines = []
    new_lines.append('feed_local = '+options[0]+'\n')
    new_lines.append('job_sched = '+options[1]+'\n\n')

    config_lines = []
    new_config_lines = []
    r_switch = 1
    insert_idx = 20
    with open(project_name + '.config', 'r') as config_file:
        config_lines = config_file.readlines()
    
    logfile.writelines(config_lines)

    tmp_str = "---------------------------------------------------------------------\n"
    logfile.write(tmp_str)

    tmp_str = "After operation of feed_options, the new config file looks like:\n"
    logfile.write(tmp_str)
    
    for i,line in enumerate(config_lines):
	if r_switch == 1:
	    new_config_lines.append(line) 
        if r_switch == 0:
            if '@' in line or 'postprocess' in line:
                r_switch = 1
                new_config_lines.append(line)
        if line == '@feedjobs\n':
            insert_idx = i+1
            r_switch = 0	


    new_config_lines[insert_idx:insert_idx] = new_lines

    with open(project_name + '.config','w') as newconfig_file:
        newconfig_file.writelines(new_config_lines)

    logfile.writelines(new_config_lines)
    tmp_str = "---------------------------------------------------------------------\n"
    logfile.write(tmp_str)
    logfile.close()
    error_file.close()
    return 0 
