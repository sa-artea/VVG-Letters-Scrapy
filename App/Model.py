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
import os
import copy

# ___________________________________________________
# extension python libraries
# ___________________________________________________
import pandas as pd
import cv2

# ___________________________________________________
# developed python libraries
# ___________________________________________________
import Config
from Lib.Utils import Error as Error
from Lib.Recovery.Content import Page
assert Page
assert Error
assert Config

# default template for the element/paint dict in gallery
DEFAULT_FRAME_SCHEMA = [
    # ID element in the gallery and local folder name
    "ID",

    # tittle of the element in the gallery
    "TITLE",

    # recovered element (paint) URL
    "COLLECTION_URL",

    # direct image URL/link for the image in the gallery
    "DOWNLOAD_URL",

    # boolean if there is a picture file in the local folder
    "HAS_PICTURE",

    # JSON with the description of the element
    "DESCRIPTION",

    # JSON with the collection tags of the element
    "SEARCH_TAGS",

    # JSON with the museum object data of the element
    "OBJ_DATA",

    # JSON with the related work text and URLs of the element
    "RELATED_WORKS",

    # numpy RGW matrix created from original image
    "IMG_DATA",
]


# -----------------------------------------------------
# API for the scrapping the gallery of paintings
# -----------------------------------------------------
class Gallery(object):
    """
    this class implement the gallery of the model, containing all its elements
    (ie.: painintgs) contains all gallery data in memory and helps create the
    dataFrame for it.
    """

    # =========================================
    # class variables
    # =========================================

    webGallery = str()
    galleryPath = str()
    schema = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
    dataFrame = pd.DataFrame(columns=DEFAULT_FRAME_SCHEMA)

    # =========================================
    # functions to create a new gallery
    # =========================================
    def __init__(self, *args, **kwargs):
        """
        creator of the class gallery()

        Args:
            webGallery (str, optional): url of the page I want to recover.
            Defaults to str().
            galleryPath ([type]): [description]
            schema (list, optional): dictionary for the data template of the
            elements in the gallery.
            dataFrame (dataFrame, optional): element dataframe (ie.: paintings)
            in the gallery, you can pass an existing df to the creator. Default
            is empty.

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            Model (Model): return a new Model() object
        """
        try:

            # default creator attributes
            self.webGallery = str()
            self.galleryPath = str()
            self.schema = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
            self.dataFrame = pd.DataFrame(columns=DEFAULT_FRAME_SCHEMA)

            # when arguments are pass as parameters
            if len(args) > 0:
                for arg in args:
                    # URL of the remote gallery to scrap
                    if args.index(arg) == 0:
                        self.webGallery = arg

                    # local dirpath to save the gallery CSV
                    if args.index(arg) == 1:
                        self.galleryPath = arg

                    # dataframes containing the data of the gallery
                    if args.index(arg) == 2:
                        self.dataFrame = arg

            # if there are dict decrators in the creator
            if len(kwargs) > 0:

                for key in list(kwargs.keys()):

                    # updating schema in the model
                    if key == "schema":
                        self.schema = copy.deepcopy(kwargs[key])

        # exception handling
        except Exception as exp:
            raise exp

    def createNewIndex(self, cols, data):
        """
        creates a new dataframe in the model based on the columns
        names and new data.

        Args:
            columns (list): list of names of the columns you want to add in the
            dataframe
            data (list:list or pandas/numpy matrix): data of each column you
            want to add in the dataframe

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dataframe.info()): new pandas dataframe description
        """
        try:
            # self.schema = cols
            self.dataFrame = pd.DataFrame(columns=self.schema)

            for col, td in zip(cols, data):

                self.dataFrame[col] = td

            ans = self.dataFrame.info()
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def updateData(self, column, data):
        """
        updates a single column with new data, the size of the data needs to be
        the same as the existing records

        Args:
            column (str): name of the column in the dataframe to update
            data (list/np.array): dataframe of the data to update

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dataframe.info()): updated pandas dataframe description
        """
        try:
            self.dataFrame[column] = data
            ans = self.dataFrame.info()
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    # =========================================
    # consult functions
    # =========================================
    def getData(self, column, *args, **kwargs):
        """
        gets the data from a given column name, returning a list

        Args:
            column (str): name of the column in the dataframe to update

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): formated copy of the data in the dataframe
        """
        try:

            ans = copy.deepcopy(self.dataFrame[column])
            ans = list(ans)
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def checkGallery(self):
        """
        checks the state of the model's dataframe

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dataframe.info()): pandas dataframe description
        """
        try:
            ans = self.dataFrame.info()
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getColData(self, column):

        try:

            ans = list(self.dataFrame[column])
            return ans

        except Exception as exp:
            raise exp

    # =========================================
    # update functions
    # =========================================
    def updateIndex(self, column, data):
        """
        updates a single column according to its index/name in the dataframe

        Args:
            column (str): column name in the dataframe
            data (list): list with the updated data for the pandas dataframe,
            needs to have the same size of the original

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dataframe.info()): pandas dataframe description
        """
        try:

            self.dataFrame[column] = data
            ans = self.dataFrame.info()
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    # =========================================
    # I/O functions
    # =========================================

    def saveGallery(self, fileName, dataFolder):
        """
        save the in memory dataframe into a CSV file with UTF-8 encoding

        Args:
            fileName (str): file's name with .csv extension
            dataFolder (file-object): valid dirpath str or an array with valid
            folders.

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
        """
        loads the gallery from a CSV file in UTF-8 encoding

        Args:
            fileName (str): file's name with .csv extension
            dataFolder (file-object): valid dirpath str or an array with valid
            folders.

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

    def imgToData(self, fname, fn, *args, **kwargs):
        """
        open the image file and creates an unaltered numpyarray from it

        Args:
            fname (str): image file root folder location
            fn (str): image's file name with extension ie.: .jpg

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (np.array): image's numpy data matrix
        """
        try:
            ans = None
            # joining folder name and filename
            imgfn = os.path.join(fname, fn)
            # reading all data from image

            ans = cv2.imread(imgfn, cv2.IMREAD_UNCHANGED)
            # ans = cv2.cvtColor(ans, cv2.COLOR_RGB2RGBA)
            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp
