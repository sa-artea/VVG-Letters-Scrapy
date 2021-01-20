"""
* Copyright 2020, Maestria de Humanidades Digitales, 
* Universidad de Los Andes
*
* Developed for the Msc graduation project in Digital Humanities
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# ___________________________________________________
# native python libraries
# ___________________________________________________
# from Apps.Scrapy.controller import DEFAULT_FRAME_SCHEMA
import re
import os
import sys
import copy
import json
import urllib
import datetime
from urllib.parse import urlparse

# ___________________________________________________
# extension python libraries
# ___________________________________________________
import requests
import validators
from bs4 import BeautifulSoup as bs4
import numpy as np
import pandas as pd

# ___________________________________________________
# developed python libraries
# ___________________________________________________
# from .Lib.Recovery.Content import Page as page
import Config
from Lib.Utils import Error as Error
from Lib.Recovery.Content import Page
assert Page
assert Error
assert Config

# default template for the element/paint dict in gallery
DEFAULT_FRAME_SCHEMA = [
    "ID",                   # unique ID for an element in the gallery, its also its folder name in the localdir
    "TITLE",                # tittle of the element inside the gallery
    "COLLECTION_URL",       # element (paint) URL/link recovered with ScrapyWEB
    "DOWNLOAD_URL",         # direct image URL/link for the image in the gallery
    "HAS_PICTURE",          # boolean data to identify if there is a picture file in the local folder, based on DOWNLOAD_URL
    "DESCRIPTION",          # JSON cell with the description of the element in the gallery
    "SEARCH_TAGS",          # JSON cell with the collection tags of the element in the gallery
    "OBJ_DATA",             # JSON cell with the museum object data of the element in the gallery
    "RELATED_WORKS",        # JSON cell with the related work text and URLs of the element in the gallery
    "EXHIBITIONS",          # JSON cell with the list of the exhibitions were the element in the gallery has been displayed
    "LITERATURE",           # JSON cell with the list of the literatire references for the gallery elements
]

# default number of paintings in the gallery
DEFAULT_MAX_PAINTS = 10

# -----------------------------------------------------
# API for the scrapping the gallery of paintings
# -----------------------------------------------------
class Gallery(object):
    """
    this class implement the gallery of the model, containing all its elements (ie.: painintgs)
    contains all gallery data in memory and helps create the dataFrame for it.
    """

    #___________________________________________
    # class parameters
    #___________________________________________
    galleryWEB = str()
    localGallery = str()
    modelStruct = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
    gallerySize = DEFAULT_MAX_PAINTS
    currentPaint = 0
    dataFrame = pd.DataFrame(columns=DEFAULT_FRAME_SCHEMA)

    # =========================================
    # functions to create a new gallery
    # =========================================

    def __init__(self, *args, **kwargs):
        """
        creator of the class gallery()

        Args:
            galleryWEB (str, optional): url of the page I want to recover. Defaults to str().
            localGallery ([type]): [description]
            modelStruct (list, optional): dictionary for the data template of the elements in the gallery.
            gallerySize (int, optional): size of the gallery, len of the galleryList. Default to 10.
            currentPaint (int, optional): index of the working element in gallery, usefull when a gallery is created with elements. Default to 0.
            dataFrame (dataFrame, optional): element dataframe (ie.: paintings) in the gallery, you can pass an existing df to the creator. Default is empty

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            [Model]: return a new model object
        """
        try:
            
            # default creator
            # not passing parameters in the creator
            self.galleryWEB = str()
            self.localGallery = str()
            self.modelStruct = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
            self.currentPaint = 0
            self.gallerySize = DEFAULT_MAX_PAINTS
            self.dataFrame = pd.DataFrame(columns=DEFAULT_FRAME_SCHEMA)

            # when arguments are pass as parameters
            if len(args) > 0:
                i = 0
                for i in range(int(len(args))):
                    # URL of the remote gallery to scrap
                    if i == 0:
                        self.galleryWEB = args[i]

                    # local dirpath to save the gallery CSV
                    if i == 1:
                        self.localGallery = args[i]

                    # paintings dataframes containing the in memory data of the gallery
                    if i == 2:
                        self.dataFrame = args[i]

                    # the current painting in the dataframe to process
                    if i == 3:
                        self.currentPaint = args[i]

            # if there are dict decrators in the creator
            if len(kwargs) > 0:

                for key in list(kwargs.keys()):

                    # updating schema in the model
                    if key == "schema":
                        self.modelStruct = copy.deepcopy(kwargs[key])

                    # setting the max size of the gallery
                    if key == "size":
                        self.maxPaints = kwargs[key]

        # exception handling
        except Exception as exp:
            raise exp

    def createNewIndex(self, columns, data):
        """this function creates a new dataframe in the model based on the columns names and new data.

        Args:
            columns (list): list of names of the columns you want to add in the dataframe
            data (list:list or pandas/numpy matrix): data of each column you want to add in the dataframe

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            [dataframe.info()]: return the pandas description of the new dataframe
        """
        try:
            self.dataFrame = pd.DataFrame(columns=self.modelStruct)

            for col, td in zip(columns, data):

                self.dataFrame[col] = td
            
            answer = self.dataFrame.info()
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def updateData(self, column, data):
        """this function updates a single column with new data

        Args:
            column (str): [description]
            data ([type]): [description]

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            [type]: [description]
        """
        try:
            self.dataFrame[column] = data
            answer = self.dataFrame.info()
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    # =========================================
    # consult functions 
    # =========================================
    def getData(self, column, *args, **kwargs):
        """[summary]

        Args:
            column ([type]): [description]

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            [type]: [description]
        """
        try:

            answer = copy.deepcopy(self.dataFrame[column])
            answer = list(answer)
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def checkGallery(self):
        """[summary]

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            [type]: [description]
        """
        try:
            answer = self.dataFrame.info()
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def getColData(self, column):

        try:

            answer = list(self.dataFrame[column])
            return answer

        except Exception as exp:
            raise exp

    # =========================================
    # update functions
    # =========================================

    def updateIndex(self, column, data):
        """[summary]

        Args:
            column ([type]): [description]
            data ([type]): [description]

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            [type]: [description]
        """
        try:

            self.dataFrame[column] = data
            answer = self.dataFrame.info()
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    # =========================================
    # I/O functions
    # =========================================

    def saveGallery(self, fileName, dataFolder):
        """[summary]

        Args:
            fileName ([type]): [description]
            dataFolder ([type]): [description]

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            # pandas function to save dataframe in CSV file
            galleryFilePath = os.path.join(os.getcwd(), dataFolder, fileName)
            self.dataFrame.to_csv(galleryFilePath, sep=",",
                                  index=False, encoding="utf-8", mode="w")

        # exception handling
        except Exception as exp:
            raise exp

    def loadGallery(self, fileName, dataFolder):
        """[summary]

        Args:
            fileName ([type]): [description]
            dataFolder ([type]): [description]

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            # read an existing CSV fileto update the dataframe
            galleryFilePath = os.path.join(os.getcwd(), dataFolder, fileName)
            self.dataFrame = pd.read_csv(
                galleryFilePath, sep=",", encoding="utf-8", engine="python")

        # exception handling
        except Exception as exp:
            raise exp
