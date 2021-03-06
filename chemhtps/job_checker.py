#1/usr/bin/env python

_MODULE_NAME = "job_checker"
_MODULE_VERSION = "v0.1.0"
_REVISION_DATE = "2019-01-10"
_AUTHORS = "Johannes Hachmann (hachmann@buffalo.edu), William Evangelista (wevangel@buffalo.edu) and Yudhajit Pal (yudhajit@buffalo.edu)"
_DESCRIPTION = "This module checks for completed jobs and attempts error handling on crashed jobs."

import os
import sys
import glob
import subprocess
import fnmatch
import datetime
from .utils.misc import chk_mkdir


class Job(object):
    """
        A class to handle all aspects of a job unit

        :param str name: The name of the job unit
        :param str cluster: Which cluster the job was submitted to
        :param str sbatch: The slurm submission string
        :param str path: The path to the location the job is run from
        :param str slurm_id: The slurm job id of the job
        :param str slurm_last_line: The last line of the slurm output file
        :param str slurm_3last_line: The third from last line of the slurm output file specific for Q-chem errors
        :param str out_last_line: The last line of the quantum software output file
        :param bool is_running: A boolean that is true if the job is running and False if its not
        :param str rm_path: a path for removal, if populated can be deleted because the job has been tarred
    """
# initializes the important parameters for each job_object


    def __init__(self, name, cluster):
        """
            Initialize a Job object.
        """
        self.name = name
        self.cluster = cluster
        self.path = os.getcwd()
        self.slurm_id = ''
        self.is_running = True
        self.rm_path = ''
        self.slurm_last_line = ''
        self.out_last_line = ''
        self.out_2last_line = ''
        self.slurm_3last_line = ''
        self.out_3last_line = ''

    def slurm_submit_id(self,sbatch):
        """
            Submits the job and retrieves the jobid for tracking
            :param str sbatch: The sbatch command needed to submit that job
        """
        self.slurm_id = str(subprocess.check_output(sbatch, shell=True).split()[3]).split('\'')[1]

    def check_status(self, user_name):
        """
            Checks if the slurm job has finished or not and updates the is_running variable

            :return self.is_running: The state of the job
            :rtype: bool
        """
        tmp = "squeue -M " + str(self.cluster) + " -u " + str(user_name) + " | grep " + str(self.slurm_id) + " | wc -l"
        number = int(subprocess.check_output(tmp, shell=True))
        if number == 0:
            self.is_running = False
        else:
            pass
        return self.is_running

    def time_limit_restart(self):
        """
            Makes the necessary changes to the input file and gbw file to restart a job that ran out of time
            Note: This only applies to ORCA jobs
        """
        input_file = self.path + '/' + self.name + '.inp'
        gbw = self.path + '/' + self.name + '.gbw'
        tmp = "mv " + gbw + " " + self.path + '/' + 'old.gbw'
        os.system(tmp)
        with open(input_file, 'r') as inp:
            lines = inp.readlines()
        lines.insert(1, "!MORead\n")
        lines.insert(2, '%moinp "old.gbw"\n')
        with open(input_file, 'w') as ninp:
            ninp.writelines(lines)

    def nth_line(self, n, file_name):
        """
            Returns the nth from the end line of the specified file

            :param str file_name: The name of the file
            :param int n: Number of lines from the end
            :return line: The nth line
            :rtype: str
        """
        #print (self.path + '/' + file_name)
        out = open(self.path + '/' + file_name,'r')
        contents = out.readlines()
        contents = [x.strip('\n') for x in contents]
        if len(contents) < n : return 'IndexError'
        line = contents[-n]
        return line

    def slurm_last(self):
        """
            Get the last line of the slurm output
        """
        #print (self.slurm_id)
        self.slurm_last_line = self.nth_line(1, 'slurm.out')
         
    def slurm_3last(self):
        """
            Get the last line of the slurm output
        """
        #print (self.slurm_id)
        self.slurm_3last_line = self.nth_line(3, 'slurm.out')
         
    def out_last(self):
        """
            Get the last line of the quantum software output
        """
        self.out_last_line = self.nth_line(1, self.name + ".out")
    
    def out_2last(self):
        """
            Get the last line of the quantum software output
        """
        self.out_2last_line = self.nth_line(2, self.name + ".out")

    def out_3last(self):
        """
            Get the third from last line of the quantum software output
        """
        self.out_3last_line = self.nth_line(3, self.name + ".out")

    def tar_job_unit(self, tbz='.tbz'):
        """
            Tars the jobunit preparing it for transport

            :param str tbz: The tar file extension
        """
        cwd = os.getcwd()
        os.chdir(self.path.rsplit('/', 1)[0])
        tmp = "tar -cjf " + self.name + tbz + " " + self.name.split('.')[-1]
        os.system(tmp)
        self.rm_path = self.path
        self.path = self.path.rsplit('/', 1)[0] + '/' + self.name + tbz
        os.chdir(cwd)

    def move_job(self, dest_path):
        """
            moves the job unit to the specified location

            :param str dest_path: The destination path where the jobunit is going
        """
        tmp = "mv " + self.path + " " + dest_path
        print (tmp)
        os.system(tmp)

    def rm_job(self):
        """
            Deletes the job folder after the job has been tarred
        """
        tmp = "rm -r " + self.rm_path
        os.system(tmp)


def check_jobs(user_name, scratch, archive, lost, job_list):
    """
        This function checks for completed or crashed jobs and processes them.

        :param str scratch: The path of the scratch directory where jobs are run
        :param str archive: The path of the archive to place finished jobs
        :param str lost: The path of the lost and found folder for user attention
        :param str job_list: A list of current job units to check
        :return rem_list: List of jobs still running and/or waiting to be processed
        :rtype: list of Job objects
    """

    cwd = os.getcwd()
    logfile = open('job_checker.log', 'a')
    error_file = open('job_checker.err', 'a')

    if not os.path.isdir(scratch):
        error_file.write("There is no scratch folder with jobs\n")
        sys.exit('Missing scratch folder')

    rem_list = []
    for job in job_list:
        if not job.check_status(user_name):
            if not os.path.isfile(job.path+'/slurm.out') or not os.path.isfile(job.path + '/' + job.name + '.out'):
                rem_list.append(job)
                continue
            job.slurm_last()
            job.slurm_3last()
            job.out_last()
            job.out_2last()
            job.out_3last()
            if job.slurm_last_line == "All Done!" and "TOTAL RUN TIME:" in job.out_last_line: #orca success
                job.tar_job_unit()
                job.move_job(archive)
                job.rm_job()
                now = datetime.datetime.now()
                logfile.write('Job ' + job.name + ' has finished and been moved to the archive: ' + str(now) + '\n')
            elif job.slurm_last_line == "All Done!" and "cleanup process" in job.out_last_line: #qchem success
                job.tar_job_unit()
                job.move_job(archive)
                job.rm_job()
                now = datetime.datetime.now()
                logfile.write('Job ' + job.name + ' has finished and been moved to the archive: ' + str(now) + '\n')
            elif job.slurm_last_line == "All Done!" and job.out_last_line == "ABORTING THE RUN": #orca failure 
                job.tar_job_unit('.coordoff.tbz')
                job.move_job(lost)
                job.rm_job()
                now = datetime.datetime.now()
                logfile.write('Job ' + job.name + ' has not finished due to the geometry being very off, moved to lost+found: ' + str(now) + '\n')
            elif job.slurm_last_line == "All Done!" and "Error : multiplicity" in job.out_2last_line: #orca multiplicity failure 
                job.tar_job_unit('.spinchargeerr.tbz')
                job.move_job(lost)
                job.rm_job()
                now = datetime.datetime.now()
                logfile.write('Job ' + job.name + ' has not finished due to a mismatch between charge and spin multiplicity, moved to lost+found: ' + str(now) + '\n')
            elif job.slurm_last_line == "All Done!" and "You must have a [COORDS] ... [END] block in your input" in job.out_2last_line: # orca missing mol failure
                job.tar_job_unit('.missingmolsec.tbz')
                job.move_job(lost)
                job.rm_job()
                now = datetime.datetime.now()
                logfile.write('Job ' + job.name + ' has not finished due to a missing molecule section in the geometry, moved to lost+found: ' + str(now) + '\n')
            elif job.slurm_last_line == "All Done!" and job.out_last_line == "No atoms to convert in Cartesian2Internal": #orca geometry failure
                job.tar_job_unit('.missingcoord.tbz')
                job.move_job(lost)
                job.rm_job()
                now = datetime.datetime.now()
                logfile.write('Job ' + job.name + ' has not finished due to a missing coordinate in the geometry, moved to lost+found: ' + str(now) + '\n')
            elif job.slurm_last_line == "All Done!" and "interrupt SIGx" in job.out_last_line:
                if "Could not find $molecule section" in job.out_3last_line: #qchem missing mol failure
                    job.tar_job_unit('.missingmolsec.tbz')
                    job.move_job(lost)
                    job.rm_job()
                    now = datetime.datetime.now()
                    logfile.write('Job ' + job.name + ' has not finished due to a missing molecule section in the geometry, moved to lost+found: ' + str(now) + '\n')
                elif "Basis not supported for the above atom." in job.out_3last_line: #qchem basis failure
                    job.tar_job_unit('.basiserror.tbz')
                    job.move_job(lost)
                    job.rm_job()
                    now = datetime.datetime.now()
                    logfile.write('Job ' + job.name + ' has not finished due to a basis set error, moved to lost+found: ' + str(now) + '\n')
                elif "Should be exactly two non-comment tokens on charge and multiplicity line" in job.out_3last_line: #qchem basis failure
                    job.tar_job_unit('.missingmol.tbz')
                    job.move_job(lost)
                    job.rm_job()
                    now = datetime.datetime.now()
                    logfile.write('Job ' + job.name + ' has not finished due to missing molecule, moved to lost+found: ' + str(now) + '\n')
                elif "Invalid charge/multiplicity combination in MoleculeInput" in job.out_3last_line: #qchem basis failure
                    job.tar_job_unit('.spinchargeerr.tbz')
                    job.move_job(lost)
                    job.rm_job()
                    now = datetime.datetime.now()
                    logfile.write('Job ' + job.name + ' has not finished due to a mismatch between charge and spin multiplicity, moved to lost+found: ' + str(now) + '\n')
                else:
                    job.tar_job_unit('.bad.tbz')
                    job.move_job(lost)
                    job.rm_job()
                    now = datetime.datetime.now()
                    logfile.write('Job ' + job.name + ' has not finished for unknown reason: ' + str(now) + '\n')
                    error_file.write('Job ' + job.name + ' has not finished due to a previously unknown issue: ' + str(now) + '\n')
            elif job.slurm_last_line == "All Done!" and "net_send: could not write to" in job.out_last_line : #qchem parallel failure
                job.tar_job_unit('.nodeerror.tbz')
                job.move_job(lost)
                job.rm_job()
                now = datetime.datetime.now()
                logfile.write('Job ' + job.name + ' has not finished due to a problem in parallel communication, moved to lost+found: ' + str(now) + '\n')
            #elif job.slurm_last_line == "slurmstepd: Exceeded step memory limit at some point." and job.name.split('.')[0] == 'ORCA': #memory limit failure
            #    restarts = cwd + '/jobpool/priority/restarts'
            #    chk_mkdir(restarts)
            #    job.move_job(restarts)
            #    now = datetime.datetime.now()
            #    logfile.write('Job ' + job.name + ' crashed due to a memory issue, and has been restarted: ' + str(now) + '\n')
            #elif "DUE TO TIME LIMIT" in job.slurm_last_line and job.name.split('.')[0] == 'ORCA': #time limit failure
            #    job.time_limit_restart()
            #    restarts = cwd + '/jobpool/priority/' 
            #    chk_mkdir(restarts)
            #    job.move_job(restarts)
            #    now = datetime.datetime.now()
            #    logfile.write('Job ' + job.name + ' ran out of time and has been restarted: ' + str(now) + '\n')
            else:
                job.tar_job_unit('.bad.tbz')
                job.move_job(lost)
                job.rm_job()
                now = datetime.datetime.now()
                logfile.write('Job ' + job.name + ' has not finished for unknown reason: ' + str(now) + '\n')
                error_file.write('Job ' + job.name + ' has not finished due to a previously unknown issue: ' + str(now) + '\n')
        else:
            rem_list.append(job)
            pass
    

    return rem_list
