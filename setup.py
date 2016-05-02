from setuptools import setup, find_packages

setup(name='episode-miner',
      description = "Finds frequent episodes in event sequence.",
      version='1.0.0',
      #py_modules=['test1'],
      install_requires = ['estnltk'],
      author = 'Paul Tammo',
      author_email='paul.tammo@gmail.com',
      packages = find_packages(),
      license='GNU GPL version 2',
      #entry_points = {
      #  'console_scripts': [
      #    'transform_vocabulary=lexicon_deidentifier.scripts.transform_vocabulary:main',]}
)