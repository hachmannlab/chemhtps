#!/usr/bin/env python

_MODULE_NAME = "job_feeder"
_MODULE_VERSION = "v0.1.0"
_REVISION_DATE = "2015-08-11"
_AUTHORS = "Johannes Hachmann (hachmann@buffalo.edu) and William Evangelista (wevangel@buffalo.edu)"
_DESCRIPTION = "This module takes the set up jobs and runs them through the high-throughput system"

# Version history timeline:
# v0.0.1 (2015-06-24): basic implementation
# v0.1.0 (2016-02-24): added support for clusters instead of just partitions
# v0.1.1 (2016-02-25): changed the way jobs are located

###################################################################################################
# TASKS OF THIS MODULE:
# -Feed the jobs generated in the job_generator module to the cluster queue
# -Basic organization of completed jobs
###################################################################################################

###################################################################################################
# TODO:
#
###################################################################################################

import sys
import os
import time
import subprocess
import fnmatch

from misc import (banner,
                  format_invoked_opts,
                  tot_exec_time_str,
                  intermed_exec_timing,
                  std_datetime_str,
                  chk_rmfile,
                  chk_mkdir,
                  target_dir_struct,
                  mv2subdir_struct)

from job_checker import check_jobs, Job

###################################################################################################


def feed_jobs(project_name, user_name):
    """
    .. function:: feed_jobs(project_name, user_name)
        This function feeds the jobs to the queue.

        :param str project_name: The name of the project
        :param str user_name: The name of the user
    """
    time_start = time.time()
    logfile = open('job_feeder.log', 'a', 0)
    error_file = open('job_feeder.err', 'a', 0)
    check_file = open('job_feeder.chk', 'a', 0)  # this contains a list of files where the node was out of space

    cwd = os.getcwd()

    # TODO think about way to handle non default folders and paths (possibly argparser)
    slurm_path = cwd + '/job_templates'
    job_pool_path = cwd + '/jobpool'
    scratch_path =  os.environ['GLOBAL_SCRATCH'] + '/' + user_name + '/' + project_name
    result_path = cwd + '/archive'
    problem_path = cwd + '/lost+found'
    queue_file_path = cwd + '/queue_list.dat'

    chk_mkdir(scratch_path)  # Do this for result and problem paths as well if they aren't default folders

    # Makes sure all necessary components are present
    if not os.path.isdir(slurm_path):
        error_file.write('no slurm path')
        sys.exit('Missing dir: ' + slurm_path)
    if not os.path.isdir(job_pool_path):
        error_file.write('no jobpool path')
        sys.exit('Missing dir: ' + job_pool_path)
    if not os.path.isdir(result_path):
        error_file.write('no result path')
        sys.exit('Missing dir: ' + result_path)
    if not os.path.isdir(problem_path):
        error_file.write('no problem path')
        sys.exit('Missing dir: ' + problem_path)
    if not os.path.isfile(queue_file_path):
        error_file.write('no queue path')
        sys.exit('Missing dir: ' + queue_file_path)

    # Keeps track of the run dir
    run_dir_counter = 0

    job_class_list = []

    while 1:
        queue_list = []  # List of quadruples (cluster name, partition name, total jobs that can be run, job type)
        queue_file = open(queue_file_path, 'r')
        # Reads the list of available queues
        while 1:
            line = queue_file.readline()
            if not line:
                break
            words = line.split()
            if len(words) == 4:
                if words[0][0] != '#':
                    queue_list.append(words)
        queue_file.close()

        quickcycle_flag = False

        # Process the queues
        for queue in queue_list:

            # Check current load on the queue
            if len(queue[1]) < 10:
                tmp_str = "squeue -M " + queue[0] + " -u " + user_name + " | grep '" + queue[1] + " ' | grep 'R\|PD' | wc -l"
            else:
                tmp_str = "squeue -M " + queue[0] + " -u " + user_name + " | grep '" + queue[1][0:9] + " ' | grep 'R\|PD'  | wc -l"
            queue_load = int(subprocess.Popen(tmp_str, shell=True, stdout=subprocess.PIPE).stdout.read())
            # Check for space on the queue for new jobs
            if queue_load < int(queue[2]):
                n_new_jobs = int(queue[2]) - queue_load
                if n_new_jobs > (int(queue[2]) / 2):
                    quickcycle_flag = True
                if queue[3] == 'long':
                    job_pool_type_list = ('priority', 'long', 'short')
                elif queue[3] == 'short':
                    job_pool_type_list = ('short',)
                else:
                    sys.exit('Unknown queue type')

                job_counter = 0
                # Make a list of job source paths
                job_source_path_list = []
                for job_pool_type in job_pool_type_list:
                    for folder in os.listdir(job_pool_path + '/' + job_pool_type):
                        for job in os.listdir(job_pool_path + '/' + job_pool_type + '/' + folder):
                            # TODO: listdir gives random order should sort by timestamp
                            if job_counter == n_new_jobs:
                                break
                            tmp_str = job_pool_path + '/' + job_pool_type + '/' + folder + '/' + job
                            if os.path.isdir(tmp_str):
                                job_source_path_list.append(tmp_str)
                                job_counter += 1

                for job_source_path in job_source_path_list:
                    slurm_script = project_name + queue[1] + '.sh'
                    while 1:
                        job_target_path = scratch_path + '/%07d' % run_dir_counter
                        if os.path.isdir(job_target_path):
                            run_dir_counter += 1
                        else:
                            chk_mkdir(job_target_path)
                            run_dir_counter += 1
                            break
                    tmp_str = 'mv ' + job_source_path + ' ' + job_target_path + '/.'
                    os.system(tmp_str)

                    # Move slurm script into job folder
                    # TODO possibly rethink this maybe do in job_generator module, also options for different slurm scripts
                    # Changed to allow for slurm scripts to already be in job folder
                    slurm_exists = False
                    for root, directories, filenames in os.walk(job_target_path):
                        for filename in fnmatch.filter(filenames, '*.sh'):
                            if filename != None:
                                slurm_exists = True
                                slurm_script = os.path.join(root, filename)
                    if slurm_exists:
                        pass
                    else:
                        tmp_str = 'cp ' + slurm_path + '/' + slurm_script + ' ' + job_target_path + '/' + job_source_path.split('/')[-1]
                        os.system(tmp_str)

                    os.chdir(job_target_path + '/' + job_source_path.split('/')[-1])

                    # Submit job to the queue
                    os.environ["PATH"] += os.pathsep + cwd + '/job_templates'
                    tmp_str = 'sbatch ' + slurm_script
                    job_class_list.append(job_source_path.split('/')[-1])
                    job_class_list[-1]=Job(job_class_list[-1], queue[0], tmp_str)


                    tmp_str = std_datetime_str() + ": Submitting " + job_target_path + '/' + job_source_path.split('/')[-1]
                    logfile.write(tmp_str + '\n')

                    os.chdir(cwd)

        # TODO: Need to process finished jobs still

        if quickcycle_flag:
            time.sleep(60)
            job_class_list = check_jobs(user_name, scratch_path, result_path, problem_path, job_class_list)
        else:
            time.sleep(500)
            job_class_list = check_jobs(user_name, scratch_path, result_path, problem_path, job_class_list)

    # end of run section (Note: since we use an endless loop, we will probably never use the regular exit)
    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
    logfile.write(tmp_str + '\n')

    tmp_str = tot_exec_time_str(time_start) + '\n' + std_datetime_str()
    print tmp_str + '\n\n\n'
    logfile.write(tmp_str + '\n\n\n')
    logfile.close()
    error_file.close()
    check_file.close()

    # Check whether error files contain anything
    chk_rmfile(error_file)
    chk_rmfile(check_file)

    return 0
