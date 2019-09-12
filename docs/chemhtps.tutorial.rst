Demo Tutorial Guide
===================

This guide will go over a short demo project to make users more familiar with the various nuts and bolts that go behind a typical ChemHTPS project's work-flow.


.. code:: bash

   chemhtpsshell --setup_project --project_name  trial


The above command will start a new project called "trial" at the current location.

.. code:: bash

   $ ls trial
   archive  db  jobpool  job_templates  lost+found  queue_list.dat  screeninglib  trial.config

Among the contents of a project folder:
    
        - "archive/" is where successfull jobs get tarred and archived to
        - "db/" should be used for storing the generated data in a data-base
        - "jobpool/" keeps all the jobs generated that are yet to be run under "short/" and "long/" sub-folders
        - "job_templates/" keeps the project-specific SLURM scripts and program-template files. These are essentially copies of the files in the "chemhtps/chemhtps/metadata/job_templates/" folder. Users can make their desired SLURM scripts in the original metadata location as well
        - "lost+found/" stores all the unsuccessful jobs
        - "queue_list.dat" contains the various cluster/partition limits that can be defined by the user before a job-run
        - "screeninglib/" contains all the files and folders for library-generation purposes
        - "trial.config" is the config-file for this project

Although, ChemHTPS can be used purely for work-flow purposes, in our example we will show its use while interfacing with ChemLG for library generation.

Once, the project has been setup as shown above, the config-file "trial.config" will look like:

.. literalinclude:: ref_files/trial-config.txt
   :linenos:   

Once the user has downloaded and installed chemlg, (for instructions see https://hachmannlab.github.io/chemlg/), the "config.dat" file under the "chemlg/chemlg/templates/" folder should be copied into the "trial/screeninglib/" folder
    
Without going into stuff that will require an in-depth discussion of the mechanics of ChemLG, in this example we will be using a library that will be generated from a file already containing a list of SMILES codes for molecules. 

.. literalinclude:: ref_files/trial-smiles.dat
   :linenos:   

We will use ChemLG to just convert the smiles in the above file into their .xyz formats. 
The ChemLG config-file for this will look like:


.. literalinclude:: ref_files/trial-chemlg.dat
   :linenos:   

and the ChemHTPS will be something like:

.. literalinclude:: ref_files/trial-config-1.txt
   :linenos:   

Note that the generation number in the ChemLG config-file has been kept 0 since we are not generating any new molecules and are converting the existing ones between file-formats. Now, the library-generator call will be done (note: this MUST be done from within the project folder).

.. code:: bash

   $ chemhtpsshell --generatelib


After the run, the "screeninglib/" folder will look like:

.. code:: bash

   $ ls screeninglib/
   building_blocks.dat  config.dat  final_library.csv  logfile.txt  trial_lib_xyz  trial-smiles.dat
   $ ls screeninglib/trial_lib_xyz/1_1000
   1.xyz  2.xyz  3.xyz  4.xyz  5.xyz  6.xyz  7.xyz  8.xyz  9.xyz 

Moving on to the job-generation step, the options for generatejobs need to be modified. For our case the config-file looks like this:

.. literalinclude:: ref_files/trial-config-2.txt
   :linenos:

We will be generating input files using the template file as shown above. For more information on template files and their working, please refer to:

.. toctree::
   :maxdepth: 4
   :caption: ChemHTPS Template Guide

   chemhtps.template


Once this step is completed, the job-folders look like the following:

.. code:: bash

   $ ls jobpool/long/
   jg1_ORCA_trial_lib_xyz_1_1000
   $ ls jobpool/long/jg1_ORCA_trial_lib_xyz_1_1000/
   1  2  3  4  5  6  7  8  9
   $ ls jobpool/long/jg1_ORCA_trial_lib_xyz_1_1000/1/
   1.inp  1.xyz

Note that in the above case, the jobs  are all put together in a folder with the prefix of jg1. This signifies that this group of jobs was created first and so on and so forth. This distinction therefore allows the job-feeder module to proceed serially and prioritize the earlier jobs that were created. Furthermore, every cycle of job-generation can be referred back to in the "job_gen.log" log-file. One can look in the log-file to check what the config-options were for every job-generator module call. Each individual job-folder within the larger class contains the correponding .xyz and the .inp input files as seen above with 1.xyz and 1.inp files, respectively.

After making appropriate changes to feed_local and job_sched options in the config-file under the feedjobs section, we can finally execute all the jobs under the "jobpool/" folder by:

.. code:: bash

   $ chemhtpsshell --feedjobs

These jobs will be submitted according to the limits set in the "queue_list.dat" file:

.. literalinclude:: ref_files/queue.txt
   :linenos:

In our case, we will set the limit of jobs to be run in the "beta" cluster/partition combination as 10 since we have 9 jobs to run. The definitions of the cluster/partition combinations can be changed in this file and the corresponding job-scheduler (SLURM) scripts shoulld be available in the "job_templates/" folder. One can try it out and note the logs and the error messages in "feedjobs.out" and "job_checker.err", respectively.

Finally, we would like to make two important points, one of them being a reminder. All the module-calls apart from --setup_project must be made from within the project directory. Additionally, all these non-setup module-calls can also be combined into a one-line command after making the desired changes for all the modules in the config-file. This command simply looks like:

.. code:: bash

   $ chemhtpsshell --generatelib --generatejobs --feedjobs

Note that even when the order of the module-calls look like:

.. code:: bash

   $ chemhtpsshell --generatelib --feedjobs --generatejobs

The end result of the execution however, will still proceed in the library --> job-generation --> job-feeder logic-flow.




