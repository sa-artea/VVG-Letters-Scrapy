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

# ===============================
# native python libraries
# ===============================
import os
import copy
import csv

# ===============================
# extension python libraries
# ===============================
import pandas as pd
# import numpy as np
import cv2

# ===============================
# developed python libraries
# ===============================
import Conf
from Lib.Utils import Err as Err
from Lib.Recovery.Content import Page
from Lib.Recovery.Cleaner import Topic
assert Topic
assert Page
assert Err
assert Conf

# global config variables
cfgFolder = "Config"
cfgSchema = "df-schema.ini"

# loading config schema into the program
dataSchema = Conf.configGlobal(cfgFolder, cfgSchema)

# default template for the element/paint dict in gallery
DEFAULT_FRAME_SCHEMA = eval(dataSchema.get("DEFAULT", "columns"))


# ================================================
# API for the scrapping the gallery of paintings
# ================================================
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
    imagesPath = str()
    schema = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
    dataFrame = pd.DataFrame(columns=DEFAULT_FRAME_SCHEMA)
    wpage = Page()

    # =========================================
    # functions to create a new gallery
    # =========================================
    def __init__(self, *args, **kwargs):
        """
        creator of the class gallery()

        Args:
            webGallery (str): URL for the gallery to scrap data
            galleryPath (str): local dirpath for the gallery data
            schema (list): array with the column names for the model
            dataFrame (dataFrame, optional): panda df with data (ie.: paints)
            in the gallery, you can pass an existing df, Default is empty
            wpage (Page): the current webpage the controller is scrapping

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            Model (Model): return a new Model() object
        """
        try:

            # default creator attributes
            self.webGallery = str()
            self.galleryPath = str()
            self.imagesPath = str()
            self.schema = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
            self.dataFrame = pd.DataFrame(columns=DEFAULT_FRAME_SCHEMA)
            self.wpage = Page()

            # when arguments are pass as parameters
            if len(args) > 0:
                for arg in args:
                    # URL of the remote gallery to scrap
                    if args.index(arg) == 0:
                        self.webGallery = arg

                    # local dirpath to save the gallery CSV
                    if args.index(arg) == 1:
                        self.galleryPath = arg

                    # local dirpath to save the images
                    if args.index(arg) == 2:
                        self.imagesPath = arg

                    # dataframes containing the data of the gallery
                    if args.index(arg) == 3:
                        self.dataFrame = arg

            # if there are dict decrators in the creator
            if len(kwargs) > 0:

                for key in list(kwargs.keys()):

                    # updating schema in the model
                    if key == "schema":
                        self.schema = copy.deepcopy(kwargs[key])
                        self.dataFrame = pd.DataFrame(columns=self.schema)

        # exception handling
        except Exception as exp:
            raise exp

    def scrapIndex(self, galleryUrl, sleepTime, div, attrs):
        """
        Scrap the gallery index and recover all the elements in it

        Args:
            galleryUrl (str): URL for the gallery to scrap data
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine
            the search and scrap
            sleepTime (float): waiting time between requests

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bs-obj): div and attrs filtered beatifulsoup object
        """
        try:
            # reset working web page
            self.wpage = Page()
            ans = None

            # getting the basic element list from gallery online index
            self.wpage.getCollection(galleryUrl, sleepTime)
            ans = self.wpage.findInReq(div, attributes=attrs)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def scrapAgain(self, div, attrs):
        """
        Using the scrapIndex() results, scrap for new information
        to complete the dataframe index

        Args:
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bs-obj): div and attrs filtered beatifulsoup object
        """
        try:
            ans = None
            ans = self.wpage.findInReq(div, attributes=attrs)
            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def scrapElement(self, elemUrl, div, attrs, **kwargs):
        """
        controller interface to scrap elements within a link based
        on the <div>, html marks and other attributes or decoratos

        Args:
            elemUrl (str): gallery's element url
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bs-obj): HTML divs as a beatifulsoup object
        """
        try:

            # reset working web page
            self.wpage = Page()

            # get the body of the element url
            reqStatus = self.wpage.getBody(elemUrl)
            ans = None

            if reqStatus == 200:
                # find element inside the html body
                ans = self.wpage.findInReq(
                                    div,
                                    attributes=attrs,
                                    multiple=kwargs.get("multiple"))
            # returning answer
            return ans

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
            self.dataFrame.to_csv(
                            galleryFilePath,
                            sep=",",
                            index=False,
                            encoding="utf-8",
                            mode="w",
                            quoting=csv.QUOTE_ALL
                            )

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
                                galleryFilePath,
                                sep=",",
                                encoding="utf-8",
                                engine="python",
                                quoting=csv.QUOTE_ALL
                                )

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
            ans1 (np.array): image's numpy data matrix
            ans2 (np.array.shape): image's numpy data shape
        """
        try:
            ans1 = None
            ans2 = None
            # joining folder name and filename
            imgfn = os.path.join(fname, fn)
            # reading all data from image

            # ans1 = cv2.imread(imgfn, cv2.IMREAD_COLOR)
            ans1 = cv2.imread(imgfn, cv2.IMREAD_GRAYSCALE)
            ans2 = ans1.shape
            # img_reshape = None

            # ans1 = ans1.flatten()
            # ans1 = list(ans1)
            ans1 = ans1.tolist()
            # ans1 = self.listToString(ans1)
            # separator = ", "
            # ans1 = separator.join(ans1)
            # # ans1 = str().join(ans1, separator="|")
            # ans1 = str(ans1) #, encoding="utf-8")
            ans2 = list(ans2)
            # temp = ans2[0]*ans2[1]#*ans2[2]
            # # temp2 = ans1.tolist()
            # print(str(len(ans1)), str(ans2), temp)  # , len(temp2))

            # # ans = cv2.cvtColor(ans, cv2.COLOR_RGB2RGBA)
            # # returning answer
            return ans1, ans2

        # exception handling
        except Exception as exp:
            raise exp
