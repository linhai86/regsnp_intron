##Prerequisites
*ANNOVAR (>= 2016Feb01)*
Follow the instructions at <http://annovar.openbioinformatics.org/en/latest> to install, and prepare Ensembl gene annotation.
```bash
tar -xf annovar.latest.tar.gz
cd annovar
perl annotate_variation.pl -downdb -buildver hg19 -webfrom annovar ensGene humandb/
```
*BEDTools (>= 2.25.0)*
Follow the instructions at <http://bedtools.readthedocs.io/en/latest> install, and make sure the programs are in your PATH.

*Python (>= 2.7.11)*
Python 3 is not currently supported.

The following Python libraries are also required. Installing libraries such as Numpy and Scipy can be a little difficult for inexperienced users. We highly recommend installing [Anaconda](https://docs.continuum.io/anaconda). Anaconda conveniently installs Python and other commonly used packages for scientific computing and data science.
* Numpy (>= 1.10.4),
* Scipy (>= 0.17.0),
* Pandas (>= 0.17.1),
* Scikit-learn (>= 0.17),

*bx-python (0.7.3)*
```bash
pip install bx-python
```
*pysam (>= 0.8.4)*
```bash
pip install pysam
```
*pybedtools (>= 0.7.6)*
```bash
pip install pybedtools
```

##Installation

##Configuration


