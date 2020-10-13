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
import config
from Lib.Utils import error as error
from Lib.Recovery.content import Page
assert Page
assert error
assert config

# default template for the element/paint dict in gallery
DEFAULT_FRAME_SCHEMA = [
    "ID",                   # unique ID for an element in the gallery, its also its folder name in the localdir
    "TITLE",                # tittle of the element inside the gallery
    "PAINT_URL",            # element (paint) URL/link recovered with ScrapyWEB
    "DOWNLOAD_URL",         # direct image URL/link for the image in the gallery
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
    localGallery = list()
    modelStruct = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
    gallerySize = DEFAULT_MAX_PAINTS
    currentPaint = 0
    GallerydataFrame = pd.DataFrame(columns=DEFAULT_FRAME_SCHEMA)

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
            GallerydataFrame (dataFrame, optional): element dataframe (ie.: paintings) in the gallery, you can pass an existing df to the creator. Default is empty
        """
        try:
            
            # default creator
            # not passing parameters in the creator
            self.galleryWEB = str()
            self.localGallery = str()
            self.modelStruct = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
            self.gallerySize = DEFAULT_MAX_PAINTS
            self.currentPaint = 0
            self.GallerydataFrame = pd.DataFrame(columns=DEFAULT_FRAME_SCHEMA)

            # when arguments are pass as parameters
            if len(args) > 0:

                for i in range(int(len(args))-1):

                    # URL of the remote gallery to scrap
                    if i == 0:
                        self.galleryWEB = args[i]

                    # local dirpath to save the gallery CSV
                    if i == 1:
                        self.localGallery = args[i]

                    # paintings dataframes containing the in memory data of the gallery
                    if i == 2:
                        self.GallerydataFrame = args[i]

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

    def openGallery(self, *args, **kwargs):

        try:
            pass

        # exception handling
        except Exception as exp:
            raise exp


    # =========================================
    # consult functions
    # =========================================

    def getPaint(self, index):

        try:

            answer = self.galleryList[index]
            answer = copy.deepcopy(answer)
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def lastPaint(self):

        try:

            answer = self.galleryList[len(self.galleryList)-1]
            answer = copy.deepcopy(answer)
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def firstPaint(self):
        try:

            answer = self.galleryList[0]
            answer = copy.deepcopy(answer)
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    # =========================================
    # update functions
    # =========================================

    def updatePaint(self, parameter_list):
        try:
            pass

        # exception handling
        except Exception as exp:
            raise exp

    def appendPaint(self, paint):

        try:

            self.galleryList.append(paint)
            self.gallerySize = len(self.galleryList)
            self.currentPaint = self.gallerySize-1

        # exception handling
        except Exception as exp:
            raise exp

    # =========================================
    # compare functions
    # =========================================

    def findPaints(self, parameter_list):
        try:
            pass

        # exception handling
        except Exception as exp:
            raise exp

    def cmpPaints(self, parameter_list):
        try:
            pass

        # exception handling
        except Exception as exp:
            raise exp

# -----------------------------------------------------
# API for the scrapping element (paintings) in the WEB
# -----------------------------------------------------
class Paint(object):
    pass
