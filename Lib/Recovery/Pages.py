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
import datetime
from urllib.parse import urlparse

# ___________________________________________________
# extension python libraries
# ___________________________________________________
import requests
import validators
from bs4 import BeautifulSoup

# ___________________________________________________
# developed python libraries
# ___________________________________________________
import config
from .Utils import error as error
assert config
assert error

class page(object):

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
    sbody = None
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
            if len(args) == 0 and len(kwargs) == 0:

                self.url = ""
                # setting default dialect
                self.dialect = "html.parser"
                self.request = None
                self.shead = None
                self.sbody = None
            
            # url passed as creator parameter
            elif len(args) == 1 and len(kwargs) == 0:

                self.url = str(args[0])
                # setting default dialect
                self.dialect = "html.parser"
                self.request = None
                self.shead = None
                self.sbody = None

            # costume url and dialect in parameters
            elif len(args) == 1 and len(kwargs) > 0:

                self.url = str(args[0])
                self.request = None
                self.shead = None
                self.sbody = None

                # setting costume dialect
                if kwargs.get("dialect"):

                    self.dialect = kwargs["dialect"]

        except Exception as exp:
            error.reraise(exp, 'page->getPage: ')
    
    
    def getPage(self, *args):
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
                answer = self.request.status_code
                self.request.close()
                return answer

            # requesting the page with the url parameter
            elif len(args) == 1:

                self.url = args[0]
                self.request = requests.get(self.url)
                answer = self.request.status_code
                self.request.close()
                return answer

        except Exception as exp:
            error.reraise(exp, 'page->getPage: ')

    def setSoup(self, **kwargs):
        """
        this void method creates the soup of the request with the beautifulsoup (bs4) library, it automaticaly sets body and head soup.
        
        Args:
            dialect (str, optional): parse dialect I use, the same as beautiful soup. Defaults to "html.parser".        
        """
        try:

            if len(kwargs) == 0:

                self.shead = BeautifulSoup(self.request.content, self.dialect).head
                self.sbody = BeautifulSoup(self.request.content, self.dialect).body

            elif len(kwargs) > 0:

                if kwargs.get("dialect") == True:

                    self.dialect = kwargs["dialect"]

                self.shead = BeautifulSoup(self.request.content, self.dialect).head
                self.sbody = BeautifulSoup(self.request.content, self.dialect).body

        except Exception as exp:
            error.reraise(exp, 'page->setSoup: ')

    def findInBody(self, division, attributes = None, multiple = True):
        """[summary]

        Args:
            division (str): the html division to find in the soup ie.: "div", "li"
            attributes ([type], optional): decorators to reduce the divs options. Defaults to None.
            multiple (bool, optional): if the method finds multiple or just one occurrence of the HTML divs. Defaults to True.

        Returns:
            answer: return the element or the list of elements of the soup, -1 if nothing something goes wrong
        """
        answer = -1

        try:

            if multiple == True:

                answer = self.sbody.findAll(division, attrs = attributes)

            elif multiple == False:

                answer = self.sbody.find(division, attrs=attributes)
            
            return answer

        except Exception as exp:
            error.reraise(exp, 'page->findInBody: ')
