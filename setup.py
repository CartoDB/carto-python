
from distutils.core import setup

setup(name='cartodb', 
      author = 'Javi Santana', 
      author_email = 'jsantfer@gmail.com',
      description = 'client to access cartodb api',
      url='https://github.com/javisantana/cartodb',
      version='0.1',
      packages=['cartodb'],
      requires = ['oauth']
)
