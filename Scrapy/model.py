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
from ..Lib.Recovery.Pages import page as page
from ..Lib.Utils import error as error
assert page
assert error

soupCol = [
    "ID",  # identificador unico de la galeria, tambien es el nombre del folder dentro del directorio local
    "NAME",  # nombre del elemento en la galeria
    "ELEMENT_URL",  # enlace del elemento recuperado del ScrapyWEB
    "DOWNLOAD_URL",  # enlace de la imagen dentro del elemento de la galeria

    "HAS_ID",  # booleano que identifica si se tiene un folder local del elemento
    "HAS_NAME",  # booleano que identifica si se tiene el nombre del elemento

    # booleano que identifica si se tiene la seccion de descripcion en el HTML del elemento
    "HAS_DESCRIPTION",
    "HAS_DOWNLOAD",  # booleano que identifica si se tiene la seccion de enlace de descarga en el HTML del elemento
    "HAS_TAGS",  # booleano que identifica si se tiene la seccion de tags de busqueda en el HTML del elemento
    "HAS_DATA",  # booleano que identifica si se tiene la seccion de datos de archivo en el HTML del elemento
    "HAS_RELATEDW",  # booleano que identifica si se tiene la seccion de trabajo relacionado en el HTML del elemento

    "ERR_ID",  # si no se puede crear la carpeta con el ID se guarda el error aca
    "ERR_NAME",  # si no se obtiene el nombre se guarda el error aca

    "ERR_DESCRIPTION",  # si no se obtiene la descripcion se guarda el error aca
    "ERR_DOWNLOAD",  # si no se obtiene el enlace de descarga se guarda el error aca
    "ERR_TAGS",  # si no se obtiene los tags de busqueda se guarda el error aca
    "ERR_DATA",  # si no se obtiene los datos de archivo se guarda el error aca
    "ERR_RELATEDW",  # si no se obtiene el trabajo relacionado se guarda el error aca

    "DESCRIPTION",  # aqui guardo el JSON con la informacion de la descripcion
    "TAGS",  # aqui guardo el JSON con la informacion de los tags de busqueda
    "DATA",  # aqui guardo el JSON con la informacion de los datos de coleccion
    "RELATEDW",  # aqui guardo el JSON con la informacion del trabajo relacionado con cada una de las obras
]

# default template for the element/paint dict in gallery
DEFAULT_DATA_TEMPLATE = {
    "ID": str(),                # unique ID for an element in the gallery, its also its folder name in the localdir
    "NAME": str(),              # name of the element inside the gallery
    "PAINT_URL": str(),         # element (paint) URL/link recovered with ScrapyWEB
    "HAS_ID": bool(),           # boolean indicating if the paint has a folder on the localdir
    "HAS_NAME": bool(),         # boolean indicating if the paint has a name in the gallery
    }

# -----------------------------------------------------
# API for the scrapping the gallery of paintings
# -----------------------------------------------------
class gallery(object):
    """
    this class implement the gallery of the model, containing all its elements (ie.: painintgs)
    contains all gallery data in memory and helps create the dataFrame for it.
    """

    #___________________________________________
    # class parameters
    #___________________________________________
    galleryUrl = str()
    dataTemplate = copy.deepcopy(DEFAULT_DATA_TEMPLATE)
    gallerySize = 10
    currentPaint = 0
    galleryList = list()

    # =========================================
    # functions to create a new gallery
    # =========================================

    def __init__(self, *args, **kwargs):
        """
        creator of the class gallery()

        Args:
            galleryUrl (str, optional): url of the page I want to recover. Defaults to str().
            dataTemplate (dic, optional): dictionary for the data template of the elements in the gallery.
            gallerySize (int, optional): size of the gallery, len of the galleryList. Default to 10.
            currentPaint (int, optional): index of the working element in gallery, usefull when a gallery is created with elements. Default to 0.
            galleryList (list, optional): list of elements (ie.: paintings) in the gallery, you can pass an existing list to the creator. Default to list()
        """
        try:
            
            # default creator
            # not passing parameters in the creator
            self.galleryUrl = str()
            self.dataTemplate = copy.deepcopy(DEFAULT_DATA_TEMPLATE)
            self.gallerySize = 10
            self.currentPaint = 0
            self.galleryList = list()

            # if parameters are passed
            if len(args) > 0:

                # url passed as creator parameter
                if len(args) == 1:

                    self.galleryUrl = args[0]
                    self.dataTemplate = copy.deepcopy(DEFAULT_DATA_TEMPLATE)
                    self.gallerySize = 10
                    self.currentPaint = 0
                    self.galleryList = list()

                # url and size passed as creator parameter
                elif len(args) == 2:

                    self.galleryUrl = args[0]
                    self.dataTemplate = copy.deepcopy(DEFAULT_DATA_TEMPLATE)
                    self.gallerySize = args[1]
                    self.currentPaint = 0
                    self.galleryList = list()

                # url, size and an existing gallery passed as creator parameter
                elif len(args) == 4:

                    self.galleryUrl = args[0]
                    self.dataTemplate = copy.deepcopy(DEFAULT_DATA_TEMPLATE)
                    self.gallerySize = args[1]
                    self.currentPaint = args[2]
                    self.galleryList = args[3]

            # if there is more than 4 parameters or 3 we raise error
            elif len(args) > 4 or len(args) == 3:

                raise Exception
            
            # if decorators are passed
            if len(kwargs) > 0:

                # setting costume template
                if kwargs.get("data_template"):

                    self.dialect = kwargs["data_template"]

                # no other decorator is available
                else:
                    raise Exception

        except Exception as exp:
            error.reraise(exp, 'gallery->gallery(): ')

    def openGallery(self, *args, **kwargs):

        try:
            pass

        except Exception as exp:
            error.reraise(exp, 'gallery->openGallery: ')


    # =========================================
    # consult functions
    # =========================================

    def getPaint(self, index):

        try:

            answer = self.galleryList[index]
            answer = copy.deepcopy(answer)
            return answer

        except Exception as exp:
            error.reraise(exp, 'gallery->getPaint: ')

    def lastPaint(self):

        try:

            answer = self.galleryList[len(self.galleryList)-1]
            answer = copy.deepcopy(answer)
            return answer

        except Exception as exp:
            error.reraise(exp, 'gallery->lastPaint: ')

    def firstPaint(self):
        try:

            answer = self.galleryList[0]
            answer = copy.deepcopy(answer)
            return answer

        except Exception as exp:
            error.reraise(exp, 'gallery->firstPaint: ')

    # =========================================
    # update functions
    # =========================================

    def updatePaint(self, parameter_list):
        try:
            pass

        except Exception as exp:
            error.reraise(exp, 'gallery->updatePaint: ')

    def appendPaint(self, paint):

        try:

            self.galleryList.append(paint)
            self.gallerySize = len(self.galleryList)
            self.currentPaint = self.gallerySize-1

        except Exception as exp:
            error.reraise(exp, 'gallery->appendPaint: ')

    # =========================================
    # compare functions
    # =========================================

    def findPaints(self, parameter_list):
        try:
            pass

        except Exception as exp:
            error.reraise(exp, 'gallery->findPaints: ')

    def cmpPaints(self, parameter_list):
        try:
            pass

        except Exception as exp:
            error.reraise(exp, 'gallery->cmpPaints: ')

# -----------------------------------------------------
# API for the scrapping element (paintings) in the WEB
# -----------------------------------------------------
class paint(object):
    pass
