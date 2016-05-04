from setuptools import setup, find_packages

setup(name='episode-miner',
      description = "Finds frequent episodes in event sequence.",
      version='1.0.0',
      install_requires = ['pyahocorasick'],
      author = 'Paul Tammo',
      author_email='paul.tammo@gmail.com',
      packages = find_packages(),
      license='GNU GPL version 2',
)
