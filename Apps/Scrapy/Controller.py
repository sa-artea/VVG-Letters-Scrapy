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

# ___________________________________________________
# extension python libraries
# ___________________________________________________
import numpy as np
import pandas as pd

# ___________________________________________________
# developed python libraries
# ___________________________________________________
import config
assert config
from Apps.Scrapy.Model import Gallery
from Apps.Scrapy.Model import Paint
from Lib.Utils.error import error as error
assert Gallery
assert Paint
assert error

"""
The controller mediates between the view and the model, there are
some operations implemented in this class, specially the load and save
functions as well as functions to merge the results from different
elements in the models or various models.
"""

# default template for the element/paint dict in gallery
DEFAULT_PANDAS_FRAME = {
    # unique ID for an element in the gallery, its also its folder name in the localdir
    "ID": str(),
    "NAME": str(),              # name of the element inside the gallery
    "PAINT_URL": str(),         # element (paint) URL/link recovered with ScrapyWEB
    "HAS_ID": bool(),           # boolean indicating if the paint has a folder on the localdir
    "HAS_NAME": bool(),         # boolean indicating if the paint has a name in the gallery
}

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

    galleryHome = str()
    localGallery = str()
    gallery = list()
    paintStruct = None
    galleryFrame = None
    maxPaints = None

    def __init__(self, *args, **kwargs):
        """[summary]

        Args:
            galleryHome ([type]): [description]
            localGallery ([type]): [description]
            gallery ([type]): [description]
            paintStruct ([type]): [description]
            galleryFrame ([type]): [description]
            maxPaints ([type]): [description]
        """

        # Controller default values
        self.galleryHome = str()
        self.localGallery = str()
        self.gallery = list()
        self.paintStruct = copy.deepcopy(DEFAULT_PANDAS_FRAME)
        self.galleryFrame = pd.DataFrame(columns = DEFAULT_PANDAS_FRAME)
        self.maxPaints = DEFAULT_MAX_PAINTS

        # when arguments are pass as parameters
        if len(args) > 0:
            
            for i in range(int(len(args))):

                # URL of the remote gallery to scrap
                if i == 0:
                    self.galleryHome = args[i]

                # local dirpath to save the gallery CSV
                if i == 1:
                    self.localGallery = args[i]
                
                # list of paintings containing the in memory data of the gallery
                if i == 2:
                    self.gallery = args[i]

        # if there are dict decrators in the creator
        if len(kwargs) > 0:

            for key in list(kwargs.keys()):

                # updating schema in the controller
                if key == "schema":
                    self.paintStruct = copy.deepcopy(kwargs[key])
                    self.galleryFrame = pd.DataFrame(columns = kwargs[key])
                
                # setting the max size of the gallery
                if key == "size":
                    self.maxPaints = kwargs[key] 

    def SetUpLocal(self, galleryFolder, *args):
        """[summary]

        Args:
            galleryFolder ([type]): [description]

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """
        
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
    
    def setUpIndex(self, galleryIndex, *args):
        
        

        return False

    def loadGallery(self, galleryFilePath, **kwargs):
        pass

    def saveGallery(self, galleryFilePath, **kwargs):
        pass

    def addPaint(self, parameter_list):
        pass

# ___________________________________________________
#  Funciones para la carga de datos y almacenamiento
#  de datos en los modelos
# ___________________________________________________
