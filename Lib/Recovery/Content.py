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
# Standard library imports
# ___________________________________________________
import os
import sys
import re
import time

# ___________________________________________________
# Third party imports
# ___________________________________________________
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
# ___________________________________________________
# Local application imports
# ___________________________________________________
import config
assert config

class Page(object):

    """
    this module make a request of an URL and helps translate its 
    data into readable information for the dataframe
    """

    #___________________________________________
    # class parameters
    #___________________________________________
    url = ""
    request = None
    shead = None
    rsoup = None
    dialect = "html.parser"

    def __init__(self, *args, **kwargs):
        """
        creator of the class page()

        Args:
            url (str, optional): url of the page I want to recover. Defaults to str().
            dialect (str, optional): parse dialect I use, the same as beautiful soup. Defaults to "html.parser".
        """
        try:

            # not passing parameters in the creator
            self.url = str()
            # setting default dialect
            self.dialect = "html.parser"
            self.request = None
            self.rsoup = None

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
        """[summary]

        Args:
            galleryUrl ([type]): [description]
            elementAttributes ([type]): [description]
            sleepTime ([type]): [description]

        Returns:
            [type]: [description]
        """
        try:

            # create the driver for the scrapping of the webpage
            self.request = webdriver.Firefox()
            self.request.implicitly_wait(30)
            self.request.get(galleryUrl)

            # scrolling in the infinite gallery
            self.scrollCollection(self.request, sleepTime)

            # HTML from `<html>`
            resquestBody = self.request.execute_script("return document.documentElement.innerHTML;")

            # HTML from `<body>`
            resquestBody = self.request.execute_script("return document.body.innerHTML;")

            # Once scroll returns bs4 parsers the page_source
            self.rsoup = BeautifulSoup(resquestBody, self.dialect)

            # closing driver
            self.request.close()
            
        # exception handling
        except Exception as exp:
            raise exp

    def scrollCollection(self, browserDriver, sleepTime):
        """this function scroll an infinte gallery of items in a web page with selenium driver

        Args:
            driver (driver): selenium driver created to extract de information (firefox, chrome, safari).
            timeout (int): wating time for the HTTP response to return to the driver and compile the information.

        Returns:
            None: activate firefox and scroll the gallery, after execution the browser will close.
        """
        try:

            scroll_pause_time = sleepTime

            # Get scroll height
            last_height = browserDriver.execute_script("return document.body.scrollHeight")

            while True:
                # Scroll down to bottom
                browserDriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(scroll_pause_time)

                # Calculate new scroll height and compare with last scroll height
                new_height = browserDriver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    # If heights are the same it will exit the function
                    break
                last_height = new_height

        # exception handling
        except Exception as exp:
            raise exp
    
    def findInBody(self, division, attributes=None, multiple=True):
        """[summary]

        Args:
            division (str): the html division to find in the soup ie.: "div", "li"
            attributes ([type], optional): decorators to reduce the divs options. Defaults to None.
            multiple (bool, optional): if the method finds multiple or just one occurrence of the HTML divs. Defaults to True.

        Returns:
            answer: return the element or the list of elements of the soup, -1 if nothing something goes wrong
        """
        try:

            if multiple == True:

                answer = self.rsoup.findAll(division, attrs=attributes)
                return answer

            elif multiple == False:

                answer = self.rsoup.find(division, attrs=attributes)
                return answer

        # exception handling
        except Exception as exp:
            raise exp

    def getBody(self, *args):
        """ 
        the method makes a request with the URL. if succesfull retunrs the REST status code of the page and updates the self.request attribute of page().

        Args:
            url (str, optional): url of the page I want to recover. Defaults to str().

        Returns:
            int: the status code of the recovered page in the request status_code
        """
        try:

            # requesting the page with the existing url
            if len(args) == 0:

                self.request = requests.get(self.url)
                self.rsoup = BeautifulSoup(self.request, self.dialect)
                answer = self.request.status_code
                self.request.close()
                return answer

            # requesting the page with the url parameter
            elif len(args) == 1:

                self.url = args[0]
                self.request = requests.get(self.url)
                self.rsoup = BeautifulSoup(self.request, self.dialect)
                answer = self.request.status_code
                self.request.close()
                return answer

        # exception handling
        except Exception as exp:
            raise exp
