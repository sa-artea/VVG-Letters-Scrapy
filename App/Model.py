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
import re
import unicodedata
import urllib

# ===============================
# extension python libraries
# ===============================
import pandas as pd
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

    # =========================================
    # Index functions
    # =========================================

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

    def getIndexID(self, gsoup, ide, clean):
        # FIXME: remove after implement the Topic() class
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

            ans = list()

            for element in gsoup:

                tid = element.get(ide).replace(clean, "")
                ans.append(tid)

            # returning answer
            return ans

            # exception handling
        except Exception as exp:
            raise exp

    def getIndexURL(self, gsoup, rurl, urle):
        # FIXME: remove after implement the Topic() class
        """
        get the list of the elements inside the gallery index based on the root
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

            ans = list()

            for title in gsoup:

                turl = urllib.parse.urljoin(rurl, title.get(urle))
                ans.append(turl)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getIndexTitle(self, gsoup, etitle):
        # FIXME: remove after implement the Topic() class
        """
        get the element titles from the gallery main page

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

            ans = list()
            for element in gsoup:
                # default unknown element name

                title = "untitled"

                # if we know the name of the element
                if element.get(etitle) is not None:
                    title = element.get(etitle)

                # update the answer
                ans.append(title)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    # =========================================
    # Scrap columns functions in Index
    # =========================================

    def scrapElement(self, eurl, div, attrs, **kwargs):
        """
        scrap elements within a link based on the <div>, html marks
        and other attributes or decoratos

        Args:
            eurl (str): gallery's element url
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
            reqStatus = self.wpage.getBody(eurl)
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

    def getImgName(self, eurl, div, attrs):
        """
        scrap elements within a link based on the <div>, html marks
        and other attributes or decoratos

        Args:
            eurl (str): gallery's element url
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

            # get the headers and the content from the url
            reqStatus = self.wpage.getHeader(eurl)
            reqStatus = self.wpage.getContent()

            ans = str()

            if reqStatus == 200:
                # find attribute inside the headers
                if attrs.items() <= self.wpage.shead.items():
                    headers = self.wpage.shead
                    ans = headers.get(div)
                    ans = str(ans)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def cleanImgName(self, text, elem, clean):
        """
        scrap elements within a link based on the <div>, html marks
        and other attributes or decoratos

        Args:
            text (str): text to be clean
            elem (str): keyword to split the str and process
            clean (str): keyword to clean in the text

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (str): clean file name with extension
        """
        try:

            ans = None
            ans = text.split(elem)[1].strip().strip(clean)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getImgFile(self, gfolder, dlUrl, pfn):
        # FIXME: remove after implement the Topic() class
        """
        save the paint file from the asset URL in the local folder path

        Args:
            gfolder (str): root local dirpath where the file is going to be
            save
            dlUrl (str): url address with the downlodable image file
            pfn (str): filename to save the image

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): True if the file was downloaded in the local dirpath,
            False if not
        """
        try:
            # default answer
            ans = False

            # parsing the URL to choose the local folder to save the file
            imgf = urllib.parse.urlparse(dlUrl)
            imgf = imgf.path.split("/")[len(imgf.path.split("/"))-1]
            fp = os.path.join(gfolder, imgf, pfn)

            # if the file doesnt exists
            if not os.path.exists(fp):

                # saving file from content requests in bit form
                data = self.wpage.content
                with open(fp, "wb") as file:

                    file.write(data)
                    file.close()
                    ans = True
                    return ans

            # if the file already exists
            elif os.path.exists(fp):

                ans = True
                return ans

            # returning answer
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
            fileName (str): file name with .csv extension
            dataFolder (file-object): valid dirpath str or array with
            valid folders.

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
            fileName (str): file name with .csv extension
            dataFolder (file-object): valid dirpath str or array with
            valid folders.

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

    # =========================================
    # clean scraped information functions
    # =========================================

    def cleanDescription(self, soup, elem, clean):
        # TODO: remove after implement the Topic() class
        """
        Clean the page's description from the beatifulSoup object

        Args:
            soup (bs-obj): beatifulSoup object with the description data
            elem (str): HTML <div> keyword to scrap the description data
            clean (list): secondary <div> to clean the description data

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dict): Element (paint) clean description
        """
        try:
            # get the title in the painting page
            ans = dict()

            # some pages dont follow the most commond diagram
            if soup is not None:

                if len(soup) > 0:

                    # finding title <h1> in the soup
                    value = soup[0].find(elem[0])
                    # cleaning data
                    key = value.attrs.get(clean[0])[0]
                    key = str(key).replace(clean[1], "", 1)
                    key = self.cleanText(key)

                    value = str(value.string).strip()
                    value = self.cleanText(value)

                    # creating the dict to return to save as JSON
                    td = {key: value}
                    # updating answer dict
                    ans.update(copy.deepcopy(td))

                    # finding all description paragraphs <p> in the soup
                    description = soup[0].findAll(elem[1])
                    for element in description:

                        key = element.attrs.get(clean[0])[0]
                        key = str(key)
                        key = key.replace(clean[1], "", 1)
                        key = self.cleanText(key)

                        value = str(element.string).strip()
                        value = self.cleanText(value)

                        # creating the dict to return to save as JSON
                        td = {key: value}

                        # updating answer dict
                        ans.update(copy.deepcopy(td))

                    # getting description text section
                    key = soup[1]
                    key = key.attrs.get(clean[0])[0]
                    key = str(key)
                    key = key.replace(clean[1], "", 1)
                    key = self.cleanText(key)

                    # getting section description text
                    text = soup[1].find(elem[1])
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
                    links = soup[1].findAll(elem[2])
                    for link in links:
                        key = str(link.string)
                        key = self.cleanText(key)

                        # getting the link URL
                        url = link.get("href")
                        # reconstructing all the url from the page
                        value = str(url)
                        td = {key: value}

                        # creating the dict to return to save as JSON
                        td = {key: value}

                        # updating answer dict
                        ans.update(copy.deepcopy(td))

            # ans = self.toJSON(ans)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def cleanSearchTags(self, rurl, soup, elem, clean):
        # FIXME: remove after implement the Topic() class
        """
        Clean the page's search-tags from the beatifulSoup object

        Args:
            rurl (str): root URL of the domain to complete the search-tags
            soup (bs-obj): beatifulSoup object with the search-tags data
            elem (str): HTML <div> keyword to scrap the search-tags data
            clean (str): secondary <div> keyword to clean the data from
            the scrap

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dict): Element (paint) clean search-tags
        """
        try:
            # default answer
            ans = dict()

            # checking if searchtags exists
            if soup is not None:

                # checking is the correct collection search tags
                if len(soup) > 0:

                    # finding searhtags <a> in the sou
                    tags = soup[0].findAll(elem)

                    # processing the search tags
                    if len(tags) > 0 and isinstance(tags, list) is True:

                        for tag in tags:
                            # cleaning data
                            key = str(tag.string)
                            key = self.cleanText(key)
                            url = tag.get(clean)

                            # reconstructing all the url from the page
                            value = str(urllib.parse.urljoin(rurl, url))
                            td = {key: value}

                            # updating answer dict
                            ans.update(copy.deepcopy(td))

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def cleanObjData(self, soup, elem):
        # FIXME: remove after implement the Topic() class
        """
        Clean the page's object-data from the beatifulSoup object

        Args:
            soup (bs-obj): beatifulSoup object with the object-data data
            elem (str): HTML <div> keyword to scrap the object-data data

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dict): Element (paint) clean object-data
        """
        try:
            # default answer
            ans = dict()

            # checking if object-data exists
            if soup is not None:

                # finding <dt> and <dd> from the soup
                keys = soup.findAll(elem[0])
                values = soup.findAll(elem[1])

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

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def cleanRelatedWork(self, rurl, soup, elem, clean):
        # FIXME: remove after implement the Topic() class
        """
        process the scraped data from the beatifulSoup object and saves the
        related work information into a JSON files

        Args:
            rurl (str): domain root URL to complete the related-work link
            soup (bs-obj): beatifulSoup object with the related-work data
            elem (str): HTML <div> keyword to scrap the related-work data
            clean (list): secondary <div> to clean the related-work data

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dict): Element (paint) clean related-work
        """
        try:
            # default answer
            ans = dict()

            # checking if searchtags exists
            if soup is not None:

                # finding searhtags <article> in the sou
                relworks = soup[0].findAll(elem)

                # processing related work
                i = 1
                for rw in relworks:
                    # cleaning data and getting all keys and values
                    key = str(rw.find(clean[0]).string)
                    key = self.cleanText(key)

                    url = rw.find(clean[1])
                    url = url.get(clean[2])
                    value = str(urllib.parse.urljoin(rurl, url))

                    # may names are similar in related work
                    if key in ans.keys():

                        # creating alternate key for the dict
                        key = key + " " + str(i)
                        i += 1

                    # updating answer dict
                    td = {key: value}
                    ans.update(copy.deepcopy(td))

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def cleanDownloadURL(self, gsoup, rurl, urle):
        # FIXME: remove after implement the Topic() class
        """
        recovers the download URL for a gallery element

        Args:
            gsoup (bs-obj): beatifulSoup object with gallery element list
            rurl (str): domain root URL to complete the gallery index
            urle (str): HTML <div> keyword to scrap the gallery index
            urls to download files

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (str): unique URL with the downloadable element's file
        """
        try:
            ans = None

            if gsoup is not None:
                url = gsoup.get(urle)
                ans = urllib.parse.urljoin(rurl, url)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def cleanText(self, text):
        # FIXME: remove after implement the Topic() class
        """
        clean text from HTML, remove all inconvinient characters such as:
        extra spaces, extra end-of-line, and non utf-8 characters

        Args:
            text (str): text to clean

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans(str): clean text
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
