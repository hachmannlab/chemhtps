Job Input Files: Template Guide
===============================

Currently, ChemHTPS works with ORCA and QCHEM. Here, we discuss how the xyz information of a molecule goes into the template file to create unique input files.

ORCA:

If we have a template file as follows:

.. literalinclude:: input_templates/orca_template.inp
   :linenos:

or another example with no "xyzfile" line mentioned at all:

.. literalinclude:: input_templates/orca_template_1.inp
   :linenos:

Following is the corresponding job input file for H2O.xyz molecular file:

.. literalinclude:: input_templates/orca_inpfile.inp
   :linenos:

Similarly for QCHEM:

Template:

.. literalinclude:: input_templates/qc_template.inp
   :linenos:

Job input file:

.. literalinclude:: input_templates/qc_inpfile.inp
   :linenos:

In the case of ORCA, we can have jobs with multiple calculations re-using different .xyz files from previous calculations within the same job file. We add the molecular file information only for the first instance of the xyzfile line. For the other jobs, we trust the user to write proper ORCA template files to use the output of the first calculation: 

.. literalinclude:: input_templates/orca_template1.inp
   :linenos:

.. literalinclude:: input_templates/orca_inpfile1.inp
   :linenos:

For both QCHEM and ORCA jobs, a user can change the charge and the spin in the template file itself, (for e.g., in line 13 of the qchem template, line 2 in the first two ora template files, and line 5 in the third orca template files), and the job-generator module code will keep that as the default value for all the jobs generated. Hence, we recommend that separate calls of job-generator be done for different charge/spin combinations.


