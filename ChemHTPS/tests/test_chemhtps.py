#!/usr/bin/env python

_MODULE_NAME = "test_chemhtps"
_MODULE_VERSION = "v0.1.0"
_REVISION_DATE = "2015-08-18"
_AUTHORS = "Johannes Hachmann (hachmann@buffalo.edu) and William Evangelista (wevangel@buffalo.edu)"
_DESCRIPTION = "These are the tests"

# Version history timeline:
# v0.1.0 (2015-08-18): basic implementation

###################################################################################################
# TASKS OF THIS MODULE:
# -Test different portion of the project to make sure it works
###################################################################################################

###################################################################################################
# TODO:
#
###################################################################################################

import pytest
import os
import shutil
from chemhtps.project_setup import setup_project
from chemhtps.job_generator import generate_jobs
from chemhtps.misc import chk_mkdir


def test_gonna_fail():
    """
    Just an experiment
    """
    assert True == False  # Going to fail here on line 34


def test_setup_project():
    """
    A test for the setup_project() function in project_setup.py
    """
    setup_project('testing')
    dir_list = ['/archive', '/db', '/jobpool/short', '/jobpool/priority', '/jobpool/long', '/lost+found',
                '/screeninglib/geometrylib', '/screeninglib/structurelib', '/job_templates']
    file_list = ['/testing.config', '/screeninglib/building_blocks.dat', '/screeninglib/config.dat']
    for dir in dir_list:
        assert True == os.path.isdir('testing' + dir)
    for file in file_list:
        assert True == os.path.isfile('testing' + file)

def test_generate_lib():
    """
    A test for the generate_geometries() function in library_generator.py
    """
    cwd = os.getcwd()
    ## Menu for the library generator options
    inp = []
    rule = []
    cluster = ['general-compute', 'beta', 'run locally']

    ## dictionary of menus for checking all available options
    menus = {0: inp, 1: rule, 2: cluster}
    
    for root, directories, filenames in os.walk(cwd + '../chemlg/chemlg/templates'):
        for filename in fnmatch.filter(filenames, '*building*'):
            menus[0].insert(0,os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, '*smiles.csv*'):
            menus[0].insert(0,os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, '*config*'):
            menus[1].insert(0,os.path.join(root, filename))
    print (menus)


def test_generate_jobs():
    """
    A test of the generate_jobs() function in job_generator.py
    """
    # template = ['!DFT PBE0 Def2-SVP smallPRINT PRINTBASIS PRINTGAP\n', '!opt']
    # with open('testing/job_templates/PBE0_def2svp.inp', 'w') as test_template:
    #     test_template.writelines(template)
    testgeo = ['C 0.000000 0.000000 0.000000\n', 'C 0.000000 0.000000 1.400000\n', 'C 1.212436 0.000000 2.100000\n',
               'C 2.424871 0.000000 1.400000\n', 'C 2.424871 0.000000 0.000000\n', 'C 1.212436 0.000000 -0.700000\n',
               'H -0.943102 0.000000 1.944500\n', 'H 1.212436 0.000000 3.189000\n', 'H 3.367973 0.000000 1.944500\n',
               'H 3.367973 0.000000 -0.544500\n', 'H 1.212436 0.000000 -1.789000\n', 'H -0.943102 0.000000 -0.544500\n']
    chk_mkdir('testing/screeninglib/newlib/1_1000')
    with open('testing/screeninglib/newlib/1_1000/testing.xyz', 'w') as test_geo:
        test_geo.writelines(testgeo)
    cwd = os.getcwd()
    os.chdir(cwd + '/testing')
    generate_jobs()
    os.chdir('..')
    assert True == os.path.isfile('testing/jobpool/short/testing/testing.xyz')
    assert True == os.path.isfile('testing/jobpool/short/testing/testing.inp')
    assert True == os.path.isfile('testing/screeninglib/geometrylib/testing.xyz')


def test_check_jobs()
    """
    A test of the nth_line() function in job_checker.py with n=1
    """
    cwd = os.getcwd()
    out = open(cwd + '../chemlg/chemlg/templates/config.dat', 'r')
    contents = out.readlines()
    contents = [x.strip('\n') for x in contents]
    if len(contents) < 1 : return 'IndexError'
    line = contents[-1]
    assert line == 'Library name                    :: new_library_'


def test_wrap_up():
    """
    This test just deletes the temporary test project that was created to run the previous tests
    """
    shutil.rmtree('testing')
    assert False == os.path.isdir('testing')

if __name__ == '__main__':
    pytest.main()
