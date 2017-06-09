"""
Module for carto-python exceptions definitions

.. module:: carto.exceptions
   :platform: Unix, Windows
   :synopsis: Module for carto-python exceptions definitions

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""


class CartoException(Exception):
    """
    Any Exception produced by carto-python should be wrapped around this class
    """
    pass
