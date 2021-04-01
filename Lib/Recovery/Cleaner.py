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
# import re
# import os
# import copy
# import urllib
# import requests

# =========================================
# extension python libraries
# =========================================
# from urllib.parse import urlparse
# import unicodedata

# =========================================
# developed python libraries
# =========================================
import Conf
from Lib.Utils import Err
assert Conf
assert Err

# =========================================
# Global variables
# =========================================
DEFAULT_HTML_PARSER = "html.parser"


class Topic():
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
            url (str): page url to recover. Defaults is empty str
            dialect (str): beautifulSoup parser dialect. Defaults
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
            Err.reraise(exp, "Topic: XXXXX")
