import setuptools
from os import path
import chemhtps

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

if __name__ == "__main__":
    setuptools.setup(
        name='chemhtps',
        version=chemhtps.__version__,
        author='Yudhajit Pal, William Evangelista, Johannes Hachmann',
        author_email='yudhajit@buffalo.edu, hachmann@buffalo.edu',
        # url='https://github.com/hachmannlab/chemml',
        project_urls={
            'Source': 'https://github.com/hachmannlab/chemhtps',
            'url': 'https://hachmannlab.github.io/chemhtps/'
        },
        description=
        'A General Purpose Computational Chemistry High-Throughput Screening Platform',
        long_description=long_description,
        scripts=['lib/chemhtpsshell'],
        keywords=[
            'Data Mining', 'Quantum Chemistry',
            'Materials Science', 'Drug Discovery'
        ],
        license='BSD-3C',
        packages=setuptools.find_packages(),

        install_requires=[
            'future', 'six', 'numpy',
            'chemlg'
        ],
        extras_require={
            'docs': [
                'sphinx',
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
                'numpydoc',
                'nbsphinx'
            ],
            'tests': [
                'pytest', #==3.10
                'pytest-cov',
                'pytest-pep8',
                'tox',
            ],
        },
        tests_require=[
            'pytest',
            'pytest-cov',
            'pytest-pep8',
            'tox',
        ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Natural Language :: English',
            'Intended Audience :: Science/Research',
            # 'Programming Language :: Python :: 2.7',
            # 'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
        zip_safe=False,
    )