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
import re

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
from Lib.Utils import Err
assert Conf
assert Err

# =========================================
# Global variables
# =========================================
DEFAULT_HTML_PARSER = "html.parser"


class Page():
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
            Err.reraise(exp, "Page: __init__")

# ============================================================================================================

    def get_image(self, url):
        """
        Get the image from an artwork.

        Args:
            url (str): Image URL

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bytes): image
        """
        try:
            response = requests.get(url)
            ans = response.content
            return ans
        except Exception as exp:
            Err.reraise(exp, "Page: get_image")

    def load_body(self, return_data=False):
        """
        Load the body of the url. 

        Args:
            return_data (bool): Defines if return data or not. Default to False

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (BeautifulSoup): if return_data is True else returns None
        """
        try:
            ans = None
            response = requests.get(self.url)
            self.sbody = BeautifulSoup(response.text, "html.parser")
            if return_data:
                ans = self.sbody
                return ans
            else:
                return ans

        except Exception as exp:
            Err.reraise(exp, "Page: load_body")

    def get_elements(self, tag="a", pattern=""):
        """
        Get the elements of a given tag that their text matches an specific pattern. 

        Args:
            tag (str, optional): tag to filter elements. Default to a
            pattern (str, optional): pattern to match element's content. Default to ""

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): List with all the elements
        """
        try:
            elements = self.sbody.find_all(tag)
            ans = []
            if pattern:
                for element in elements:
                    if re.match(pattern, element.text):
                        url = str(element).split("\"")[1]
                        route = url.split("/")[3]
                        ans.append(route)
                return ans
            return elements
        except Exception as exp:
            Err.reraise(exp, "Page: get_elements")

    def scrap_metadata(self, route, tag="div", attrs={}):
        """
        Get the metadata of a given letter (route).

        Args:
            route (str): letter ID
            tag (str, optional): tag that contains all the data. Default is div
            attrs (dict, optional): attributes that must have the tag. Default is empty

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dict): Dictionary with the metadata
        """
        try:
            path = self.url.replace(".html", "/"+route+"/print.html")
            response = requests.get(path)
            body = BeautifulSoup(response.text, "html.parser")
            elements = body.find_all(tag, attrs=attrs)
            heading = elements[1].text.split("\n")
            title = heading[0]
            author = heading[1].split(": ")[1]
            to = heading[2].split(": ")[1]

            dateAndLocation = heading[3].split(": ")[1]
            location = dateAndLocation.split(", ")[0]
            date = dateAndLocation.split(", ")[1:]
            date = ', '.join(date)

            ans = {"TITLE": title, "AUTHOR": author,
                   "ADDRESSEE": to, "DATE": date,
                   "LOCATION": location}
            return ans
        except Exception as exp:
            Err.reraise(exp, "Page: scrap_metadata")

    def scrap_at_position(self, tag="div", attrs={}, position=0, route=""):
        """
        Get the data at a specific position.

        Args:
            tag (str, optional): tag that elements must have. Default is div
            attrs (dict, optional): attributes that must have the tag. Default is empty
            position (int, optional): position of all the elemnts of the given tag to scrap. Default is 0
            route (str, optional): letter id to scrap. Default is ""

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (str): Text of the element of the given tag at the specific position
        """
        try:
            path = self.url.replace(".html", "/"+route+"/print.html")
            response = requests.get(path)
            body = BeautifulSoup(response.text, "html.parser")
            elements = body.find_all(tag, attrs=attrs)
            ans = ""
            if position < len(elements):
                ans = elements[position].text.replace("\n", " ")
            return ans
        except Exception as exp:
            Err.reraise(exp, "Page: scrap_at_position")

    def scrap_artworks(self, route):
        """
        Scrap all the artowrks of a given letter.

        Args:
            route (str): letter id to scrap artworks.

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dict): dict with all the data of the artworks of the given letter
        """
        try:
            links = []
            titles = []
            Fs = []
            JHs = []
            ids = []

            path = self.url.replace(".html", "/"+route+"/letter.html")

            driver = webdriver.Firefox()
            driver.maximize_window()
            driver.get(path)
            driver.refresh()
            driver.find_element_by_link_text("works of art").click()
            x = driver.find_elements_by_class_name("image")
            for i in x:
                a = i.find_element_by_tag_name("a")
                img = a.find_element_by_tag_name("img")
                image_link = img.get_attribute("src").replace("t.jpg", ".jpg")
                title = img.get_attribute('title')
                F = re.findall(r'F\s\d+', title)
                JH = re.findall(r'JH\s\d+', title)
                if len(F) > 0:
                    F = F[0]
                else:
                    F = ""
                if len(JH) > 0:
                    JH = JH[0]
                else:
                    JH = ""

                # parsing the URL to choose the local folder to save the file
                imgf = image_link.split("/")[-1].replace(".jpg", "")
                ids.append(imgf)
                links.append(image_link)
                Fs.append(F)
                JHs.append(JH)
                titles.append(title)

            driver.close()
            ans = {"ARTWORKSTITLE": titles, "ARTWORKSF": Fs,
                   "ARTWORKSJH": JHs, "ARTWORKSLINK": links, "ARTWORKSID": ids}
            return ans

        except Exception as exp:
            Err.reraise(exp, "Page: scrap_artworks")

# ============================================================================================================

    def get_collection(self, gurl, stime):
        """
        Gets an URL and a wait time to update the BeautifulSoup
        object in the class attribute. 

        Args:
            gurl (str): url of the main gallery to parse.
            stime (float): waiting time between HTML request with selenium.

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            # create the driver for the scrapping of the webpage
            self.request = webdriver.Firefox()
            self.request.implicitly_wait(30)
            self.request.get(gurl)

            # HTML from `<html>`
            rbody = self.request.execute_script(
                "return document.documentElement.innerHTML;")

            # HTML from `<body>`
            rbody = self.request.execute_script(
                "return document.body.innerHTML;")

            # Once scroll returns bs4 parsers the page_source
            self.sbody = BeautifulSoup(rbody, self.dialect)

            # closing driver
            self.request.close()

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Page: get_collection")

    def scroll_collection(self, brdriver, stime):
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

            scroll_pause_time = stime

            # Get scroll height
            last_height = brdriver.execute_script(
                "return document.body.scrollHeight")

            while True:
                # Scroll down to bottom
                brdriver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(scroll_pause_time)

                # Calculate new scroll height and compare with last one
                new_height = brdriver.execute_script(
                    "return document.body.scrollHeight")
                if new_height == last_height:
                    # If heights are the same it will exit the function
                    break
                last_height = new_height

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Page: scroll_collection")

    def findin(self, division, attributes=None, multiple=True):
        """
        find HTML tags inside a BeautifulSoup class attribute.

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
            ans = None

            if multiple is True:
                ans = self.sbody.findAll(division, attrs=attributes)

            elif multiple is False:
                ans = self.sbody.find(division, attrs=attributes)

            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Page: findin")

    def get_body(self, *args):
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
            ans = None

            # requesting the page with the existing url
            if len(args) == 0:
                self.request = requests.get(self.url)
                self.sbody = BeautifulSoup(self.request.content, self.dialect)
                ans = self.request.status_code
                self.request.close()

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
            Err.reraise(exp, "Page: get_body")

    def get_header(self, *args):
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
            ans = None

            # requesting the page with the existing url
            if len(args) == 0:

                self.request = requests.get(self.url)
                headers = self.request.headers
                self.shead = dict(**headers)
                ans = self.request.status_code
                self.request.close()

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
            Err.reraise(exp, "Page: get_header")

    def get_content(self, *args):
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
            ans = None

            # requesting the page with the existing url
            if len(args) == 0:

                self.request = requests.get(self.url)
                self.content = self.request.content
                ans = self.request.status_code
                self.request.close()

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
            Err.reraise(exp, "Page: get_content")
