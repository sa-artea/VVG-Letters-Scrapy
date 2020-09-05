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
from Recovery.Utils import error as error
assert config
assert error

"""
this module make a request of an URL and helps translate its 
data into readable information for the dataframe
"""
class page(object):
    """[summary]

    Args:
        object ([type]): [description]

    Returns:
        [type]: [description]
    """
    url = str()
    request = None
    shead = None
    sbody = None
    dialect = "html.parser"


    def __init__(self, url = str(), dialect = None):
        """[summary]

        Args:
            url ([str], optional): url of the page I want to recover. Defaults to str().
            dialect ([str], optional): parse dialect I use, the same as beautiful soup. Defaults to None.
        """
        self.url = url
        self.request = None
        self.shead = None
        self.sbody = None

        if dialect != None:
            self.dialect = dialect

        self.dialect = "html.parser"

    def getPage(self, url):

        try:
            
            self.request = requests.get(self.url)
            return self.request.status_code

        except Exception as exp:
            error.reraise(exp, 'page->getPage: ')

    def setSoup(self, dialect = "html.parser"):

        try:

            if self.request.status_code == 200:

                if dialect != "html.parser":
                    
                    self.dialect = dialect

                self.shead = BeautifulSoup(self.request.content, self.dialect).head
                self.sbody = BeautifulSoup(self.request.content, self.dialect).body

        except Exception as exp:
            error.reraise(exp, 'page->setSoup: ')

    def findInBody(self, division, attributes = None, multiple = True):

        answer = None

        try:

            if multiple == True:

                answer = self.sbody.findAll(division, attrs = attributes)

            else:

                answer = self.shead.find(division, attrs = attributes)

            return answer

        except Exception as exp:
            error.reraise(exp, 'page->findInBody: ')
