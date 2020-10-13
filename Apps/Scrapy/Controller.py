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
import sys
import re
import os
import copy
import json
import urllib
import requests
import validators
import datetime
import time

# ___________________________________________________
# extension python libraries
# ___________________________________________________
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

# ___________________________________________________
# developed python libraries
# ___________________________________________________
import config
assert config
from Apps.Scrapy.model import Gallery
from Apps.Scrapy.model import Paint
from Lib.Recovery.content import Page as Page
assert Gallery
assert Paint

"""
The controller mediates between the view and the model, there are
some operations implemented in this class, specially the load and save
functions as well as functions to merge the results from different
elements in the models or various models.
"""

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

class Controller (object):
    """[summary]

    Args:
        object ([type]): [description]

    Raises:
        Exception: [description]

    Returns:
        [type]: [description]
    """

    galleryWEB = str()
    localGallery = str()
    modelStruct = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
    galleryModel = Gallery()
    maxPaints = DEFAULT_MAX_PAINTS

    def __init__(self, *args, **kwargs):
        """[summary]

        Args:
            galleryWEB ([type]): [description]
            localGallery ([type]): [description]
            modelStruct ([type]): [description]
            galleryModel ([type]): [description]
            maxPaints ([type]): [description]
        """

        try:

            # Controller default values
            self.galleryWEB = str()
            self.localGallery = str()
            self.modelStruct = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
            self.galleryModel = Gallery()
            self.currentPage = Page()
            self.maxPaints = DEFAULT_MAX_PAINTS

            # when arguments are pass as parameters
            if len(args) > 0:

                for i in range(int(len(args))-1):

                    # URL of the remote gallery to scrap
                    if i == 0:
                        self.galleryWEB = args[i]

                    # local dirpath to save the gallery CSV
                    if i == 1:
                        self.localGallery = args[i]

                    # list of paintings containing the in memory data of the gallery
                    if i == 2:
                        self.galleryModel = args[i]

            # if there are dict decrators in the creator
            if len(kwargs) > 0:

                for key in list(kwargs.keys()):

                    # updating schema in the controller
                    if key == "schema":
                        self.paintStruct = copy.deepcopy(kwargs[key])

                    # setting the max size of the gallery
                    if key == "size":
                        self.maxPaints = kwargs[key]

        # exception handling
        except Exception as exp:
            raise exp

    def SetUpLocal(self, galleryFolder, *args):
        """[summary]

        Args:
            galleryFolder ([type]): [description]

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """
        try:
            # Make sure the local gallery path exists and is correct
            if not os.path.exists(galleryFolder):

                raise Exception
            
            # the local path exists and is correct
            elif os.path.exists(galleryFolder):

                # integratnig subfoders in the realpath
                workPath = galleryFolder

                if len(args) > 0:

                    for i in range(int(len(args))):
                        workPath = os.path.join(workPath, args[i])
    
                # creating appropiate subfoders
                if not os.path.exists(workPath):

                    os.makedirs(workPath)
                
                self.galleryFolder = workPath
                return workPath

        # exception handling
        except Exception as exp:
            raise exp

    def updateLocal(self, galleryFolder, *args):

        try:
            pass

        # exception handling
        except Exception as exp:
            raise exp

    def scrapIndex(self, galleryUrl, sleepTime, scrapDivision, scrapAttributes):
        """[summary]

        Args:
            galleryUrl ([type]): [description]
            scrapDivision ([type]): [description]
            scrapAttributes ([type]): [description]
            sleepTime ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:

            self.currentPage = Page()
            self.currentPage.getCollection(galleryUrl, sleepTime)
            answer = self.currentPage.findInBody(scrapDivision, attributes=scrapAttributes)

            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def scrapAgain(self, scrapDivision, scrapAttributes):
        """[summary]

        Args:
            scrapDivision ([type]): [description]
            scrapAttributes ([type]): [description]

        Returns:
            [type]: [description]
        """
        answer = self.currentPage.findInBody(scrapDivision, attributes=scrapAttributes)
        return answer

    def getID(self, gallerySoup, idElement):
        """[summary]

        Args:
            gallerySoup ([type]): [description]
            idElement ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:
            answer = list()

            for element in gallerySoup:
                
                tid = element.get(idElement).replace("/en/collection/", "")
                answer.append(tid)

            return answer

            # exception handling
        except Exception as exp:
            raise exp

    def getTitle(self, gallerySoup, titleElement):
        """[summary]

        Args:
            gallerySoup ([type]): [description]
            titleElement ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:
            answer = list()

            for element in gallerySoup:

                ttitle = element.get(titleElement)
                answer.append(ttitle)

            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def getURL(self, gallerySoup, rootURL, urlElement):
        """[summary]

        Args:
            gallerySoup ([type]): [description]
            rootURL ([type]): [description]
            urlElement ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:
            answer = list()

            for title in gallerySoup:

                turl = urllib.parse.urljoin(rootURL, title.get(urlElement))
                answer.append(turl)

            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def saveGallery(self, galleryFilePath, **kwargs):
        try:
            pass

            # exception handling
        except Exception as exp:
            raise exp

    def loadGallery(self, galleryFilePath, **kwargs):
        try:
            pass

            # exception handling
        except Exception as exp:
            raise exp
