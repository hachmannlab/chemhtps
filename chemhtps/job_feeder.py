#!/usr/bin/env python

_MODULE_NAME = "job_feeder"
_MODULE_VERSION = "v0.1.0"
_REVISION_DATE = "2019-01-10"
_AUTHORS = "Johannes Hachmann (hachmann@buffalo.edu), William Evangelista (wevangel@buffalo.edu) and Yudhajit Pal (yudhajit@buffalo.edu)"
_DESCRIPTION = "This module takes the set up jobs and runs them through the high-throughput system"

import sys
import os
import os.path
import time
import subprocess
import fnmatch

from misc import (banner,
                  menu_input,
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


def feed_jobs(project_name, user_name, config_opts):
    """
        This function feeds the jobs to the queue.

        :param str project_name: The name of the project
        :param str user_name: The name of the user
        :param dict config_opts: The options specified in the .config file
    """
    time_start = time.time()
    logfile = open('job_feeder.log', 'a')
    error_file = open('job_feeder.err', 'a')

    banner_list = banner(_MODULE_NAME, _MODULE_VERSION, _REVISION_DATE, _AUTHORS, '', _DESCRIPTION)
    for line in banner_list:
        print (line)
        logfile.write(line + '\n')
    
    cwd = os.getcwd()
    slurm_path = cwd + '/job_templates'
    job_pool_path = cwd + '/jobpool'
    scratch_path =  os.environ['GLOBAL_SCRATCH'] + '/' + user_name + '/' + project_name
    result_path = cwd + '/archive'
    problem_path = cwd + '/lost+found'
    queue_file_path = cwd + '/queue_list.dat'

    chk_mkdir(scratch_path)
    chk_mkdir(result_path)
    chk_mkdir(problem_path)

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
    quickcycle_flag = False
    job_class_list = []
    jobs_length = 0
    job_lines = []
    #job_tracker.log keeps track of all the jobs that at last check hadn't been processed after their submission
    #so this part checks for the spillover jobs from the last run that needs processing
    if os.path.isfile('job_tracker.log'):
        with open('job_tracker.log', 'r') as job_logfile:
            job_lines = job_logfile.readlines()
        for line in job_lines:
            words = line.rstrip().rsplit(',')
            new_job = []
            new_job.append(words[0])
            new_job[-1] = Job(new_job[-1], words[1])
            new_job[-1].path = words[2]
            new_job[-1].slurm_id = words[3]
            job_class_list.append(new_job[-1]) 

        tmp_str = "cp job_tracker.log job_tracker_old.log"
        os.system(tmp_str)

        job_class_list = check_jobs(user_name, scratch_path, result_path, problem_path, job_class_list)
        if jobs_length != len(job_class_list):
            print ("-------------------------------------------------------------------------------")
            print ("Jobs running at: " + std_datetime_str())
            job_logfile = open('job_tracker.log', 'w')
            jobs_length = len(job_class_list)
            for job in job_class_list:
                tmp_str = str(job.name) + ',' + str(job.cluster) + ',' + str(job.path) + ',' + str(job.slurm_id) + '\n' 
                job_logfile.write(tmp_str)
                print (tmp_str.strip('\n'))
                job_logfile.flush()
            job_logfile.close()
    

    if config_opts['job_sched'] == 'SLURM':
        counter = 0
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
            
            job_logfile = open('job_tracker.log', 'w')

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
                        job_pool_type_list = ( 'long', 'short')
                    elif queue[3] == 'short':
                        job_pool_type_list = ('short',)
                    else:
                        sys.exit('Unknown queue type')

                    job_counter = 0
                    # Make a list of job source paths
                    job_source_path_list = []
                    for job_pool_type in job_pool_type_list:
                        # Jobpool folders sorted by chronology of job_generation
                        for folder in sorted(os.listdir(job_pool_path + '/' + job_pool_type)):
                            # Job folders within a pool sorted by chronology of ease of calculation as done during generation phase
                            for job in sorted(os.listdir(job_pool_path + '/' + job_pool_type + '/' + folder)):
                                if job_counter == n_new_jobs:
                                    break
                                tmp_str = job_pool_path + '/' + job_pool_type + '/' + folder + '/' + job
                                if os.path.isdir(tmp_str):
                                    job_source_path_list.append(tmp_str)
                                    job_counter += 1

                    # Goes through the list of jobs and moves the necessary job files into the corresponding scratch folders
                    for job_source_path in job_source_path_list:
                        #print (job_source_path)
                        if len(job_source_path.split('/')) < 2:
                            continue
                        if len(job_source_path.split('/')[-2].split('_')) < 6:
                            continue
                        prog = job_source_path.split('/')[-2].split('_')[1]
                        lib = "".join(job_source_path.split('/')[-2].split('_')[2:-3])
                        job_no = job_source_path.split('/')[-2].split('_')[0] + '_'  + job_source_path.split('/')[-1]
                        j_no = job_source_path.split('/')[-1]
                        slurm_script = project_name + '_' + prog + '_'  + queue[1] + '.sh'
                        
                        while 1:
                            job_target_path = scratch_path + '/%07d' % run_dir_counter
                            if os.path.isdir(job_target_path):
                                run_dir_counter += 1
                            else:
                                chk_mkdir(job_target_path)
                                run_dir_counter += 1
                                break
                        tmp_str = 'mv ' + job_source_path + ' ' + job_target_path + '/' + job_no
                        os.system(tmp_str)
                        logfile.write(tmp_str + '\n')
                        tmp_str = 'mv ' + job_target_path + '/' + job_no + '/' + j_no + '.inp' + ' ' + job_target_path + '/' + job_no + '/' + prog + '.' + lib + '.' + job_no + '.inp'
                        os.system(tmp_str)
                        logfile.write(tmp_str + '\n')

                        # Move slurm script into job folder
                        slurm_exists = False
                        for root, directories, filenames in os.walk(job_target_path):
                            for filename in fnmatch.filter(filenames, '*.sh'):
                                if filename != None:
                                    slurm_exists = True
                                    slurm_script = os.path.join(root, filename)
                        if slurm_exists:
                            pass
                        else:
                            #tmp_str = 'cp ' + slurm_path + '/' + slurm_script + ' ' + job_target_path + '/' + job_no + '/'
                            #os.system(tmp_str)
                            slurm_file = job_target_path + '/' + job_no + '/' + slurm_script
                            with open (slurm_path + '/' + slurm_script,'r') as temp:
                                slurm_lines = temp.readlines()
                                for i,line in enumerate(slurm_lines):
                                    if 'infile here' in line:
                                        slurm_lines[i] = 'export INFILE=' + prog + '.' + lib + '.' + job_no + '.inp\n'
                                    elif 'outfile here' in line:
                                        slurm_lines[i] = 'export OUTFILE=' + prog + '.' + lib + '.' + job_no + '.out\n'
                                with open (slurm_file,'w') as temp_wr:
                                    temp_wr.writelines(slurm_lines)

                        os.chdir(job_target_path + '/' + job_no)
                        tmp_str = "sed -i \"8i#SBATCH --job-name="+ prog + '.' + lib + '.' +  job_no + "\" " + slurm_script
                        os.system(tmp_str)

                        # Submit job to the queue
                        #os.environ["PATH"] += os.pathsep + cwd + '/job_templates'
                        tmp_str = 'sbatch ' + slurm_script
                        job_class_list.append(prog+ '.' + lib + '.' + job_no)
                        job_class_list[-1]=Job(job_class_list[-1], queue[0])
                        job_class_list[-1].slurm_submit_id(tmp_str)

                        job = job_class_list[-1]
                        tmp_str = str(job.name) + ',' + str(job.cluster) + ',' + str(job.path) + ',' + str(job.slurm_id) + '\n'
                        #print (tmp_str)
                        job_logfile.write(tmp_str)
                        tmp_str = std_datetime_str() + ": Submitting " + prog + '.' + lib + '.' + job_no + ' at '  + job_target_path + '/' + job_no
                        logfile.write(tmp_str + '\n\n')

                        os.chdir(cwd)
            job_logfile.flush()
            job_logfile.close()
            # TODO: Need to process finished jobs still

            if quickcycle_flag:
                time.sleep(60)
                job_class_list = check_jobs(user_name, scratch_path, result_path, problem_path, job_class_list)
                #counter = counter + 1
                if jobs_length != len(job_class_list):
                    print ("Jobs running at: " + std_datetime_str())
                    jobs_length = len(job_class_list)
                    tmp_str = "cp job_tracker.log job_tracker_old.log"
                    os.system(tmp_str)
                    job_trackfile = open('job_tracker.log', 'w')
                    for job in job_class_list:
                        tmp_str = str(job.name) + ',' + str(job.cluster) + ',' + str(job.path) + ',' + str(job.slurm_id) + '\n' 
                        job_trackfile.write(tmp_str)
                        print(tmp_str.strip('\n'))
                        job_trackfile.flush()
                    job_trackfile.close()
            else:
                time.sleep(500)
                job_class_list = check_jobs(user_name, scratch_path, result_path, problem_path, job_class_list)
                #counter = counter + 1
                if jobs_length != len(job_class_list):
                    print ("Jobs running at: " + std_datetime_str())
                    jobs_length = len(job_class_list)
                    tmp_str = "cp job_tracker.log job_tracker_old.log"
                    os.system(tmp_str)
                    job_trackfile = open('job_tracker.log', 'w')
                    for job in job_class_list:
                        tmp_str = str(job.name) + ',' + str(job.cluster) + ',' + str(job.path) + ',' + str(job.slurm_id) + '\n' 
                        job_trackfile.write(tmp_str)
                        print(tmp_str.strip('\n'))
                        job_trackfile.flush()
                    job_trackfile.close()

        # end of run section (Note: since we use an endless loop, we will probably never use the regular exit)
    tmp_str = "------------------------------------------------------------------------------ "
    print (tmp_str)
    logfile.write(tmp_str + '\n')

    tmp_str = tot_exec_time_str(time_start) + '\n' + std_datetime_str()
    print (tmp_str + '\n\n\n')
    logfile.write(tmp_str + '\n\n\n')
    logfile.close()
    error_file.close()

    # Check whether error files contain anything
    chk_rmfile(error_file)

    return 0
