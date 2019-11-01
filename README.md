Welcome to ChemHTPS's documentation!
====================================

ChemHTPS is a program suite to for conducting high-throughput computational screenings and generating chemical-modeling data.

source repository on github: (https://github.com/hachmannlab/chemhtps)

Program Version: 0.1

## Code Design:
ChemHTPS is developed in the Python 3 programming language and makes use of a host of domain-specific libraries.
The code structure is modular and has an object-oriented design to make it flexible and versatile for diverse project-specific needs.

We recommend running ChemHTPS with ChemLG for in-silico molecule generation. For this, OpenBabel and its Python extension, Pybel is required.
Additional ChemLG requirements include MPI4PY for its parallel implementation. Hence OpenBabel and MPI4PY are also, by extension, dependencies of ChemHTPS.

## Documentation:
ChemHTPS documentation can be found here (https://chemhtps.readthedocs.io/en/latest/)

## Installation and Dependencies:
You can download ChemHTPS from Python Package Index (PyPI) via pip. We also recommend that a virtual environment is used to run ChemHTPS to allow it to interface with ChemLG.

    conda create --name my_chemeco_env python=3.6
    source activate my_chemeco_env
    conda install -c openbabel openbabel
    conda install -c anaconda mpi4py
    pip install chemhtps
    optional: pip install chemlg 


You can test the installation with:

    pytest -v


## Citation:
Please cite the use of ChemHTPS as:


    Main citation:

    @article{chemhtps2019,
    author = {Pal, Yudhajit and Evangelista, William and Afzal, Mohammed Atif Faiz and Haghighatlari, Mojtaba and Hachmann, Johannes},
    journal = {},
    pages = {},
    title = {ChemHTPS - A General Purpose Computational Chemistry High-Throughput Screening Platform},
    doi = {},
    year = {2019}
    }


    Other references:

    @article{Hachmann2018,
    author = {Hachmann, Johannes and Afzal, Mohammad Atif Faiz and Haghighatlari, Mojtaba and Pal, Yudhajit},
    doi = {10.1080/08927022.2018.1471692},
    issn = {10290435},
    journal = {Molecular Simulation},
    number = {11},
    pages = {921--929},
    title = {Building and deploying a cyberinfrastructure for the data-driven design of chemical systems and the exploration of chemical space},
    volume = {44},
    year = {2018}
    }



## About us:

Maintainers:
    - Johannes Hachmann, hachmann@buffalo.edu
    - Yudhajit Pal
      University at Buffalo - The State University of New York (UB)

Contributors:
    - William Evangelista (UB): base-code and starting conceptualization
    - Mojtaba Haghighatlari (UB): scientific advice and software mentor
    - Gaurav Vishwakarma (UB): library generator module
    - Mohammad Atif Faiz Afzal (UB): library generator module

We encourage any contributions and feedback. Feel free to fork and make pull-request to the "development" branch.


## Acknowledgements:
    - ChemHTPS is based upon work supported by the U.S. National Science Foundation under grant #OAC-1751161.
    - ChemHTPS was also supported by start-up funds provided by UB's School of Engineering and Applied Science and UB's Department of Chemical and Biological Engineering, the New York State Center of Excellence in Materials Informatics through seed grant #1140384-8-75163, and the U.S. Department of Energy under grant #DE-SC0017193.


## License:
ChemHTPS is copyright (C) 2014-2019 Johannes Hachmann and Yudhajit Pal, all rights reserved.
ChemHTPS is distributed under 3-Clause BSD License (https://opensource.org/licenses/BSD-3-Clause).
