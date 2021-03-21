# =========================================
# Standard library imports
# =========================================
# import configparser
import os
import sys

"""
workaround the relative explicit import limitations and altering the sys.path
# Keep checking the '../..' parameter to go further into the app path
"""
file_path = os.path.join(os.path.dirname(__file__), '..')
file_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(file_path))
data_dir = os.path.join(file_dir, 'Data')

# config = configparser.ConfigParser()
# with open('example.ini', 'w', encoding="utf-8") as configfile:
#     config.write(configfile)
