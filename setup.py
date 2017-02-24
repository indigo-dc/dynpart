from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='partition_director',
      version='0.1',
      description='Partition Director of batch and cloud resources',
      long_description=readme(),
      url='https://github.com/indigo-dc/dynpart',
      author='Sonia Taneja, Stefano Dal Pra',
      author_email='sonia.taneja@cnaf.infn.it',
      license='Apache-2',
      packages=find_packages(),
      zip_safe=False)
