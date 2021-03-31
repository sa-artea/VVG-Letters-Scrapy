# =========================================
# Standard library imports
# =========================================
# import configparser
import os
import sys
import configparser

"""
workaround the relative explicit import limitations and altering the sys.path
# Keep checking the '../..' parameter to go further into the app path
"""
file_path = os.path.join(os.path.dirname(__file__), '..')
file_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(file_path))
data_dir = os.path.join(file_dir, 'Data')


def configGlobal(*args, **kwargs):
    """
    Read a INI file to load the configuration into the program

    Returns:
        cfgData (configparser): loaded configuration to execute the app
    """

    cfgfp = os.path.join(*args)
    cfgData = configparser.ConfigParser()
    cfgData.read(cfgfp, encoding="utf-8")
    return cfgData

# config = configparser.ConfigParser()
# with open('example.ini', 'w', encoding="utf-8") as configfile:
#     config.write(configfile)
