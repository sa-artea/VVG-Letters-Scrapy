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
import copy
import json
import urllib
import requests
import validators
import time

# ___________________________________________________
# extension python libraries
# ___________________________________________________
from urllib.parse import urlparse
import unicodedata

# ___________________________________________________
# developed python libraries
# ___________________________________________________
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

# defaul waiting time for scrapping data, this helps not to get blocked
DEFAULT_SLEEP_TIME = 3.0

# default short waiting time for scrapping data, avoids some errors if the
# script goes to fast
DEFAULT_SHORT_SLEEP_TIME = 0.2


class Controller (object):
    """
    Controller class, comunicate the View() and the Model()
    """

    # =========================================
    # class variables
    # =========================================
    webGallery = str()
    galleryPath = str()
    modelStruct = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
    gallery = Gallery()
    wpage = Page()

    def __init__(self, *args, **kwargs):
        """
        Controller() class creator

        Args:
            webGallery (str): URL for the gallery to scrap data
            galleryPath (str): local dirpath for the gallery data
            modelStruct (list): array with the column names for the model
            gallery (Gallery): object with the gallery dataframe model
            wpage (Page): the current webpage the controller is scrapping
        """

        try:

            # Controller default values
            self.webGallery = str()
            self.galleryPath = str()
            self.modelStruct = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
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
                        self.gallery = args[i]

            # if there are dict decrators in the creator
            if len(kwargs) > 0:

                for key in list(kwargs.keys()):

                    # updating schema in the controller
                    if key == "schema":
                        self.schema = copy.deepcopy(kwargs[key])

                    # setting the max size of the gallery
                    if key == "size":
                        self.maxPaints = kwargs[key]

        # exception handling
        except Exception as exp:
            raise exp

    def SetUpLocal(self, galleryF, *args):
        """
        set up local gallery filepath accorrding to the root gallery folder and
        other subfolders

        Args:
            galleryF (str): name of the main gallery folder
            subfolders (list, optional): array with the subfolders names to the
            gallery folder conforming the absolute dirpath

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            workPath (str): returns the local filepath to the gallery
        """
        try:

            # answer with realpath local subfoders
            workPath = str()

            if len(args) > 0:

                for i in range(int(len(args))):
                    workPath = os.path.join(galleryF, args[i])

                # if the path doesnt exists you create it
                if not os.path.exists(workPath):

                    os.makedirs(workPath)

                return workPath

        # exception handling
        except Exception as exp:
            raise exp

    def createLocalFolders(self, galleryF, *args, **kwargs):
        """
        creates local subfolders with the gallery folder as root for them

        Args:
            galleryF (str): name of the main gallery folder

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            # list of IDs as folder names for the local gallery
            folders = self.gallery.getData(args[0])

            # looping trhough the possible folders in the local gallery
            for folder in folders:

                # create the local folder path to create if necessary
                tempPF = os.path.join(galleryF, folder)

                # if the local folder doesnt exists
                if not os.path.exists(tempPF):

                    os.makedirs(tempPF)

                # the local forlder already ecists
                elif os.path.exists(tempPF):
                    pass

        # exception handling
        except Exception as exp:
            raise exp

    def scrapIndex(self, galleryUrl, sleepTime, div, attrs):
        """
        scrap the gallery index for all the elements within it

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
        using the previous index scraped results, search for new information to
        complement the dataframe index

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
        scrap all elements within a link based on its <div> html mark and other
        attributes/decoratos

        Args:
            elemUrl (str): gallery's element url
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bs-obj): div and attrs filtered beatifulsoup object
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
                        multiple=kwargs.get("multiple")
                        )

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def scrapPageDescription(self, coln, div, attrs, elem, **kwargs):
        """
        takes a column name, html divs and decorators to scrap the gallery
        element description from url

        Args:
            coln (str): column name in the dataframe to save the scraped data
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine
            elem (str): element is a secondary <div> keyword to refine the
            search and scrap process

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list with JSON objects collecting the elements
            descriptions
        """
        try:

            # get the url list from the dataframe in the model
            ans = list()

            urls = self.gallery.getData(coln)

            for url in urls:

                tempSoup = self.scrapElement(url, div, attrs, **kwargs)
                temp = self.getPageDescription(tempSoup, elem)
                # print(temp)

                # compose answer
                ans.append(temp)
                time.sleep(DEFAULT_SLEEP_TIME)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def scrapPagePicture(self, coln, rootUrl, div, attrs, elem, **kwargs):
        """
        using the column name and a root URL scrap the data to download the
        element/picture file

        Args:
            coln (str): column name in the dataframe to save the scraped data
            rootUrl (str): root URL of the domain to download the picture
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine
            elem (str): element is a secondary <div> keyword to refine the
            search and scrap process

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): the list of downloadable picture files recovered in the
            gallery element
        """
        try:

            ans = list()
            # getting the element url in the gallery
            urls = self.gallery.getData(coln)

            for url in urls:

                # scraping elements each gallery page
                tempSoup = self.scrapElement(url, div, attrs, **kwargs)
                temp = self.getDownloadURL(tempSoup, rootUrl, elem)

                # compose answer
                ans.append(temp)
                time.sleep(DEFAULT_SLEEP_TIME)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def scrapPageObjData(self, coln, div, attrs, elem, **kwargs):
        """
        able to scrap the object data from the webpage using the dataframe's
        column name, the HTML divs and other decorators in the url

        Args:
            coln (str): column name in the dataframe to save the scraped data
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine
            elem (str): element is a secondary <div> keyword to refine the
            search and scrap process

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): the list of the object data recovered from the
            gallery element
        """
        try:

            # get the url list from the dataframe in the model
            ans = list()
            urls = self.gallery.getData(coln)

            for url in urls:

                tempSoup = self.scrapElement(url, div, attrs, **kwargs)
                temp = self.getObjectData(tempSoup, elem)
                # print(temp)

                # compose answer
                ans.append(temp)
                time.sleep(DEFAULT_SLEEP_TIME)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def scrapPageSearchTags(self, coln, rootUrl, div, attrs, elem, **kwargs):
        """
        able to scrap the element/image  search tags from the webpage using the
        dataframe's column name, the HTML divs and other decorators in the url

        Args:
            coln (str): column name in the dataframe to save the scraped data
            rootUrl (str): root URL of the domain to complete the search tags
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine
            elem (str): element is a secondary <div> keyword to refine the
            search and scrap process

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): the list of the search tags recovered from the
            gallery element
        """
        try:

            # get the url list from the dataframe in the model
            ans = list()
            urls = self.gallery.getData(coln)

            for url in urls:
                # scraping elements each gallery page
                tempSoup = self.scrapElement(url, div, attrs, **kwargs)

                # extracting the search tags from the soup
                temp = self.getSearchTags(tempSoup, elem, rootUrl)
                # print(temp)

                # compose answer
                ans.append(temp)
                time.sleep(DEFAULT_SLEEP_TIME)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def scrapPageRelWork(self, coln, rootUrl, div, attrs, elem, **kwargs):
        """
        able to scrap the related work data from the webpage using the
        dataframe's column name, the HTML divs and other decorators in the url

        Args:
            coln (str): column name in the dataframe to save the scraped data
            rootUrl (str): root URL of the domain to complete the related work
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
            urls = self.gallery.getData(coln)

            for url in urls:

                # scraping elements each gallery page
                tempSoup = self.scrapElement(url, div, attrs, **kwargs)

                # # default empty dict to return
                temp = dict()
                # checking if there is any related work to process

                if len(tempSoup) > 0:

                    # extracting the search tags from the soup
                    temp = self.getRelatedWork(tempSoup, elem, rootUrl)

                # print(temp)
                # compose answer
                ans.append(temp)
                time.sleep(DEFAULT_SLEEP_TIME)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def downloadPictures(self, dlUrlData, galleryF, *args, **kwarg):
        """
        download the picture files from a list of available url in the gallery

        Args:
            dlUrlData (str): list of downloadable known URLs
            galleryF (str): name of the main gallery folder

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list of boolean marking if it is possible to download a
            picture file or not
        """
        try:
            # getting the element url in the gallery
            urls = list(dlUrlData)
            ans = list()

            for url in urls:

                # the url is valir, it can be null or na or none
                if validators.url(str(url)) is True:

                    temp = self.getPicture(url, galleryF, *args, **kwarg)
                    ans.append(temp)

                # invalid url
                else:

                    temp = False
                    ans.append(temp)

                time.sleep(DEFAULT_SLEEP_TIME)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def exportToJSON(self, galleryF, indexCol, expCol, fname):
        """
        export the data from one column in the model's dataframe into JSON file
        in an specific local gallery folder

        Args:
            galleryF (str): name of the main gallery folder
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
                self.saveToJSON(tdata, galleryF, tindex, tfile)
                time.sleep(DEFAULT_SHORT_SLEEP_TIME)

        # exception handling
        except Exception as exp:
            raise exp

    def getSearchTags(self, elemSoup, searchElem, rootUrl):
        # TODO: separate into other class in future versions
        """
        process the scraped data from the beatifulSoup object and saves the
        relevant information into a JSON files

        Args:
            elemSoup (bs-obj): beatifulSoup object with the search tags data
            searchElem (str): HTML <div> keyword to search and scrap the search
            tags data
            rootUrl (str): root URL of the domain to complete the search tags

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (json): json with the search tags data recovered from the
            gallery element
        """
        try:
            # default answer
            ans = dict()

            # checking if searchtags exists
            if elemSoup is not None:

                # checking is the correct collection search tags
                if len(elemSoup) > 0:

                    # finding searhtags <a> in the sou
                    tags = elemSoup[0].findAll(searchElem)

                    # processing the search tags
                    if len(tags) > 0 and isinstance(tags, list) is True:

                        for tag in tags:
                            # cleaning data
                            key = str(tag.string)
                            key = self.cleanText(key)
                            url = tag.get("href")

                            # reconstructing all the url from the page
                            value = str(urllib.parse.urljoin(rootUrl, url))
                            td = {key: value}

                            # updating answer dict
                            ans.update(copy.deepcopy(td))

            ans = self.toJSON(ans)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def exportImages(self, indexCol, imgf, *args, **kwargs):
        """
        reads the gallery's element id folder, get the image file and  export
        them an RGBA to a numpy matrix

        Args:
            indexCol (str): name of the column in the dataframe with the
            gallery index with unique IDs for each elements (same as the local
            folder's names)
            imgf (str): relevant image's extension to process

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): the list of the related work recovered from the
            gallery elements
        """
        try:
            # working variables
            ans1 = list()
            ans2 = list()
            indexData = self.getData(indexCol)
            rootDir = self.galleryPath

            # iterating 2 list at the same time
            for tid in indexData:

                timgfn = os.path.join(rootDir, tid)

                # recovering image
                timg, tshape = self.getImage(timgfn, imgf, *args, **kwargs)
                ans1.append(timg)
                ans2.append(tshape)

            # return answer list
            return ans1, ans2

        # exception handling
        except Exception as exp:
            raise exp

    def getImage(self, fname, imgf, *args, **kwargs):
        """
        get the image using a folder dirpath and the name of the file

        Args:
            fname (str): Gallery's root dirpath in local drive
            imgf (str): image's file format, ie.: ".jpg"

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans1 (np.array): list with the numpy matrix of the image's RGB data
            ans2 (np.array.shape): list with the image's numpy shape
        """

        try:
            # default answer
            ans1 = None
            ans2 = None
            flist = os.listdir(fname)
            fn = ""

            # finding the propper file
            for tf in flist:
                if tf.endswith(imgf):
                    fn = tf

            # if the file exists
            if fn != "":
                ans1, ans2 = self.gallery.imgToData(fname, fn, *args, **kwargs)

            # returning answer
            ans1 = copy.deepcopy(ans1)
            ans2 = copy.deepcopy(ans2)
            return ans1, ans2

        # exception handling
        except Exception as exp:
            raise exp

    def getObjectData(self, elemSoup, objElem):
        # TODO: separate into other class in future versions
        """
        process the scraped data from the beatifulSoup object and saves the
        object data into a JSON files

        Args:
            elemSoup (bs-obj): beatifulSoup object with the object data
            object data to recover the search tags
            objElem (str): HTML <div> keyword to process the Page's scraped
            object-data

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (json): json with the object-data recovered from the
            gallery element
        """
        try:
            # default answer
            ans = dict()

            # checking if object-data exists
            if elemSoup is not None:

                # finding <dt> and <dd> from the soup
                keys = elemSoup.findAll(objElem[0])
                values = elemSoup.findAll(objElem[1])

                # soup keys and values must have data
                if len(keys) > 0 and len(values) > 0:

                    # looping over the <dt> and <dd> data
                    for key, value in zip(keys, values):

                        # cleaning data for dictionary
                        key = str(key.string)
                        key = self.cleanText(key)

                        value = str(value.string)
                        value = self.cleanText(value)

                        # temp dict for complete answer
                        td = {key: value}
                        # updating answer dict
                        ans.update(copy.deepcopy(td))

            # transforming the answer to JSON
            ans = self.toJSON(ans)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getRelatedWork(self, elemSoup, relwElem, rootUrl):
        # TODO: separate into other class in future versions
        """
        process the scraped data from the beatifulSoup object and saves the
        related work information into a JSON files

        Args:
            elemSoup (bs-obj): beatifulSoup object with the related work data
            relwElem (str): HTML <div> keyword to process the Page's scraped
            related work
            rootUrl (str): domain root URL to complete the related work link

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (json): json with the related work recovered from the
            gallery element
        """
        try:
            # default answer
            ans = dict()

            # checking if searchtags exists
            if elemSoup is not None:

                # finding searhtags <article> in the sou
                relworks = elemSoup[0].findAll(relwElem)

                # processing related work
                i = 1
                for rw in relworks:
                    # cleaning data and getting all keys and values
                    key = str(rw.find("span").string)
                    key = self.cleanText(key)

                    url = rw.find("a").get("href")
                    value = str(urllib.parse.urljoin(rootUrl, url))

                    # may names are similar in related work
                    if key in ans.keys():

                        # creating alternate key for the dict
                        key = key + " " + str(i)
                        i += 1

                    # updating answer dict
                    td = {key: value}
                    ans.update(copy.deepcopy(td))

            ans = self.toJSON(ans)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getData(self, coln, *args, **kwargs):
        """
        get the data based in the column name of the model's dataframe

        Args:
            coln (str): column name in the dataframe to save the scraped data

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): return the list with the column name data
        """
        try:
            # getting the element url in the gallery
            ans = list()
            ans = self.gallery.getData(coln, *args, **kwargs)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getPicture(self, downloadUrl, galleryF, *args, **kwargs):
        # TODO: separate into other class in future versions
        """
        save the element image file in a local dirpath folder

        Args:
            downloadUrl (str): url address with the downlodable image file
            galleryF (str): root local dirpath where the file is going to be
            save

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): True if the file was downloaded in the local dirpath,
            False if not
        """
        try:
            # default answer
            ans = False

            # requesting page
            downReq = requests.get(downloadUrl)

            # succesful request
            if downReq.status_code == 200:

                # get the request header to get the file name str
                picFile = downReq.headers.__getitem__("Content-Disposition")
                picFile = str(picFile)
                picFile = picFile.split(";")[1].strip().strip("filename=")

                # parsing the URL to choose the local folder to save the file
                elemf = urlparse(downloadUrl)
                elemf = elemf.path.split("/")[len(elemf.path.split("/"))-1]
                filePath = os.path.join(galleryF, elemf, picFile)

                # if the file doesnt exists
                if not os.path.exists(filePath):

                    # seving file from content requests in bit form
                    with open(filePath, "wb") as file:

                        file.write(downReq.content)
                        file.close()
                        ans = True
                        return ans

                # if the file already exists
                elif os.path.exists(filePath):

                    ans = True
                    return ans

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getID(self, gallerySoup, idElem):
        """
        get the unique identifier (ID) of the gallery element and assign it to
        the dataframe record

        Args:
            gallerySoup (bs-obj): beatifulSoup object containing the gallery's
            element list
            idElem (str): HTML <div> keyword to process the Page's scraped
            gallery's IDs

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list with the gallery's element IDs
        """
        try:
            ans = list()

            for element in gallerySoup:

                tid = element.get(idElem).replace("/en/collection/", "")
                ans.append(tid)

            # returning answer
            return ans

            # exception handling
        except Exception as exp:
            raise exp

    def getURL(self, gallerySoup, rootUrl, urlElem):
        """
        get the list of the elements inside the gallery index based on the root
        domain url and html div tags

        Args:
            gallerySoup (bs-obj): beatifulSoup object containing the gallery's
            element list
            rootUrl (str): root URL of the domain to complete the element url
            urlElem (str): HTML <div> keyword to process the Page's scraped
            gallery urls

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list with each of the gallery's unique urls
        """
        try:
            ans = list()

            for title in gallerySoup:

                turl = urllib.parse.urljoin(rootUrl, title.get(urlElem))
                ans.append(turl)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getDownloadURL(self, gallerySoup, rootUrl, urlElem):
        """
        recovers the download url for a gallery element

        Args:
            gallerySoup (bs-obj): beatifulSoup object containing the gallery's
            element list
            rootUrl (str): root URL of the domain to complete the related work
            urlElem (str): HTML <div> keyword to process the Page's scraped
            gallery's urls to download files
        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (str): unique url with the downlodable element's file
        """
        try:
            ans = None

            if gallerySoup is not None:
                url = gallerySoup.get(urlElem)
                ans = urllib.parse.urljoin(rootUrl, url)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getTitle(self, gallerySoup, titleElem):
        """
        get the element titles from the gallery main page

        Args:
            gallerySoup (bs-obj): beatifulSoup object containing the gallery's
            element list
            titleElem HTML <div> keyword to process the scraped data from
            the gallery's soup to get the element titles

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list with the gallery's element tittles as str
        """
        try:
            ans = list()
            for element in gallerySoup:
                # default unknown element name

                title = "untitled"

                # if we know the name of the element
                if element.get(titleElem) is not None:
                    title = element.get(titleElem)

                # update the answer
                ans.append(title)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getPageTittle(self, elemSoup, titleElem):
        # TODO: separate into other class in future versions
        """
        get the page's tittle from the beatifulSoup object

        Args:
            elemSoup (bs-obj): beatifulSoup object with the page tittle data
            titleElem (str): HTML <div> keyword to recover the scraped page
            title

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (str): Page's tittle
        """
        try:
            # get the title in the painting page
            ans = elemSoup.find(titleElem).string
            # cleaning data
            ans = str(ans).strip()
            ans = unicodedata.normalize('NFD', ans)
            ans = ans.encode('ascii', 'ignore')
            ans = ans.decode("utf-8")
            ans = str(ans)
            ans = re.sub(r" \s+", "", ans)
            ans = re.sub(r"\n", "", ans)
            ans = re.sub(r"'", "", ans)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getPageDescription(self, elemSoup, desElem):
        # TODO: separate into other class in future versions
        """
        get the page's description from the beatifulSoup object

        Args:
            elemSoup (bs-obj): beatifulSoup object with the description scraped
            from the webpage
            desElem (str): HTML <div> keyword to recover the scraped page
            description data

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (str): Page's tittle
        """
        try:
            # get the title in the painting page
            ans = dict()

            # some pages dont follow the most commond diagram
            if elemSoup is not None:

                if len(elemSoup) > 0:

                    # finding title <h1> in the soup
                    value = elemSoup[0].find(desElem[0])
                    # cleaning data
                    key = value.attrs.get("class")[0]
                    key = str(key).replace("art-object-page-content-", "", 1)
                    key = self.cleanText(key)

                    value = str(value.string).strip()
                    value = self.cleanText(value)

                    # creating the dict to return to save as JSON
                    td = {key: value}
                    # updating answer dict
                    ans.update(copy.deepcopy(td))

                    # finding all  description paragraphs <p> in the soup
                    description = elemSoup[0].findAll(desElem[1])
                    for element in description:

                        key = element.attrs.get("class")[0]
                        key = str(key)
                        key = key.replace("art-object-page-content-", "", 1)
                        key = self.cleanText(key)

                        value = str(element.string).strip()
                        value = self.cleanText(value)

                        # creating the dict to return to save as JSON
                        td = {key: value}

                        # updating answer dict
                        ans.update(copy.deepcopy(td))

                    # getting description text section
                    key = elemSoup[1]
                    key = key.attrs.get("class")[0]
                    key = str(key)
                    key = key.replace("art-object-page-content-", "", 1)
                    key = self.cleanText(key)

                    # getting section description text
                    text = elemSoup[1].find(desElem[1])
                    value = str()
                    for txt in text:
                        txt = txt.string
                        txt = str(txt)
                        value = value + txt

                    # cleaning data
                    value = str(value).strip()
                    value = self.cleanText(value)

                    # updating answer dict
                    td = {key: value}
                    ans.update(copy.deepcopy(td))

                    # finding all the related links in the description
                    links = elemSoup[1].findAll(desElem[2])
                    for link in links:
                        # key = link.attrs.get("")[0]
                        key = str(link.string)
                        key = self.cleanText(key)

                        # getting the link URL
                        url = link.get("href")
                        # reconstructing all the url from the page
                        # value = str(urllib.parse.urljoin(rootUrl, url))
                        value = str(url)
                        td = {key: value}

                        # creating the dict to return to save as JSON
                        td = {key: value}

                        # updating answer dict
                        ans.update(copy.deepcopy(td))

            ans = self.toJSON(ans)

            # returning answer
            return ans

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

    def saveToJSON(self, jsonData, galleryF, *args, **kwargs):
        """
        saves a json object into a local file according to the gallery folder
        and subfolders

        Args:
            jsonData (JSON): JSON data to save in file
            galleryF (str): name of the main gallery folder
            subfolders (str, optional) a subfolder name to the main gallery
            folder, can be as much as neeeded

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            # configuring local filepath
            localFP = os.path.join(galleryF, *args)

            # saving data in with utf-8 encoding
            with open(localFP, "w", encoding="utf-8") as file:
                file.write(jsonData)
                file.close()

        # exception handling
        except Exception as exp:
            raise exp

    def newDataFrame(self, columns, data):
        """
        creates a new model dataframe with

        Args:
            columns (list): list of columns names for the new dataframe
            data (dataframe): new dataframe data, it can be empty

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dataframe.info()): pandas description of dataframe
        """
        try:

            ans = self.gallery.createNewIndex(columns, data)
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

            ans = self.gallery.updateData(column, data)
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

            self.gallery.saveGallery(fname, folder)

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
            self.gallery.loadGallery(fname, folder)

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
            return self.gallery.checkGallery()

            # exception handling
        except Exception as exp:
            raise exp

    def cleanText(self, text):
        """
        clean text from HTML, remove all

        Args:
            text (str): text to be clean

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans(str): cleaned and processed text
        """
        try:
            # asigning text as ans
            ans = str(text)

            # attempt striping
            ans = ans.strip()

            # fix encoding
            ans = unicodedata.normalize('NFD', ans)
            ans = ans.encode('ascii', 'ignore')
            ans = ans.decode("utf-8")
            ans = str(ans)

            # removing extra spaces
            ans = re.sub(r" \s+", " ", ans)
            # removing newlines
            ans = re.sub(r"\n", ". ", ans)
            # remove pesky single quote
            ans = re.sub(r"'", "", ans)
            # ans = re.sub(r"[^\w\s]", "", ans)
            # HTML weird leftovers
            ans = re.sub(r"None{1,3}", " ", ans)

            # final cast and rechecking
            ans = str(ans)
            # ans = re.sub(r"\W", " ", ans)
            ans = re.sub(r" \s+", " ", ans)

            # return answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp
