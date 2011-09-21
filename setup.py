
from distutils.core import setup

setup(name='cartodb', 
      author = 'Javi Santana', 
      author_email = 'jsantana@vizzuality.com',
      description = 'client to access cartodb api',
      url='https://github.com/javisantana/cartodb',
      version='0.2',
      packages=['cartodb'],
      requires = ['oauth2', 'simplejson']
)
