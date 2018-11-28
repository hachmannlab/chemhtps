#!/usr/bin/env python

_MODULE_NAME = "job_generator"
_MODULE_VERSION = "v0.1.0"
_REVISION_DATE = "2015-06-24"
_AUTHORS = "Johannes Hachmann (hachmann@buffalo.edu) and William Evangelista (wevangel@buffalo.edu)"
_DESCRIPTION = "This module generates the computational chemistry jobs."

# Version history timeline:
# v0.1.0 (2015-06-24): basic implementation
# v0.1.1 (2016-02-25): changed so you can select a library

###################################################################################################
# TASKS OF THIS MODULE:
# -generate the computational chemistry jobs
# -prioritize the jobs pool
###################################################################################################

###################################################################################################
# TODO:
#
###################################################################################################

import sys
sys.path.insert(0, "/user/m27/pkg/openbabel/2.3.2/lib")
import pybel
import openbabel
import os
import shutil
import curses
import fnmatch

from misc import (chk_mkdir)
from template_generator import generate_template, runmenu, showresult
from misc import menu_input


###################################################################################################

def generate_jobs(project_name, config_opts):
    """
        This function generates the computational chemistry jobs.
    """
    logfile = open('job_gen.log', 'a', 0)
    error_file = open('job_gen.err', 'a', 0)

    cwd = os.getcwd()

    menu = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    curses.start_color()
    menu.keypad(1)

    libraries = ['Available libraries', 'Please choose a library: ']
    jtype = ['Available job types', 'Please choose a length for your jobs: ', 'short', 'long', 'priority']
    chtype = ['Available manual input for charge', 'Please choose a charge for your jobs: ', 'Charge: ']
    spintype = ['Available spin types', 'Please choose low-spin multiplicity or high-spin multiplicity for your jobs: ', 'low', 'high']
    programs = ['Supported Programs', 'Please choose a program', 'ORCA', 'QCHEM']
    templates = []
    files = []
    
    # dictionary of menus for navigation purposes

    menus = {0: libraries, 1: jtype, 2: chtype, 3: spintype, 4: programs, 5: templates}
    menu_names = {0: 'Library', 1: 'Job Type', 2: 'Charge Type', 3: 'Spin Type', 4: 'Program', 5: 'Template'}
    options = {0: '', 1: '', 2: '', 3: '', 4: '', 5: ''}
    menu_id = []  
    count = 0   
 
    # checking config file for options, if not using CUI for user to supply them
    for root, directories, filenames in os.walk(cwd + '/screeninglib'):
        for directory in directories:
            if filter(os.path.isdir, [os.path.join(root + '/' + directory, file) for file in
                                      os.listdir(os.path.join(root, directory))]):
                files.append(os.listdir(os.path.join(root, directory))[0:10])
                libraries.append(os.path.join(root, directory))
 
    if 'library_in' in config_opts:
	if config_opts['library_in'] not in menus[0][2:]:
	    options[0] = ''
	    menu_id.append(0)
	else:
	    options[0] = config_opts['library_in']
    else:
	options[0] = ''
	menu_id.append(0)


    if 'job_type' in config_opts:
	if config_opts['job_type'] not in menus[1][2:]:
	    options[1] = ''
	    menu_id.append(1)
	else:
	    options[1] = config_opts['job_type']
    else:
	options[1] = ''
	menu_id.append(1)


    if 'charge' in config_opts:
	if not config_opts['charge'].isdigit():
	    options[2] = ''
	    menu_id.append(2)
	else:
	    options[2] = config_opts['charge']
    else:
	options[2] = ''
	menu_id.append(2)


    if 'spin' in config_opts:
	if config_opts['spin'] not in menus[3][2:]:
	    options[3] = ''
	    menu_id.append(3)
	else:
	    options[3] = config_opts['spin']
    else:
	options[3] = ''
	menu_id.append(3)


    if 'program' in config_opts:
	if config_opts['program'] not in menus[4][2:]:
	    options[4] = ''
	    menu_id.append(4)
	else:
	    options[4] = config_opts['program']
            menus[5].extend(
                ('Available %s Templates' % options[0], 'Please choose a template'))
            for root, directories, filenames in os.walk(cwd + '/job_templates/%s' % options[4]):
                for filename in fnmatch.filter(filenames, '*.inp'):
                    menus[5].append(os.path.join(root, filename))
	    if not menu_id:
                menus[5].append('Exit Program')
	    else :
                menus[5].append('Previous Menu')
    else:
	options[4] = ''
	menu_id.append(4)


    if 'template' in config_opts:
	if config_opts['template'] not in menus[5][2:-1] :
	    options[5] = ''
	    menu_id.append(5)
	else:
	    options[5] = config_opts['template']
    else:
	options[5] = ''
	menu_id.append(5)

    error_code = 0
    
    if len(menu_id) > 0:
        for j in range(len(menu_id)):
	    if menu_id[j] == 5:
		break
	    if j == 0:
                menus[menu_id[j]].append('Exit Program')
	    else :
                menus[menu_id[j]].append('Previous Menu')

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
        elif i == 2 and pos == menus[i].index('Charge: '):
            options[2] = menu_input(menu, pos, len(menus[2][pos]))
	    j += 1
	elif i == 4 and pos != menus[i].index('Previous Menu'):
            menus[5] = []
	    menus[5].extend(
                ('Available %s Templates' % options[0], 'Please choose a template'))
            for root, directories, filenames in os.walk(cwd + '/job_templates/%s' % options[4]):
                for filename in fnmatch.filter(filenames, '*.inp'):
                    menus[5].append(os.path.join(root, filename))
	    menus[5].append('Previous Menu')
	    j += 1	
        else:
            j += 1
    
    library = options[0]
    library_name = library.rsplit('/')[-1]
    job_type = options[1] + '/'
    charge = options[2]
    spin = options[3]
    prog = options[4]

    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)
    menu.keypad(0)
    curses.endwin()
    
    if error_code == 1:
	error_file.close()
	logfile.close()
	sys.exit('termination by user')

    # making necessary additions to config file
    new_lines = []
    new_lines.append('library_in = '+options[0]+'\n')
    new_lines.append('job_type = '+options[1]+'\n')
    new_lines.append('charge = '+options[2]+'\n')
    new_lines.append('spin = '+options[3]+'\n')
    new_lines.append('program = '+options[4]+'\n')
    new_lines.append('template = '+options[5]+'\n\n')

    config_lines = []
    new_config_lines = []
    r_switch = 1
    insert_idx = 20
    with open(project_name + '.config', 'r') as config_file:
        config_lines = config_file.readlines()

 
    logfile.writelines(config_lines)

    tmp_str = "---------------------------------------------------------------------\n"
    logfile.write(tmp_str)

    tmp_str = "After operation of job_generator, the new config file looks like:\n"
    logfile.write(tmp_str)
    
    for i,line in enumerate(config_lines):
	if r_switch == 1:
	    new_config_lines.append(line) 
	if r_switch == 0:
	    if '@' in line or 'feedjobs' in line:
            	r_switch = 1
        	new_config_lines.append(line)
	if line == '@generatejobs\n':
	    insert_idx = i+1
	    r_switch = 0

    new_config_lines[insert_idx:insert_idx] = new_lines

    with open(project_name + '.config','w') as newconfig_file:
        newconfig_file.writelines(new_config_lines)

    logfile.writelines(new_config_lines)
    tmp_str = "---------------------------------------------------------------------\n"
    logfile.write(tmp_str)

    if library != 'Exit Program':
        lib = os.listdir(library)
    else:
        sys.exit(0)

    # Not sure this is the best way to get the template should maybe ask which template to use
    #template = generate_template()
    template = options[5]
    with open(template, 'r', 0) as jt:
        job_template = jt.readlines()
    job_template = tuple(job_template)
    for folder in lib:
        if '.dat' in folder or '.smi' in folder:
            pass
        else:
            folder_dir = cwd + '/jobpool/' + job_type + prog + '_'  + library_name + '_' + folder
            chk_mkdir(folder_dir)
            for geo in os.listdir(library + '/' + folder):
                temp = list(job_template)
                job_file = library + '/' + folder + '/' + geo
                job_dir = folder_dir + '/' + geo.split('.')[0]
                chk_mkdir(job_dir)
                shutil.copy(job_file, job_dir + '/' + geo)
		mol_try = pybel.readfile("xyz",job_dir+'/'+geo.split('.')[0]+'.xyz').next()
		xyz_charge = mol_try.OBMol.GetTotalCharge()+int(charge)
		xyz_spin = mol_try.OBMol.GetTotalSpinMultiplicity() 
                change = (int(charge))%2
		base_name = ''
		if spin == 'low':
		    xyz_spin = xyz_spin - pow(-change,xyz_spin)	
		elif spin == 'high':
		    xyz_spin = xyz_spin + 2 - pow(-change,xyz_spin)	
		#temp.append('* xyzfile 0 1 ' + geo + '\n')
		if prog == 'ORCA':
		    xyz_flag = 0
		    for i,line in enumerate(temp):
		        if line == 'xyzlinehere\n':
		            temp[i] = '* xyzfile ' + str(xyz_charge) + ' ' + str(xyz_spin) + ' ' + geo + '\n'    
		            xyz_flag = 1
			elif line == 'xyzline2here\n':
		    	    temp[i] = '* xyzfile ' + str(xyz_charge) + ' ' + str(xyz_spin) + '\n'  
			    xyz_flag = 1
		    if xyz_flag == 0:
			tmp_str = '* xyzfile ' + str(xyz_charge) + ' ' + str(xyz_spin) + ' ' + geo + '\n'
			temp.append(tmp_str)
		elif prog == 'QCHEM':
		    coords = []
    		    with open(job_dir + '/' + geo, 'r', 1) as qc_xyz:
                    	coords = list(qc_xyz.readlines())
		    first_line = str(xyz_charge) + ' ' + str(xyz_spin) + '\n'
		    mol_section = []
	            mol_section.append(first_line)
		    mol_section.extend(coords[2:])
		    length = int(coords[0][:-1])
		    count = 0
		    for i,line in enumerate(temp):
		        if count > 0 and count <= length:
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

    error_file.close()
    logfile.close()
    return 0

def prioritize_pool():
    """
        This function prioritizes the jobs pool.
    """

# TODO: write this function creating all the stuff in the dummy_project, including the config file containing the project name
