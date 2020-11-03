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
from urllib.parse import urlparse

# ___________________________________________________
# developed python libraries
# ___________________________________________________
import config
assert config
from Apps.Scrapy.model import Gallery
from Lib.Recovery.content import Page as Page
assert Gallery

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
    "COLLECTION_URL",       # element (paint) URL/link recovered with ScrapyWEB
    "DOWNLOAD_URL",         # direct image URL/link for the image in the gallery
    "HAS_PICTURE",          # boolean data to identify if there is a picture file in the local folder, based on DOWNLOAD_URL
    "DESCRIPTION",          # JSON cell with the description of the element in the gallery
    "SEARCH_TAGS",          # JSON cell with the collection tags of the element in the gallery
    "OBJ_DATA",             # JSON cell with the museum object data of the element in the gallery
    "RELATED_WORKS",        # JSON cell with the related work text and URLs of the element in the gallery
    # "EXHIBITIONS",          # JSON cell with the list of the exhibitions were the element in the gallery has been displayed
    # "LITERATURE",           # JSON cell with the list of the literatire references for the gallery elements
]

# default number of paintings in the gallery
DEFAULT_MAX_PAINTS = 10

# defaul wating time for scrapping anything, this helps not to get blocked
DEFAULT_SLEEP_TIME = 3.0

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
                i = 0
                for i in range(int(len(args))):

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
                        self.schema = copy.deepcopy(kwargs[key])

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

            # integratnig subfoders in the realpath
            workPath = str()

            if len(args) > 0:

                for i in range(int(len(args))):
                    workPath = os.path.join(galleryFolder, args[i])

                # if the path doesnt exists you create it
                if not os.path.exists(workPath):

                    os.makedirs(workPath)

                return workPath

        # exception handling
        except Exception as exp:
            raise exp

    def createLocalFolders(self, galleryFolder, *args, **kwargs):
        """[summary]

        Args:
            galleryFolder ([type]): [description]

        Raises:
            exp: [description]
        """
        try:
            # list of IDs as folder names for the local gallery
            folders = self.galleryModel.getColData(args[0])
            
            # looping trhough the possible folders in the local gallery
            for folder in folders:

                # create the local folder path to create if necessary
                tempPaintFolder = os.path.join(galleryFolder, folder)

                # if the local folder doesnt exists
                if not os.path.exists(tempPaintFolder):

                    os.makedirs(tempPaintFolder)

                # the local forlder already ecists
                elif os.path.exists(tempPaintFolder):
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
            answer = self.currentPage.findInReq(scrapDivision, attributes=scrapAttributes)

            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def scrapAgain(self, scrapDivision, scrapAttributes):
        """[summary]

        Args:
            scrapDivision ([type]): [description]
            scrapAttributes ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:
            answer = self.currentPage.findInReq(scrapDivision, attributes=scrapAttributes)
            return answer
        # exception handling
        except Exception as exp:
            raise exp

    def scrapElement(self, elementUrl, scrapDivision, scrapAttributes, **kwargs):
        """[summary]

        Args:
            elementUrl ([type]): [description]
            scrapDivision ([type]): [description]
            scrapAttributes ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:

            self.currentPage = Page()
            # get the body of the element url
            reqStatus = self.currentPage.getBody(elementUrl)
            answer = None

            if reqStatus == 200:
                # find exaclty what I want in the page body
                answer = self.currentPage.findInReq(scrapDivision, attributes=scrapAttributes, multiple=kwargs.get("multiple"))

            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def scrapPageDescription(self, columnName, scrapDivision, scrapAttributes, scrapElements, **kwargs):
        """[summary]

        Args:
            columnName ([type]): [description]
            scrapDivision ([type]): [description]
            scrapAttributes ([type]): [description]
            scrapElements ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:

            # get the url list from the dataframe in the model
            answer = list()
            urls = self.galleryModel.getColData(columnName)
            i = 0

            for url in urls:

                tempSoup = self.scrapElement(url, scrapDivision, scrapAttributes, **kwargs)
                ans = self.getPageDescription(tempSoup, scrapElements)
                # compose answer
                answer.append(ans)
                time.sleep(DEFAULT_SLEEP_TIME)
                i = i + 1
                # print("# " + str(i) + ": " + str(url))

            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def scrapPagePicture(self, columnName, rootURL, scrapDivision, scrapAttributes, scrapElements, **kwargs):

        try:

            answer = list()
            # getting the element url in the gallery
            urls = self.galleryModel.getColData(columnName)
            i = 0

            for url in urls:
                # scraping elements each gallery page
                tempSoup = self.scrapElement(url, scrapDivision, scrapAttributes, **kwargs)
                ans = self.getDownloadURL(tempSoup, rootURL, scrapElements)
                # compose answer
                answer.append(ans)
                time.sleep(DEFAULT_SLEEP_TIME)

                i = i + 1
                # print("# " + str(i) + ": " + str(url))
                
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def scrapPageObjData(self, columnName, scrapDivision, scrapAttributes, scrapElements, **kwargs):
        """[summary]

        Args:
            columnName ([type]): [description]
            scrapDivision ([type]): [description]
            scrapAttributes ([type]): [description]
            scrapElements ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:

            # get the url list from the dataframe in the model
            answer = list()
            urls = self.galleryModel.getColData(columnName)
            i = 0

            for url in urls:

                tempSoup = self.scrapElement(url, scrapDivision, scrapAttributes, **kwargs)
                ans = self.getObjectData(tempSoup, scrapElements)
                # compose answer
                answer.append(ans)
                time.sleep(DEFAULT_SLEEP_TIME)

                i = i + 1
                # print("# " + str(i) + ": " + str(url))

            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def scrapPageSearchTags(self, columnName, rootURL, scrapDivision, scrapAttributes, scrapElements, **kwargs):
        """[summary]

        Args:
            columnName ([type]): [description]
            scrapDivision ([type]): [description]
            scrapAttributes ([type]): [description]
            scrapElements ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:

            # get the url list from the dataframe in the model
            answer = list()
            urls = self.galleryModel.getColData(columnName)
            i = 0

            for url in urls:
                # scraping elements each gallery page
                tempSoup = self.scrapElement(url, scrapDivision, scrapAttributes, **kwargs)

                # extracting the search tags from the soup
                ans = self.getSearchTags(tempSoup, scrapElements, rootURL)
                # compose answer
                answer.append(ans)
                time.sleep(DEFAULT_SLEEP_TIME)
                i = i + 1
                # print("# " + str(i) + ": " + str(url))

            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def scrapPageRelWork(self, columnName, rootURL, scrapDivision, scrapAttributes, scrapElements, **kwargs):
        """[summary]

        Args:
            columnName ([type]): [description]
            scrapDivision ([type]): [description]
            scrapAttributes ([type]): [description]
            scrapElements ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:

            # get the url list from the dataframe in the model
            answer = list()
            urls = self.galleryModel.getColData(columnName)
            i = 0

            for url in urls:
                # scraping elements each gallery page
                tempSoup = self.scrapElement(url, scrapDivision, scrapAttributes, **kwargs)

                # default empty dict to return
                ans = dict()
                # checking if there is any related work to process
                if len(tempSoup) > 0:
                    # extracting the search tags from the soup
                    ans = self.getRelatedWork(tempSoup, scrapElements, rootURL)
                # compose answer
                answer.append(ans)
                time.sleep(DEFAULT_SLEEP_TIME)
                i = i + 1
                # print("# " + str(i) + ": " + str(url))

            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def downloadPictures(self, downloadURLData, galleryFolder, *args, **kwarg):
        """[summary]

        Args:
            downloadURLData ([type]): [description]
            galleryFolder ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:
            # getting the element url in the gallery
            urls = list(downloadURLData)
            answer = list()
            i = 0

            for url in urls:

                # the url is valir, it can be null or na or none
                if validators.url(str(url)) == True:
                    
                    ans = self.getPicture(url, galleryFolder, *args, **kwarg)
                    answer.append(ans)

                # invalid url
                else:

                    ans = False
                    answer.append(ans)
                    
                time.sleep(DEFAULT_SLEEP_TIME)
                i = i + 1
                # print("# " + str(i) + ": " + str(url))

            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def exportToJSON(self, galleryFolder, indexColumn, exportColumn, fileName):  # id_cname, descrip_cname):

        try:

            idData = self.getData(indexColumn)
            exportData = self.getData(exportColumn)
            # args.append(fileName)

            for tindex, tdata in zip(idData, exportData):
                
                tfile = fileName + ".json"

                self.saveToJSON(tdata, galleryFolder, tindex, tfile)

        # exception handling
        except Exception as exp:
            raise exp


    def getSearchTags(self, elementSoup, searchElement, rootURL):
        """[summary]

        Args:
            elementSoup ([type]): [description]
            searchElement ([type]): [description]
            rootURL ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:
            # default answer
            answer = dict()

            # checking if searchtags exists
            if elementSoup != None:

                # checking is the correct collection search tags
                if len(elementSoup) > 0:

                    # finding searhtags <a> in the sou
                    tags = elementSoup[0].findAll(searchElement)

                    # processing the search tags
                    if len(tags) > 0 and isinstance(tags, list) == True:

                        ansd = dict()
                        for tag in tags:

                            # cleaning data
                            key = str(tag.string)
                            url = tag.get("href")
                            # reconstructing all the url from the page
                            value = str(urllib.parse.urljoin(rootURL, url))
                            td = {key: value}
                            # updating answer dict
                            answer.update(copy.deepcopy(td))

            answer = self.toJSON(answer)
            return answer

        # exception handling
        except Exception as exp:
            raise exp
        
    def getObjectData(self, elementSoup, searchElement):
        """[summary]

        Args:
            elementSoup ([type]): [description]
            searchElement ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:
            # default answer
            answer = dict()

            # checking if object-data exists
            if elementSoup != None:

                # finding <dt> and <dd> from the soup
                keys = elementSoup.findAll(searchElement[0])
                values = elementSoup.findAll(searchElement[1])
                
                # both the keys and the values of the object data must be the same
                if len(keys) > 0 and len(values) > 0:
                    
                    # looping over the <dt> and <dd> data
                    for key, value in zip(keys, values):

                        # cleaning data for dictionary
                        key = str(key.string)
                        value = str(value.string)

                        # temp dict for complete answer
                        td = {key: value}
                        # updating answer dict
                        answer.update(copy.deepcopy(td))
            
            # transforming the answer to JSON
            answer = self.toJSON(answer)
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def getRelatedWork(self, elementSoup, searchElement, rootURL):
        """[summary]

        Args:
            elementSoup ([type]): [description]
            searchElement ([type]): [description]
            rootURL ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:

            # default answer
            answer = dict()

            # checking if searchtags exists
            if elementSoup != None:

                # finding searhtags <article> in the sou
                relworks = elementSoup[0].findAll(searchElement)

                # processing related work
                i = 1
                for rw in relworks:
                    # cleaning data and getting all keys and values
                    key = str(rw.find("span").string)
                    url = rw.find("a").get("href")
                    value = str(urllib.parse.urljoin(rootURL, url))

                    # may names are similar in related work
                    if key in answer.keys():
                        
                        # creating alternate key for the dict
                        key = key + " " + str(i)
                        i += 1

                    # updating answer dict
                    td = {key: value}
                    answer.update(copy.deepcopy(td))

            answer = self.toJSON(answer)
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def getData(self, columnName, *args, **kwargs):
        """[summary]

        Args:
            columnName ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:
            # getting the element url in the gallery
            answer = list()
            answer = self.galleryModel.getData(columnName, *args, **kwargs)
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def getPicture(self, downloadURL, galleryFolder, *args, **kwargs):
        """[summary]

        Args:
            downloadURL ([type]): [description]
            galleryFolder ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:

            # default answer
            answer = False

            # requesting page
            downReq = requests.get(downloadURL)

            # succesful request
            if downReq.status_code == 200:

                # to get the file name from headears I go to the URL request headers and extract it from the string
                pictureFile = str(downReq.headers.__getitem__("Content-Disposition"))
                pictureFile = pictureFile.split(";")[1].strip().strip("filename=")

                # parsing of the URL to choose the local folder to save the file
                elementFolder = urlparse(downloadURL)
                elementFolder = elementFolder.path.split("/")[len(elementFolder.path.split("/"))-1]
                filePath = os.path.join(galleryFolder, elementFolder, pictureFile)
                
                # if the file doesnt exists
                if not os.path.exists(filePath):
                    
                    # seving file from content requests in bit form
                    with open(filePath, "wb") as file:
                        file.write(downReq.content)
                        file.close()
                        answer = True
                        return answer

                # if the file already exists
                elif os.path.exists(filePath):

                    answer = True
                    return answer

            return answer

        # exception handling
        except Exception as exp:
            raise exp

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

    def getDownloadURL(self, gallerySoup, rootURL, urlElement):
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
            answer = None

            if gallerySoup != None:
                url = gallerySoup.get(urlElement)
                answer = urllib.parse.urljoin(rootURL, url)

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
                # default unknown element name

                title = "untitled"
                
                # if we know the name of the element 
                if element.get(titleElement) != None:
                    title = element.get(titleElement)
                                
                # update the answer
                answer.append(title)

            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def getPageTittle(self, elementSoup, titleElement):
        """[summary]

        Args:
            elementSoup ([type]): [description]
            titleElement ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:
            # get the title in the painting page
            answer = elementSoup.find(titleElement).string
            # cleaning data
            answer = str(answer).strip()
            answer = re.sub(" \s+", "", answer)
            answer = re.sub("\n", "", answer)

            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def getPageDescription(self, elementSoup, descripElement):
        """[summary]

        Args:
            elementSoup ([type]): [description]
            descripElement ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:
            # get the title in the painting page
            answer = dict()

            # some pages dont follow the most commond diagram
            if elementSoup != None:
            
                if len(elementSoup) > 0:
                    
                    # finding title <h1> in the soup
                    value = elementSoup[0].find(descripElement[0])
                    # cleaning data
                    key = value.attrs.get("class")[0]
                    key = str(key).replace("art-object-page-content-", "", 1)
                    value = str(value.string).strip()
                    value = re.sub(" \s+", "", value)
                    value = re.sub("\n", "", value)

                    # creating the dict to return to save as JSON
                    td ={key:value}

                    # updating answer dict
                    answer.update(copy.deepcopy(td))

                    # finding all the paragraphs of the description <p> in the soup
                    description = elementSoup[0].findAll(descripElement[1])
                    for element in description:

                        key = element.attrs.get("class")[0]
                        key = str(key).replace("art-object-page-content-", "", 1)
                        value = str(element.string).strip()
                        value = re.sub(" \s+", "", value)
                        value = re.sub("\n", "", value)

                        # creating the dict to return to save as JSON
                        td = {key: value}

                        # updating answer dict
                        answer.update(copy.deepcopy(td))

            answer = self.toJSON(answer)
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def toJSON(self, dictData, *args, **kwargs):

        try:

            # transforming dictionary to an interoperable JSON structure
            answer = json.dumps(copy.deepcopy(dictData), ensure_ascii = False, indent = 4)
            return answer

        # exception handling
        except Exception as exp:
            raise exp
    
    def saveToJSON(self, jsonData, galleryFolder, *args, **kwargs):
        try:
            # guardo en un archivo el JSON de la descripcion.

            localFilePath = os.path.join(galleryFolder, *args)

            with open(localFilePath, "w+", encoding="utf-8") as file:
                file.write(jsonData)
                file.close()

        # exception handling
        except Exception as exp:
            raise exp

    def newDataFrame(self, columns, data):
        """[summary]

        Args:
            columns ([type]): [description]
            data ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:
            
            answer = self.galleryModel.createNewIndex(columns, data)
            return answer
            
        # exception handling
        except Exception as exp:
            raise exp

    def updateData(self, column, data):
        """[summary]

        Args:
            column ([type]): [description]
            data ([type]): [description]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:

            answer = self.galleryModel.updateData(column, data)
            return answer

        # exception handling
        except Exception as exp:
            raise exp

    def saveGallery(self, fileName, dataFolder):
        """[summary]

        Args:
            fileName ([type]): [description]
            dataFolder ([type]): [description]

        Raises:
            exp: [description]
        """
        try:
            
            self.galleryModel.saveGallery(fileName, dataFolder)

            # exception handling
        except Exception as exp:
            raise exp

    def loadGallery(self, fileName, dataFolder):
        """[summary]

        Args:
            fileName ([type]): [description]
            dataFolder ([type]): [description]

        Raises:
            exp: [description]
        """
        try:
            self.galleryModel.loadGallery(fileName, dataFolder)

            # exception handling
        except Exception as exp:
            raise exp

    def checkGallery(self):
        """[summary]

        Raises:
            exp: [description]

        Returns:
            [type]: [description]
        """
        try:
            return self.galleryModel.checkGallery()

            # exception handling
        except Exception as exp:
            raise exp
