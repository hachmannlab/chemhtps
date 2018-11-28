#!/usr/bin/env python

_MODULE_NAME = "library_generator"
_MODULE_VERSION = "v0.0.1"
_REVISION_DATE = "2015-06-24"
_AUTHORS = "Johannes Hachmann (hachmann@buffalo.edu) and Mohammad Atif Faiz Afzal (m27@buffalo.edu)"
_DESCRIPTION = "This module generates the high-throughput screening libraries."

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
import os.path
import sys
import math
import curses
import fnmatch
from template_generator import runmenu, showresult
from misc import menu_input


def generate_structurelib():
    """
        This function generates a screening library of structures (SMILES).
    """


def generate_geometries(project_name,config_opts):
    """
        This function generates the guess geometries for a screening library.
    """
    logfile = open('lib_gen.log', 'a', 0)
    error_file = open('lib_gen.err', 'a', 0)


    cwd = os.getcwd()

    menu = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    curses.start_color()
    menu.keypad(1)

    # Menu for the library generator options
    inp = ['Building Block File', 'Please enter the name of the building block file: ', 'Manual input']
    rule = ['Generator Rules File', 'Please enter the name of the rule file: ', 'Manual input']
    moltyp = ['Molecule Type', 'Please enter the input molecule type: ', 'smiles', 'inchi']
    combi = ['Combination Type', 'Please enter the combination type for the library: ', 'link', 'fusion']
    gens = ['Generation Level', 'Please enter the number of generations (Keep this as 0 if converting an smi/inchi library to xyz): ', 'Generation: ']
    outtyp = ['Output Type', 'Please enter the output format', 'smi', 'xyz']
    lib_name = ['Library Name', 'Press Enter: ', 'Press here to enter a name']
    cores = ['Number of cores', 'Please enter number of cores: ', 'Cores: ']#Leave cores and cluster menu last
    cluster = ['Cluster', 'Please choose which cluster to run on: ', 'general-compute', 'beta', 'run locally']

    # dictionary of menus for navigation purposes
    
    menus = {0: inp, 1: rule, 2: moltyp, 3: combi, 4: gens, 5: outtyp, 6: lib_name, 7: cores, 8: cluster}
    menu_names = {0: 'input_file', 1: 'rule_file', 2: 'molecule_type', 3: 'combination_type', 
            4: 'generation_levels', 5: 'output_type', 6: 'lib_name', 7: 'cores', 8: 'cluster'}
    options = {0: '', 1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: ''}
    menu_id = []  
 
    if 'generate new library' not in config_opts:
	if 'use existing library' in config_opts:
	    if config_opts['use existing library'] == 'TRUE':
	        config_opts['generate new library'] = 'FALSE'
	    elif config_opts['use existing library'] == 'FALSE':
	        config_opts['generate new library'] = 'TRUE'
	        error_file.write('Warning ! generate new library option not specified whereas existing library was kept at FALSE\n')
	        error_file.write('Default: generate new library = TRUE\n')			
	else:   
	    config_opts['generate new library'] = 'TRUE'
	    config_opts['use existing library'] = 'FALSE'
	    error_file.write('Warning ! new library or existing library not specified\n')
	    error_file.write('Default: generate new library = TRUE\n')		
    elif config_opts['generate new library'] != 'TRUE' and config_opts['generate new library'] != 'FALSE':
	if config_opts['use existing library'] == 'TRUE':
	    config_opts['generate new library'] = 'FALSE'	
	elif config_opts['use existing library'] == 'FALSE':
	    config_opts['generate new library'] = 'TRUE'			
	else:
	    config_opts['generate new library'] = 'TRUE'
	    config_opts['use existing library'] = 'FALSE'
	    error_file.write('Warning ! new library not specified at TRUE or FALSE\n')
	    error_file.write('Default: generate new library = TRUE\n')		
    elif config_opts['generate new library'] == 'TRUE':
	config_opts['use existing library'] = 'FALSE'
    elif config_opts['generate new library'] == 'FALSE':
        config_opts['use existing library'] = 'TRUE'   
	
   
    # running the menus 

    # Build out the inp and rule menu lists
    for root, directories, filenames in os.walk(cwd + '/screeninglib'):
        if config_opts['generate new library'] == 'TRUE':
	    for filename in fnmatch.filter(filenames, '*building*'):
            	menus[0].insert(2,os.path.join(root, filename))
        elif config_opts['use existing library'] == 'TRUE':
            for filename in fnmatch.filter(filenames, '*.smi*'):
            	menus[0].insert(2,os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, '*rules*'):
            menus[1].insert(2,os.path.join(root, filename))
    
    # checking config file for options, if not using CUI for user to supply them
    error_code = 0
    if 'building_block' in config_opts:
	if config_opts['building_block'] == '' or config_opts['building_block'] == 'none':
	    options[0] = ''
	    menu_id.append(0)
	elif config_opts['building_block'] not in menus[0][2:-1]:
	    if os.path.isfile(config_opts['building_block']):   
		options[0] = config_opts['building_block']
	    else : 
		error_file.write('ERROR: building block does not exist\n')
		#print 'ERROR: building block does not exist'
		#print "no creation of library or changes recorded to " + project_name + ".config"
	    	error_file.write("no creation of library or changes recorded to " + project_name + ".config\n")
            	error_code = 1 #end program
	else :
	    options[0] = config_opts['building_block']
    else:
	options[0] = ''
	menu_id.append(0)


    if 'generation_file' in config_opts:
	if config_opts['generation_file'] == '' or config_opts['generation_file'] == 'none':
	    options[1] = ''
	    menu_id.append(1)
	elif config_opts['generation_file'] not in menus[1][2:-1]:
	    if os.path.isfile(config_opts['generation_file']):   
		options[1] = config_opts['generation_file']
	    else : 
		error_file.write('ERROR: rules file does not exist\n')
	    	error_file.write("no creation of library or changes recorded to " + project_name + ".config\n")
		#print 'ERROR: rules file does not exist'
		#print "no creation of library or changes recorded to " + project_name + ".config"
            	error_code = 2 #end program
	else :
	    options[1] = config_opts['generation_file']
    else:
	options[1] = ''
	menu_id.append(1)


    if 'input_type' in config_opts:
	if config_opts['input_type'] not in menus[2][2:]:
	    options[2] = ''
	    menu_id.append(2)
	else:
	    options[2] = config_opts['input_type']
    else:
	options[2] = ''
	menu_id.append(2)


    if 'combination' in config_opts:
	if config_opts['combination'] not in menus[3][2:]:
	    options[3] = ''
	    menu_id.append(3)
	else:
	    options[3] = config_opts['combination']
    else:
	options[3] = ''
	menu_id.append(3)


    if 'generations' in config_opts and config_opts['generate new library'] == 'TRUE':
	if config_opts['generations'] == '0' or config_opts['generations'] == '' or not config_opts['generations'].isdigit() :
	    options[4] = ''
	    menu_id.append(4)
	else:
	    options[4] = config_opts['generations']
    elif config_opts['use existing library'] == 'TRUE' and config_opts['generate new library'] == 'FALSE':
	options[4] = 0
    else:
	options[4] = ''
	menu_id.append(4)


    if 'out_type' in config_opts:
	if config_opts['out_type'] not in menus[5][2:]:
	    options[5] = ''
	    menu_id.append(5)
	else:
	    options[5] = config_opts['out_type']
    else:
	options[5] = ''
	menu_id.append(5)


    if 'library_out' in config_opts:
	if config_opts['library_out'] == 'none' or config_opts['library_out'] == '':
	    options[6] = ''
	    menu_id.append(6)
	else:
	    options[6] = config_opts['library_out']
    else:
	options[6] = ''
	menu_id.append(6)


    if 'cores' in config_opts:
	if not config_opts['cores'].isdigit() or config_opts['cores'] == '0':
	    options[7] = ''
	    menu_id.append(7)
	else:
	    options[7] = config_opts['cores']
    else:
	options[7] = ''
	menu_id.append(7)


    if 'clusters' in config_opts:
	if config_opts['clusters'] not in menus[8][2:]:
	    options[8] = ''
	    menu_id.append(8)
	else:
	    options[8] = config_opts['clusters']
    else:
	options[8] = ''
	menu_id.append(8)
   


    if len(menu_id) > 0:
	for j in range(len(menu_id)):
    	    if j == 0:	
		menus[menu_id[j]].append('Exit Program')
	    else:
		menus[menu_id[j]].append('Previous Menu')
			

    i = 0
    j = 0 
    while j <= len(menu_id):
        if j == len(menu_id):
            pos = showresult(menu, menu_names, options)
            if pos == 1:
                j = 0
		if len(menu_id) == 0:
	    	    error_file.write("library_generator terminated by user\n")
	    	    error_file.write("no creation of library or changes recorded to " + project_name + ".config\n")
	    	    #print("library_generator terminated by user")
	    	    #print("no creation of library or changes recorded to " + project_name + ".config")
            	    error_code = 3 #end program
		    break
            else:
                break
	i = menu_id[j]
        pos = runmenu(menu, menus[i])
        options[i] = menus[i][pos]
        if j == 0 and pos == menus[i].index('Exit Program'):
	    error_file.write("library_generator terminated by user\n")
	    error_file.write("no creation of library or changes recorded to " + project_name + ".config\n")
	    #print("library_generator terminated by user")
	    #print("no creation of library or changes recorded to " + project_name + ".config")
            error_code = 3 #end program
	    break
        elif j != 0 and pos == menus[i].index('Previous Menu'):
            j += -1
        elif i == 0 and pos == menus[i].index('Manual input'):
            options[0] = menu_input(menu, pos, len(menus[i][pos]))
            j += 1
        elif i == 1 and pos == menus[i].index('Manual input'):
            options[1] = menu_input(menu, pos, len(menus[i][pos]))
            j += 1
        elif i == 4 and pos == menus[i].index('Generation: '):
            options[4] = menu_input(menu, pos, len(menus[i][pos]))
            j += 1
        elif i == 6 and pos == menus[i].index('Press here to enter a name'):
            options[6] = menu_input(menu, pos, len(menus[i][pos])) + '_'
            j += 1
        elif i == 7 and pos == menus[i].index('Cores: '):
            options[7] = menu_input(menu, pos, len(menus[i][pos]))
            j += 1
        else:
            j += 1

    curses.nocbreak()
    curses.echo()
    curses.curs_set(1)
    menu.keypad(0)
    curses.endwin()


    if error_code == 1:
	error_file.close()
	logfile.close()
	sys.exit('building block file not found')
    elif error_code == 2:
	error_file.close()
	logfile.close()
	sys.exit('rule file not found')
    elif error_code == 3:
	error_file.close()
	logfile.close()
	sys.exit('termination by user')

    # making necessary additions to config file
    new_lines = []
    new_lines.append('generate new library = '+ config_opts['generate new library'] + '\n')
    new_lines.append('use existing library = '+ config_opts['use existing library'] + '\n')
    new_lines.append('generation_file = '+options[1]+'\n')
    new_lines.append('building_block = '+options[0]+'\n')
    new_lines.append('input_type = '+options[2]+'\n')
    new_lines.append('combination = '+options[3]+'\n')
    new_lines.append('generations = '+options[4]+'\n')
    new_lines.append('out_type = '+options[5]+'\n')
    new_lines.append('library_out = '+options[6]+'\n')
    new_lines.append('cores = '+options[7]+'\n')
    new_lines.append('clusters = '+options[8]+'\n\n')

    config_lines = []
    new_config_lines = []
    r_switch = 1
    insert_idx = 20
    with open(project_name + '.config', 'r') as config_file:
        config_lines = config_file.readlines()
    
    logfile.writelines(config_lines)

    tmp_str = "---------------------------------------------------------------------\n"
    logfile.write(tmp_str)

    tmp_str = "After operation of library_generator, the new config file looks like:\n"
    logfile.write(tmp_str)
    
    for i,line in enumerate(config_lines):
	if r_switch == 1:
	    new_config_lines.append(line) 
	if r_switch == 0:
	    if '@' in line or 'generatejobs' in line:
	    	r_switch = 1
		new_config_lines.append(line)     
	if line == '@generatelib\n':
	    insert_idx = i+1
	    r_switch = 0

    new_config_lines[insert_idx:insert_idx] = new_lines

    with open(project_name + '.config','w') as newconfig_file:
        newconfig_file.writelines(new_config_lines)

    logfile.writelines(new_config_lines)
    tmp_str = "---------------------------------------------------------------------\n"
    logfile.write(tmp_str)

    ops = ''
    for i in xrange(len(menus) - 2):#Need the -2 since cores and cluster options don't go in the option list
        ops += '--' + menu_names[i] + ' ' + options[i] + ' '
    logfile.write(ops+'\n')
    libgen_path = os.path.realpath(__file__).rsplit('/', 2)[0]
    libgen_path += '/libgen/libgen_play.py '
    tmp_str = 'python ' + libgen_path + ops + '--ChemHTPS\n'
    if options[8] == 'run locally':
        os.system(tmp_str)
    	logfile.write(tmp_str+'\n')
    else:
        cores = int(options[7])
	nodes = 0
        tmp_str = 'mpirun -np ' + options[7] + ' ' + tmp_str
        slurm_name = 'job_templates/' + project_name + '_generatelib.sh' 
        cluster_info = []
	#cpus = ''
        if options[8] == 'beta':
            nodes = int(math.ceil(cores/16.0))
            #cpus = '#SBATCH --cpus-per-task=16\n'
            info = ['#SBATCH --clusters=chemistry\n', '#SBATCH --partition=beta --qos=beta\n', '#SBATCH --account=hachmann\n']
            cluster_info.extend(info)
        elif options[8] == 'general-compute':
            nodes = int(math.ceil(cores/8.0))
            #cpus = '#SBATCH --cpus-per-task=8\n'
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
                lines[i] = '#SBATCH --cpus-per-task='+options[7]+'\n'
            elif line == 'Runlinehere\n':
                lines[i] = tmp_str+'\n'
		logfile.write(tmp_str +'\n')
        with open('libtmp.sh','w') as slurm_file:
            slurm_file.writelines(lines)
        submit = "sbatch libtmp.sh"
        LD = "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/user/m27/pkg/openbabel/2.3.2/lib"
        os.system(LD + ';' + submit)
        os.remove("libtmp.sh")
    error_file.close()
    logfile.close()
    return 0
# TODO: write this function creating all the stuff in the dummy_project, including the config file containing the project name
