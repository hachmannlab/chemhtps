ChemHTPS Modules and the Config File
====================================

ChemHTPS is called through a simple shell command along with arguments signaling the modules that will be triggered. 
The modules are:

- library generator
- job generator
- job feeder


The config file should closely follow the template of the initial config file that is created once the project is set-up. There are general as well as module-specific options as follows:

- log-file: Specify the log-file for a call of chemhtpsshell. 

        - Expected type: string file-name
        - Default value: "project_name".log

|

- error-file: Specify the error-file for a call of chemhtpsshell. 

        - Expected type: string file-name
        - Default value: "project_name".err

|



library generator module:

        -called by --generatelib parser argument 

- generation_file: Specify the ChemLG config-file to be used for this module call for ChemLG execution. 

        - Expected type: string file-name from current location
        - Default value: None

|

- building_block: Specify the ChemLG building-block file to be used for this module call for ChemLG execution. 

        - Expected type: string file-name from current location
        - Default value: None

|

- cores: Specify the number of cpus to be used for this run of library generator or the ChemLG call (integers). 

        - Expected type: integer
        - Default value: None

|

- clusters: cluster or partitions where ChemLG will be executed during the library generator module. 

        - Expected type: string cluster/partition, whichever applicable or "run locally"
        - Default value: None

|



job generator module:

        -called by --generatejobs parser argument 
        
We have made a separate guide as to how an input file is created from a template.

.. toctree::
   :maxdepth: 4
   :caption: Template Guide

   chemhtps.template

- library_in: Specify the library of molecules to run jobs for. 

        - Expected type: string library-name from within ./screeninglib folder
        - Default value: None

|

- job_type: Specify the class of jobs regarding their resource-expenses. 

        - Expected type: "short" or "long" strings, depending on whether the jobs will take short or long times
        - Default value: None

|

- program: Specify the program that jobs will be run for and kind of template-files that will be called. 

        - Expected type: "QCHEM" or "ORCA", string
        - Default value: None

|

- template: Specify the template file that we used to generate job-files from. 

        - Expected type: string, the file location within "./job_templates/$program/" folder
        - Default value: None

|



job feeder module:

        - called by --feedjobs parser argument 

- feed_local: Specify whether the jobs will be submitted remotely or from within the local node. 

        - Expected type: string, "TRUE" or "FALSE"
        - Default value: None

|

- job_sched: Specify the job-scheduler to be used. 

        - Expected type: string
        - Default value: "SLURM"


Along with this guide about how the config-file options operate, please do check out a short tutorial we have compiled at:

.. toctree::
   :maxdepth: 4
   :caption: Project Tutorial

   chemhtps.tutorial


