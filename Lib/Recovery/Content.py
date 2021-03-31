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
# Standard library imports
# =========================================
import time

# =========================================
# Third party imports
# =========================================
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

# =========================================
# Local application imports
# =========================================
import Conf
from Lib.Utils import Err as Err
assert Conf
assert Err

# =========================================
# Global variables
# =========================================
DEFAULT_HTML_PARSER = "html.parser"


class Page(object):
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
    content = None
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
            self.content = None

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

    def getCollection(self, galleryUrl, sleepTime):
        """
        Gets an URL and a wait time to update the BeautifulSoup
        object in the class attribute. only works with a page with an infinite
        scroll option

        Args:
            galleryUrl (str): url of the main gallery to parse.
            sleepTime (float): waiting time between HTML request with selenium.

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:

            # create the driver for the scrapping of the webpage
            self.request = webdriver.Firefox()
            self.request.implicitly_wait(30)
            self.request.get(galleryUrl)

            # scrolling in the infinite gallery
            self.scrollCollection(self.request, sleepTime)

            # HTML from `<html>`
            resquestBody = self.request.execute_script(
                "return document.documentElement.innerHTML;")

            # HTML from `<body>`
            resquestBody = self.request.execute_script(
                "return document.body.innerHTML;")

            # Once scroll returns bs4 parsers the page_source
            self.sbody = BeautifulSoup(resquestBody, self.dialect)

            # closing driver
            self.request.close()

        # exception handling
        except Exception as exp:
            raise exp

    def scrollCollection(self, browserDriver, sleepTime):
        """
        private void function to scroll an infinte gallery of items in a web
        page with selenium driver

        Args:
            driver(driver): selenium driver created to extract de information
            (firefox, chrome, safari).
            timeout(int): wating time for the HTTP response to return to the
            driver and compile the information.

        Raises:
            exp: raise a generic exception if something goes wrong
        """

        try:

            scroll_pause_time = sleepTime

            # Get scroll height
            last_height = browserDriver.execute_script(
                "return document.body.scrollHeight")

            while True:
                # Scroll down to bottom
                browserDriver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(scroll_pause_time)

                # Calculate new scroll height and compare with last one
                new_height = browserDriver.execute_script(
                    "return document.body.scrollHeight")
                if new_height == last_height:
                    # If heights are the same it will exit the function
                    break
                last_height = new_height

        # exception handling
        except Exception as exp:
            raise exp

    def findInReq(self, division, attributes=None, multiple=True):
        """
        This function find HTML tags inside a BeautifulSoup class attribute.

        Args:
            division (str): HTML tag to find in soup ie.: "div", or
            "li"
            attributes (dict, optional): decorators to highlight the divs
            options. Defaults to None.
            multiple (bool, optional): True to find multiple tag occurrences in
            the HTML, False if not. Default to True

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bs-obj): filtered BeautifulSoup object
        """
        try:

            if multiple is True:

                ans = self.sbody.findAll(division, attrs=attributes)
                return ans

            elif multiple is False:

                ans = self.sbody.find(division, attrs=attributes)
                return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getBody(self, *args):
        """
        Request the URL. if succesfull returns the REST page's status code and
        updates the BODY attribute of page() with the information collected it

        Args:
            url (str, optional): page url to recover. Defaults to empty str.

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (int): page's request status code (i.e: 200)
        """
        try:

            # requesting the page with the existing url
            if len(args) == 0:

                self.request = requests.get(self.url)
                self.sbody = BeautifulSoup(self.request.content, self.dialect)
                ans = self.request.status_code
                self.request.close()
                return ans

            # requesting the page with the url parameter
            elif len(args) > 0:

                self.url = args[0]
                self.request = requests.get(self.url)
                self.sbody = BeautifulSoup(self.request.content, self.dialect)
                ans = self.request.status_code
                self.request.close()
                return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getHeader(self, *args):
        """
        Request the URL. if succesfull returns the REST page's status code and
        updates the HEAD attribute of page() with the information collected it

        Args:
            url (str, optional): page url to recover. Defaults to empty str.

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (int): page's request status code (i.e: 200)
        """
        try:

            # requesting the page with the existing url
            if len(args) == 0:

                self.request = requests.get(self.url)
                headers = self.request.headers
                self.shead = dict(**headers)
                ans = self.request.status_code
                self.request.close()
                return ans

            # requesting the page with the url parameter
            elif len(args) > 0:

                self.url = args[0]
                self.request = requests.get(self.url)
                headers = self.request.headers
                self.shead = dict(**headers)

                # for key in self.shead.keys():
                #     print("--- key: value ---")
                #     print(key, " : ", self.shead.get(key))
                # print(type(self.shead))

                ans = self.request.status_code
                self.request.close()
                return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getContent(self, *args):
        """
        Request the URL. if succesfull returns the REST page's status code
        and updates the Content attribute of page() with the information
        collected it

        Args:
            url (str, optional): page url to recover. Defaults to empty str.

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (int): page's request status code (i.e: 200)
        """
        try:

            # requesting the page with the existing url
            if len(args) == 0:

                self.request = requests.get(self.url)
                self.content = self.request.content
                ans = self.request.status_code
                self.request.close()
                return ans

            # requesting the page with the url parameter
            elif len(args) > 0:

                self.url = args[0]
                self.request = requests.get(self.url)
                self.content = self.request.content
                ans = self.request.status_code
                self.request.close()
                return ans

        # exception handling
        except Exception as exp:
            raise exp
