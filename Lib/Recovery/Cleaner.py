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
import re
import os
import copy
import urllib
import requests

# =========================================
# extension python libraries
# =========================================
from urllib.parse import urlparse
import unicodedata

# =========================================
# developed python libraries
# =========================================
import Conf
from Lib.Utils import Err as Err
assert Conf
assert Err

# =========================================
# Global variables
# =========================================
DEFAULT_HTML_PARSER = "html.parser"


class Topic(object):
    """
    this module make a request of an URL and helps translate
    data into readable information for the dataframe
    """

    # =========================================
    # class variables
    # =========================================
    url = str()
    request = None
    sbody = None
    shead = None
    dialect = DEFAULT_HTML_PARSER

    def __init__(self, *args, **kwargs):
        """
        class creator for page()

        Args:
            url (str, optional): page url to recover. Defaults is empty str
            dialect (str, optional): beautifulSoup parser dialect. Defaults
            "html.parser"

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:

            # default object attributes
            self.url = str()
            self.dialect = DEFAULT_HTML_PARSER
            self.request = None
            self.sbody = None
            self.shead = None

            # when arguments are pass as parameters
            if len(args) > 0:

                # iterating all over the args
                for arg in args:

                    # updating the url if the crator has it
                    if args.index(arg) == 0:
                        self.url = arg

            # if there are dict decrators in the creator
            if len(kwargs) > 0:

                # iterating all over the decorators
                for key in list(kwargs.keys()):

                    # updating schema in the controller
                    if key == "dialect":
                        self.dialect = kwargs.get("dialect")

        # exception handling
        except Exception as exp:
            raise exp

    def cleanText(self, text):
        # TODO: Moved to Topic() class
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

    def getSearchTags(self, elemSoup, searchElem, rootUrl):
        # TODO: Moved to Topic() class
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

    def getObjectData(self, elemSoup, objElem):
        # TODO: Moved to Topic() class
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
        # TODO: Moved to Topic() class
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
        # TODO: Moved to Topic() class
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
        # TODO: Moved to Topic() class
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
        # TODO: Moved to Topic() class
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
        # TODO: Moved to Topic() class
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
        # TODO: Moved to Topic() class
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
