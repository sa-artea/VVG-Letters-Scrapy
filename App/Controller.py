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

# =========================================
# native python libraries
# =========================================
import os
import copy
import json
import time

# =========================================
# extension python libraries
# =========================================
import validators

# =========================================
# developed python libraries
# =========================================
import Conf
from App.Model import Gallery
from Lib.Recovery.Content import Page as Page
assert Conf
assert Gallery

"""
The controller mediates between the view and the model, there are
some operations implemented in this class, specially the load and save
functions as well as functions to merge the results from different
elements in the models or various models.
"""

# global config variables
cfgFolder = "Config"
cfgSchema = "df-schema.ini"

# loading config schema into the program
dataSchema = Conf.configGlobal(cfgFolder, cfgSchema)

# default template for the element/paint dict in gallery
DEFAULT_FRAME_SCHEMA = eval(dataSchema.get("DEFAULT", "columns"))

# defaul waiting time for scrapping data, this helps not to get blocked
DEFAULT_SLEEP_TIME = 3.0

# default short waiting time for scrapping data, avoids some errors if the
# script goes to fast
DEFAULT_SHORT_SLEEP_TIME = 0.2


class Controller (object):
    """
    Controller class, comunicate the View() and the Model(), it also
    manage file Input/Output
    """

    # =========================================
    # class variables
    # =========================================
    webGallery = str()
    galleryPath = str()
    imagesPath = str()
    schema = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
    gallery = Gallery()
    wpage = Page()

    # =========================================
    # class creator
    # =========================================

    def __init__(self, *args, **kwargs):
        """
        Controller() class creator

        Args:
            webGallery (str): URL for the gallery to scrap data
            galleryPath (str): local dirpath for the gallery data
            schema (list): array with the column names for the model
            gallery (Gallery): object with the gallery dataframe model
            # wpage (Page): the current webpage the controller is scrapping

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            Controller (Model): return a new Controller() object
        """

        try:
            # Controller default values
            self.webGallery = str()
            self.galleryPath = str()
            self.imagesPath = str()
            self.schema = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
            self.gallery = Gallery()
            self.wpage = Page()

            # when arguments are pass as parameters
            if len(args) > 0:
                i = 0
                for i in range(int(len(args))):

                    # URL of the remote gallery to scrap
                    if i == 0:
                        self.webGallery = args[i]

                    # local dirpath to save the gallery CSV
                    if i == 1:
                        self.galleryPath = args[i]

                    # painting list containing the data of the gallery
                    if i == 2:
                        self.imagesPath = args[i]

            # if there are dict decrators in the creator
            if len(kwargs) > 0:

                for key in list(kwargs.keys()):

                    # updating schema in the controller
                    if key == "schema":
                        self.schema = copy.deepcopy(kwargs[key])

                    # setting the max size of the gallery
                    if key == "model":
                        self.gallery = kwargs[key]

        # exception handling
        except Exception as exp:
            raise exp

    # =========================================
    # Config local folder functions
    # =========================================

    def SetUpLocal(self, *args):
        """
        Set up local gallery filepath acording to the root gallery folder and
        other subfolders

        Args:
            rootf (str): name of the main gallery local folder
            subfolders (list, optional): the subfolders names to the gallery
            conforming the absolute dirpath

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            workPath (str): returns the local filepath to the gallery
        """
        try:

            # answer with realpath local subfoders
            workPath = str()
            workPath = os.path.join(*args)

            # if the path doesnt exists you create it
            if not os.path.exists(workPath):

                os.makedirs(workPath)

            return workPath

        # exception handling
        except Exception as exp:
            raise exp

    def createLocalFolders(self, *args, **kwargs):
        """
        Creates local subfolders with the gallery folder as root for them

        Args:
            gfolder (str): name of the main gallery folder
            coln (str): name of the ID column to create the folders

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:

            gfolder = args[0]
            coln = args[1]

            # list of IDs as folder names for the local gallery
            folders = self.getData(coln)

            # looping trhough the possible folders in the local gallery
            for folder in folders:

                # create the local folder path to create if necessary
                tfp = os.path.join(gfolder, folder)

                # if the local folder doesnt exists
                if not os.path.exists(tfp):

                    os.makedirs(tfp)

                # the local forlder already ecists
                elif os.path.exists(tfp):
                    pass

        # exception handling
        except Exception as exp:
            raise exp

    # =========================================
    # Index functions
    # =========================================

    def scrapIndex(self, galleryUrl, sleepTime, div, attrs):
        """
        Scrap the gallery, create a new index and recover all elements in it

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
            gm = self.gallery
            ans = gm.scrapIndex(galleryUrl, sleepTime, div, attrs)
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def scrapAgain(self, div, attrs):
        """
        Scrap for new information and complete the dataframe index after
        executing the scrapIndex() function

        Args:
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bs-obj): div and attrs filtered beatifulsoup object
        """
        try:
            gm = self.gallery
            ans = gm.scrapAgain(div, attrs)
            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getIndexID(self, gsoup, ide, clean):
        """
        get the unique identifier (ID) of the gallery elements (paints) and
        list them to introduce them itto the dataframe

        Args:
            gsoup (bs-obj): list with gallery elements in Beatiful Soup format
            ide (str): HTML <div> keyword to extract the element (paint) ID

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list with the elements (paints) IDs
        """
        try:
            gm = self.gallery
            ans = gm.getIndexID(gsoup, ide, clean)
            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getIndexURL(self, gsoup, rurl, urle):
        """
        Get the list of the elements inside the gallery index based on the root
        domain url and html div tags

        Args:
            gsoup (bs-obj): beatifulSoup object containing the gallery's
            element list
            rurl (str): root URL of the domain to complete the element url
            urle (str): HTML <div> keyword to process the Page's scraped
            gallery urls

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list with each of the gallery's unique urls
        """
        try:

            gm = self.gallery
            ans = gm.getIndexURL(gsoup, rurl, urle)
            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getIndexTitle(self, gsoup, etitle):
        """
        Get the element titles from the gallery main page

        Args:
            gsoup (bs-obj): beatifulSoup object containing the gallery's
            element list
            etitle HTML <div> keyword to process the scraped data from
            the gallery's soup to get the element titles

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): gallery element (paints) titles in string
        """
        try:

            gm = self.gallery
            ans = gm.getIndexTitle(gsoup, etitle)
            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    # =========================================
    # Scrap columns functions from Index
    # =========================================

    def scrapDescriptions(self, *args, **kwargs):
        """
        Scrap the elements (paints) description in the index using the
        ID column name, HTML divisions <divs>, decorative attributes,
        secondary HTML elements and cleaning HTML divisions

        Args:
            coln (str): ID column name of the gallery dataframe
            div (str): HTML <div> search and scrap keyword
            attrs (dict): decorative <div> keywords to refine the scrap
            elem (str): secondary <div> keyword to refine the search
            and scrap process
            clean (list): secondary <div> keywords to clean the data
            obtained from the scrap

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list of element descriptions in JSON format
        """
        try:

            # get the url list from the dataframe in the model
            ans = list()
            gm = self.gallery
            coln = args[0]
            div = args[1]
            attrs = args[2]
            elem = args[3]
            clean = args[4]

            urls = self.getData(coln)

            for url in urls:

                tsoup = gm.scrapElement(url, div, attrs, **kwargs)
                tans = gm.cleanDescription(tsoup, elem, clean)

                # compose answer
                tans = self.toJSON(tans)
                ans.append(tans)
                time.sleep(DEFAULT_SLEEP_TIME)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def scrapPaintLinks(self, *args, **kwargs):
        """
        scrap the data to download the painting file using the ID column name
        and the domain root URL

        Args:
            coln (str): ID column name of the gallery dataframe
            rurl (str): domain root URL to download the elements
            div (str): HTML <div> search and scrap keyword
            attrs (dict): decorative <div> keywords to refine the scrap
            elem (str): secondary <div> keyword to refine the search
            and scrap process

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list of the URLs (HTTP) to download the elements
        """
        try:

            ans = list()
            gm = self.gallery
            coln = args[0]
            rurl = args[1]
            div = args[2]
            attrs = args[3]
            elem = args[4]

            # getting the element url in the gallery
            urls = self.getData(coln)

            for url in urls:

                # scraping elements each gallery page
                tsoup = gm.scrapElement(url, div, attrs, **kwargs)
                tans = gm.cleanDownloadURL(tsoup, rurl, elem)

                # compose answer
                ans.append(tans)
                time.sleep(DEFAULT_SLEEP_TIME)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def downloadPaints(self, *args, **kwargs):
        """
        download the paint files from the list of available asset url
        in the gallery

        Args:
            dlUrlColn (str): column name of known download URLs
            gfolder (str): name of the main gallery folder
            div (str): HTML <div> search and scrap keyword
            attrs (dict): decorative <div> keywords to refine the scrap
            elem (str): secondary <div> keyword to refine the search
            and scrap process

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list of boolean marking if it is possible to
            download a picture file or not
        """
        try:
            # getting the element url in the gallery
            ans = list()
            gm = self.gallery
            dlUrlColn = args[0]
            gf = args[1]
            div = args[2]
            attrs = args[3]
            elem = args[4]
            clean = args[5]

            urls = self.getData(dlUrlColn)

            for url in urls:

                # the url is valid, it can be null or na or none
                if validators.url(str(url)) is True:

                    # recovers the image file name
                    tsoup = gm.getImgName(url, div, attrs)
                    # clean the name to save
                    timgf = gm.cleanImgName(tsoup, elem, clean)
                    # download and save the image in the local folder
                    tans = gm.getImgFile(gf, url, timgf)
                    ans.append(tans)

                # invalid url
                else:
                    tans = False
                    ans.append(tans)

                time.sleep(DEFAULT_SLEEP_TIME)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def scrapSearchTags(self, *args, **kwargs):
        """
        Scrap the elements (paints) search-tags using the ID column name
        in the index, the domain URL, HTML divisions <divs>, decorative
        attributes, secondary HTML elements and cleaning HTML divisions

        Args:
            coln (str): ID column name of the gallery dataframe
            rurl (str): root URL of the domain to complete the search-tags
            div (str): HTML <div> keyword to scrap the search-tags
            attrs (dict): decorative attributes in the <div> keyword to refine
            elem (str): element is a secondary <div> keyword to refine the
            search and scrap process
            clean (str): secondary <div> keyword to clean the data from
            the scrap

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list of element search-tags in JSON format
        """
        try:

            # get the url list from the dataframe in the model
            ans = list()
            gm = self.gallery
            coln = args[0]
            rurl = args[1]
            div = args[2]
            attrs = args[3]
            elem = args[4]
            clean = args[5]
            urls = self.getData(coln)

            for url in urls:
                # scraping elements each gallery page
                tsoup = gm.scrapElement(url, div, attrs, **kwargs)
                # extracting the search tags from the soup
                tans = gm.cleanSearchTags(rurl, tsoup, elem, clean)

                # compose answer
                tans = self.toJSON(tans)
                ans.append(tans)
                time.sleep(DEFAULT_SLEEP_TIME)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def scrapObjsData(self, *args, **kwargs):
        #     def scrapObjsData(self, coln, div, attrs, elem, **kwargs):
        """
        Scrap the elements (paints) object-data using the ID column name
        in the index, HTML divisions <divs>, decorative attributes,
        secondary HTML elements and cleaning HTML divisions

        Args:
            coln (str): ID column name of the gallery dataframe
            div (str): HTML <div> keyword to scrap the object-data
            attrs (dict): decorative attributes in the <div> keyword to refine
            elem (str): element is a secondary <div> keyword to refine the
            search and scrap process
            clean (str): secondary <div> keyword to clean the data from
            the scrap

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list of element object-data in JSON format
        """
        try:
            # get the url list from the dataframe in the model
            ans = list()
            gm = self.gallery
            coln = args[0]
            div = args[1]
            attrs = args[2]
            elem = args[3]
            urls = self.getData(coln)

            for url in urls:

                tsoup = gm.scrapElement(url, div, attrs, **kwargs)
                tans = gm.cleanObjData(tsoup, elem)

                # compose answer
                tans = self.toJSON(tans)
                ans.append(tans)
                time.sleep(DEFAULT_SLEEP_TIME)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def scrapRelatedWork(self, *args, **kwargs):
        """
        able to scrap the related work data from the webpage using the
        dataframe's column name, the HTML divs and other decorators in the url

        Args:
            coln (str): ID column name of the gallery dataframe
            rurl (str): root URL of the domain to complete the related work
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine
            elem (str): element is a secondary <div> keyword to refine the
            search and scrap process

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): the list of the related work recovered from the
            gallery elements
        """
        try:
            # get the url list from the dataframe in the model
            ans = list()
            gm = self.gallery
            coln = args[0]
            rurl = args[1]
            div = args[2]
            attrs = args[3]
            elem = args[4]
            clean = args[5]

            urls = gm.getData(coln)

            for url in urls:

                # scraping elements each gallery page
                tsoup = gm.scrapElement(url, div, attrs, **kwargs)

                # # default empty dict to return
                tans = dict()
                # checking if there is any related work to process

                if len(tsoup) > 0:

                    # extracting the search tags from the soup
                    tans = gm.cleanRelatedWork(rurl, tsoup, elem, clean)

                # compose answer
                tans = self.toJSON(tans)
                ans.append(tans)
                time.sleep(DEFAULT_SLEEP_TIME)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def exportPaints(self, *args):
        """
        Export the images from a source folder into a target folder,
        the target images are in color and in grayscale

        Args:
            coln (str): ID column name of the gallery dataframe
            sfext (str): source image file extension, ie.: "jpg"
            tfext (dict): target image file extension, ie.: "jpg"
            tsufix (dict): target image file sufix, ie.: "-rgb"

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): the list of dict with the relative localpath
            file for each gallery element
            (ej.: {"rgb": "/Data/Img/s0004V1962r-rgb.jpg",
                    "bw": "/Data/Img/s0004V1962r-b&w.jpg"
                    })
        """
        try:
            # default answer
            ans = list()
            # working variables
            coln = args[0]
            sfext = args[1]
            tfext = args[2]
            tsufix = args[3]

            # getting index data
            indata = self.getData(coln)
            gm = self.gallery
            gp = self.galleryPath
            ip = self.imagesPath

            # iterating over the index data
            for tid in indata:
                # config source and target folders
                srcf = os.path.join(gp, tid)
                tgtf = os.path.join(ip, tid)

                # recovering source images
                srcfn = gm.getSourceImages(srcf, sfext)

                # setting target images
                tgtfn = gm.setTargetImages(srcfn, tgtf, tfext, tsufix)

                # exporting images
                tans = gm.exportImages(srcfn, tgtfn, tsufix)

                # compose answer
                tans = self.toJSON(tans)
                ans.append(tans)
                time.sleep(DEFAULT_SHORT_SLEEP_TIME)

            # return answer list
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def exportShapes(self, *args):
        """
        Export the image shapes from the exported images in the target folder

        Args:
            coln (str): ID column name of the gallery dataframe
            sfext (str): source image file extension, ie.: "jpg"
            tfext (dict): target image file extension, ie.: "jpg"
            tsufix (dict): target image file sufix, ie.: "-rgb"

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list) the list of dict with the shape of each
            gallery element
            (ej.: {"rgb": (450, 280, 3),
                    "bw": (450, 280)})
        """
        try:
            # default answer
            ans = list()
            # working variables
            coln = args[0]
            tfext = args[1]
            tsufix = args[2]

            # getting index data
            indata = self.getData(coln)
            gm = self.gallery
            ip = self.imagesPath

            # iterating over the index data
            for tid in indata:
                # config source and target folders
                tgtf = os.path.join(ip, tid)

                # recovering source images
                tgtfn = gm.getSourceImages(tgtf, tfext)

                # exporting shapes
                tans = gm.exportShapes(tgtfn, tsufix)

                # compose answer
                tans = self.toJSON(tans)
                ans.append(tans)
                time.sleep(DEFAULT_SHORT_SLEEP_TIME)

            # return answer list
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getData(self, coln, *args, **kwargs):
        """
        get the data based in the column name of the model's dataframe

        Args:
            coln (str): column name of the gallery dataframe to get

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): data from the column name
        """
        try:
            # getting the element url in the gallery
            ans = list()
            gm = self.gallery
            ans = gm.getData(coln, *args, **kwargs)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    # =========================================
    # dataframe CRUD functions
    # =========================================

    def newDataFrame(self, columns, data):
        """
        creates a new model dataframe with

        Args:
            columns (list): list of columns names for the new dataframe
            data (dataframe): new dataframe data, it can be empty

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): true if the function created a new df-frame,
            false otherwise
        """
        try:
            gm = self.gallery
            ans = gm.createNewIndex(columns, data)
            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def updateData(self, column, data):
        """
        update the data in one column of the gallery model (dataframe)

        Args:
            column (str): model column name to update
            data (list): new data to update in the column, must be of the same
            the dataframe column

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dataframe.info()): pandas description of dataframe
        """
        try:
            gm = self.gallery
            ans = gm.updateData(column, data)
            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def saveGallery(self, fname, folder):
        """
        write the gallery model (pandas) into a CSV file

        Args:
            fname (str): file name to write the gallery model
            folder (str): subfolder to write the CSV file

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            gm = self.gallery
            ans = gm.saveGallery(fname, folder)
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def loadGallery(self, fname, folder):
        """
        read the gallery model (pandas) from a CSV file

        Args:
            fname (str): file name from where to read the gallery model
            folder (str): subfolder from where to read the CSV file

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            gm = self.gallery
            ans = gm.loadGallery(fname, folder)
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def checkGallery(self):
        """
        checks the data stats of the gallery dataframe

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dataframe.info()): pandas description of dataframe
        """
        try:
            gm = self.gallery
            gm.checkGallery()
            # return ans

        # exception handling
        except Exception as exp:
            raise exp

    # =========================================
    # dataframe I/O functions
    # =========================================

    def exportToJSON(self, gfolder, indexCol, expCol, fname):
        """
        export the data from one column in the model's dataframe into JSON file
        in an specific local gallery folder

        Args:
            gfolder (str): name of the main gallery folder
            indexCol (str): name of the column in the dataframe with the
            gallery index with unique IDs for each elements (same as the local
            folder's names)
            expCol (str): name of the column with the data to export to JSON
            fname (str): name of the file to save

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            # working variables
            idData = self.getData(indexCol)
            expData = self.getData(expCol)

            for tindex, tdata in zip(idData, expData):

                tfile = fname + ".json"
                self.writeJSON(tdata, tfile, gfolder, tindex)
                time.sleep(DEFAULT_SHORT_SLEEP_TIME)

        # exception handling
        except Exception as exp:
            raise exp

    def writeJSON(self, data, filename, *args):
        """
        Save a json into a local file according to the gallery folder
        and subfolders

        Args:
            data (JSON): JSON data to save in file
            filename (str): JSON fole name
            gfolder (str): name of the main gallery folder
            subfolders (str): list of subfolder names to the main gallery
            folder, can be as much as neeeded

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            # configuring local filepath
            lfp = os.path.join(*args, filename)

            # saving data in with utf-8 encoding
            with open(lfp, "w", encoding="utf-8") as file:
                file.write(data)
                file.close()

        # exception handling
        except Exception as exp:
            raise exp

    def toJSON(self, dictData, *args, **kwargs):
        """
        transform a python dictionary into a JSON

        Args:
            dictData (dict): dictionary with the relevant data to transform

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (JSOM): a proper JSON object containing the dictionary data
        """
        try:
            # transforming dictionary to JSON
            td = copy.deepcopy(dictData)
            ans = json.dumps(td, ensure_ascii=False, indent=4)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp
