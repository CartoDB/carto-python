
#from distutils.core import setup
from setuptools import setup
import sys

REQUIRES = ['oauth2']
if sys.version_info < (2 , 6):
    REQUIRES.append('simplejson')

setup(name='cartodb', 
      author = 'Javi Santana',
      author_email = 'jsantana@vizzuality.com',
      description = 'client to access cartodb api',
      version='0.8.1',
      url='https://github.com/Vizzuality/cartodb',
      install_requires=REQUIRES,
      packages=['cartodb'],
      requires = REQUIRES,
      test_suite='test.client'
)
