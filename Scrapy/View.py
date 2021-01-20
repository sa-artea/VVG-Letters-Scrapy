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
import pprint
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
# from Lib.Recovery.Pages import page as page
# from Lib.Utils import error as error
import Config
from Scrapy.Controller import Controller
from Scrapy.Model import Gallery
assert Controller
assert Gallery
assert Config

"""
The view is in charge of the interaction with the user
selecting the options to scrap the web and load the data
into the CSV files.
"""

# ___________________________________________________
#  data input
# ___________________________________________________

# URL for the webpage to recover the paintings
# url with small query for small tests
# vincent_page = "https://www.vangoghmuseum.nl/en/collection?q=&Artist=Vincent+van+Gogh&Type=study"
# url query for VVG large consult excluding the written part of the letters
vincent_page = "https://www.vangoghmuseum.nl/en/collection?q=&Artist=Vincent+van+Gogh&Type=painting%2Cdrawing%2Csketch%2Cprint%2Cstudy"
# url with complete query with many artists related with VVG
# vincent_page = "https://www.vangoghmuseum.nl/en/collection?q=&Type=painting%2Cdrawing%2Csketch%2Cprint%2Cstudy"

# root URL of the gallery
vincent_root = "https://vangoghmuseum.nl"

# local root dirpath where the data will be save
vincent_localpath = "C:\\Users\\Felipe\\Universidad de los andes\\CoIArt - General\\04 - Data\\01 - Vincent\\Source\\"

# real rootpath to work with
galleryFolder = os.path.normpath(vincent_localpath)

# subdirs in the local root path needed to process data
paintsFolder = "Paints"
lettersFolder = "Letters"
# scrapped subfolder
sourceFolder = "Source"
# app subfoder
dataFolder = "Data"
# idex csv file
# indexFile = "VanGoghGallery_small.csv"
indexFile = "VanGoghGallery_large.csv"
# indexFile = "VanGoghGallery_extensive.csv"

# default template for the element/paint dict in gallery
VINCENT_DF_COLUMNS = [
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
VINCENT_MAX_PAINTS = 25

# ______________________________________________________
#  data input for scraping the html and creating index
# ______________________________________________________
# html tags for the general object
index_div = "a"
index_attrs = {
    "class": "collection-art-object-wrapper"
    }

colurl_cname = VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("COLLECTION_URL")]

# html tags for the unique ID in the collection
id_div = "a"
id_element = "href"
id_attrs = {
    "class": "collection-art-object-wrapper",
    "href": re.compile("^/en/collection/"),
    }

id_cname = VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("ID")]

#  html tags for the title of the element
title_div = "a"
title_element = "title"
title_attrs = {
    "class": "collection-art-object-wrapper",
    # "title": re.compile("."),
    }

#  html tags for the url of the element
url_div = "a"
url_element = "href"
url_attrs = {
    "class": "collection-art-object-wrapper",
    }

# column names for creating a new index and model in the program
start_index_columns = copy.deepcopy(VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("ID"):VINCENT_DF_COLUMNS.index("COLLECTION_URL")+1])
print(start_index_columns)
# ['ID', 'TITLE', 'COLLECTION_URL']

# ______________________________________________________
#  data input for scraping the html of each element
# ______________________________________________________

# html tags for scrapping gallery element description
desc_div = "section"
desc_attrs ={
    "class": re.compile("art-object-page-content-"),
    }
desc_element = ["h1", "p"]

descrip_cname = VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("DESCRIPTION")]

# html tags for scrapping and downloding the image 
pic_div = "a"
pic_attrs = {
    "class":"btn-icon art-object-header-bar-button",
    "href": re.compile("^/asset/download/"),
    }
pic_elements = "href"

# html tags for search annotations in the gallery elements.
search_div = "section"
search_attrs = {
    "class": "artobject-page-collection-links",
    }
search_elements = "a"#["li", "a"] # ["ul", "li"]

# html tags for object data in the gallery elements.
object_div = "dl"
object_attrs = {
    "class": "definition-list",
    # "string": "Object data",
    }
object_elements = ["dt", "dd"]

# html tags for related work in the gallery elements.
relatedw_div = "div"
relatedw_attrs = {
    "class": "teaser-row content-row grid-row",
    }
relatedw_elements = "article"

# # html tags for the exhibition data in the gallery elements.
# exhibits_div = "div"
# exhibits_attrs = {
#     "class": "accordion-item expanded",
#     "string": re.compile("Exhibitions")
#     }
# exhibits_elements = "markdown"

# # html tags for the literature reference data in the gallery elements.
# lit_div = ""
# lit_attrs = {
#     }
# lit_elements = ""

# dummy var for the index of the dataframe
donwload_cname = VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("DOWNLOAD_URL")]
haspic_cname = VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("HAS_PICTURE")]
search_cname = VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("SEARCH_TAGS")]
object_cname = VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("OBJ_DATA")]
relatedw_cname = VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("RELATED_WORKS")]
# exhibits_cname = VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("EXHIBITIONS")]
# lit_cname = VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("LITERATURE")]

# column names for creating the JSON in the folders
json_index_columns = copy.deepcopy(VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("DESCRIPTION"):VINCENT_DF_COLUMNS.index("RELATED_WORKS")+1])
print(json_index_columns)

# ___________________________________________________
#  Functions to print webpage recovered data
# ___________________________________________________
class View(object):
    """the View is the console interface for the program, connect directly with the Controller to the Model

    Args:
        object ([type]): [description]
    """

    galleryControl = Controller()
    galleryModel = Gallery()
    localGallery = ""
    galleryWEB = ""

    def __init__(self, *args, **kwargs):

        if len(args) > 0:

            for i in range(0, len(args)-1):
                if i == 0:
                    self.galleryWEB = args[i]
                
                if i == 1:
                    self.localGallery = args[i]

            self.galleryModel = Gallery(self.galleryWEB, self.localGallery)
            self.galleryControl = Controller(self.galleryWEB, self.localGallery, model = self.galleryModel)
        else:

            self.galleryModel = Gallery()
            self.galleryControl = Controller()

    def menu(self):
        """
        menu options
        """

        print("========================= WELCOME =========================")
        print("1) Start gallery index (scraping webpage for ID, TITLE and COLLECTION_URL)") # create a new index based in the root url
        print("2) Save gallery data (saving data in CSV)") #save in files all the scrapped data
        print("3) Load gallery data (load existing data in CSV)") # load preavious scraped data into model
        print("4) Check gallery data (read existing data memory)") # load preavious scraped data into model

        # recovers the basic data from the gallery query
        print("5) Compose for the basic description and image of the gallery elements (DESCRIPTION)")

        # complement the basic data created from option 6) and 12)
        print("6) Compose download URLs of the gallery elements (DOWNLOAD_URL)")
        print("7) Download image file of the gallery elements (HAS_PICTURE)")
        print("8) Compose for the search tags of the gallery elements (SEARCH_TAGS)")
        print("9) Compose for the collection data of the gallery elements (OBJ_DATA)")
        print("10) Compose for the related works of the gallery elements (RELATED_WORKS)")
        print("11) Exporting DataFrame to JSON Files (from CSV to Local Gallery)")
        # print("11) Compose for the exhibition history of the gallery elements EXHIBITIONS)")
        # print("12) Compose for the literature references of the gallery elements (LITERATURE)")
        print("0) EXIT (last option)") # finish program

    def run(self):
        """
        menu excution
        """
        # setting gallery base webpage
        self.galleryWEB = vincent_page

        # setting up local dir for saving data
        self.localGallery = self.galleryControl.SetUpLocal(galleryFolder, sourceFolder, paintsFolder)
        print("== == == == == == == Configuring the gallery View == == == == == == ==")
        print("View localdir: " + str(self.localGallery))
        print("View remote gallery URL: " + str(self.galleryWEB))
        print("\n")

        # creating the gallery model
        self.galleryModel = Gallery(self.galleryWEB, self.localGallery, schema = VINCENT_DF_COLUMNS)
        print("== == == == == == == Crating the gallery model == == == == == == ==")
        print("Model localdir: " + str(self.galleryModel.localGallery))
        print("Model remote gallery URL: " + str(self.galleryModel.galleryWEB))
        print("\n")

        # creating the gallery controller
        self.galleryControl = Controller(self.galleryWEB, self.localGallery, self.galleryModel, schema = VINCENT_DF_COLUMNS)
        print("== == == == == == == Crating the gallery controller == == == == == == ==")
        print("Controller localdir: " + str(self.galleryControl.localGallery))
        print("Controller remote gallery URL: " + str(self.galleryControl.galleryWEB))
        print("\n")

        while True:
            self.menu()
            inputs = input('Select an option to continue\n')

            # starting gallery object to scrap data
            if int(inputs) == 1:
                print("Starting new gallery index(scraping URL!!! = ID, TITLE, COLLECTION_URL)...")
                # starting the gallery index from scratch
                galleryIndex = self.galleryControl.scrapIndex(self.galleryWEB, 5, id_div, id_attrs)
                id_data = self.galleryControl.getID(galleryIndex, id_element)
                print("the gallery IDs have been processed...")

                galleryIndex = self.galleryControl.scrapAgain(title_div, title_attrs)
                title_data = self.galleryControl.getTitle(galleryIndex, title_element)
                print("the gallery Titles have ben processed...")

                galleryIndex = self.galleryControl.scrapAgain(id_div, id_attrs)
                link_data = self.galleryControl.getURL(galleryIndex, vincent_root, id_element)
                print("the gallery collection URLs have ben processed...")

                index_data = (id_data, title_data, link_data)

                answer = self.galleryControl.newDataFrame(start_index_columns, index_data)
                print("the Model new DataFrame is created...")
                
                self.galleryControl.createLocalFolders(self.galleryControl.localGallery, id_cname)
                print("the local gallery folders are created...")
                print(" ======================= REPORT ========================= ")

            elif int(inputs) == 2:
                print("Saving gallery dataframe model into CSV file...")
                self.galleryControl.saveGallery(indexFile, dataFolder)
                answer = self.galleryControl.checkGallery()
                print(" ======================= REPORT ========================= ")
                print(answer)

            elif int(inputs) == 3:
                print("Loading gallery from CSV file into dataframe model...")
                self.galleryControl.loadGallery(indexFile, dataFolder)
                self.galleryControl.createLocalFolders(self.galleryControl.localGallery, id_cname)
                answer = self.galleryControl.checkGallery()
                print(" ======================= REPORT ========================= ")
                print(answer)

            elif int(inputs) == 4:
                print("Checking gallery status in the model (dataframe from CSV)...")
                answer = self.galleryControl.checkGallery()
                print(" ======================= REPORT ========================= ")
                print(answer)

            elif int(inputs) == 5:
                print("Composing elements basic descripion (DESCRIPTION)...")
                descrip_data = self.galleryControl.scrapPageDescription(colurl_cname, desc_div, desc_attrs, desc_element, multiple = True)
                answer = self.galleryControl.updateData(descrip_cname, descrip_data)
                print(" ======================= REPORT ========================= ")
                print(answer)

            elif int(inputs) == 6:
                print("Composing download data for the gallery pictures (DOWNLOAD_URL)...")
                urlpic_data = self.galleryControl.scrapPagePicture(colurl_cname, vincent_root, pic_div, pic_attrs, pic_elements, multiple = False)
                answer = self.galleryControl.updateData(donwload_cname, urlpic_data)
                print(" ======================= REPORT ========================= ")
                print(answer)

            elif int(inputs) == 7:
                print("Downloading the the gallery pictures and check-in its existence in the model (HAS_PICTURE)...")
                urlpic_data = self.galleryControl.getData(donwload_cname)
                haspic_data = self.galleryControl.downloadPictures(urlpic_data, self.galleryControl.localGallery)
                answer = self.galleryControl.updateData(haspic_cname, haspic_data)
                print(" ======================= REPORT ========================= ")
                print(answer)

            elif int(inputs) == 8:
                print("Composing collection search tags data for the gallery pictures (SEARCH_TAGS)...")
                search_data = self.galleryControl.scrapPageSearchTags(colurl_cname, vincent_root, search_div, search_attrs, search_elements, multiple = True)
                answer = self.galleryControl.updateData(search_cname, search_data)
                print(" ======================= REPORT ========================= ")
                print(answer)

            elif int(inputs) == 9:
                print("Composing collection object data for the gallery pictures (OBJ_DATA)...")
                object_data = self.galleryControl.scrapPageObjData(colurl_cname, object_div, object_attrs, object_elements, multiple = False)
                answer = self.galleryControl.updateData(object_cname, object_data)
                print(" ======================= REPORT ========================= ")
                print(answer)

            elif int(inputs) == 10:
                print("Composing related work data for the gallery pictures (RELATED_WORKS)...")
                # authorname = input("Nombre del autor a buscar: ")
                relatedw_data = self.galleryControl.scrapPageRelWork(colurl_cname, vincent_root, relatedw_div, relatedw_attrs, relatedw_elements, multiple = True)
                answer = self.galleryControl.updateData(relatedw_cname, relatedw_data)
                print(" ======================= REPORT ========================= ")
                print(answer)

            elif int(inputs) == 11:
                print("Exporting to JSON format the DataFrame (CSV to local gallery)...")

                # JSON export for desccription, search tags, object date and related work
                for temp_cname in json_index_columns:
                    self.galleryControl.exportToJSON(self.galleryControl.localGallery, id_cname, temp_cname, temp_cname.lower())


                answer = self.galleryControl.checkGallery()
                print(" =======================  REPORT ========================= ")
                print(answer)

            # elif int(inputs) == 12:
            #     print("Composing literature data related to the gallery pictures (LITERATURE)...")
            #     # authorname = input("Nombre del autor a buscar: ")

            #     lit_data = None
            #     answer = self.galleryControl.updateData(lit_cname, lit_data)
            #     print(" =======================  REPORT ========================= ")
            #     print(answer)

            elif int(inputs) == 0:
                sys.exit(0)

            else:
                print("Invalid option, please try again...")

if __name__ == "__main__":

    """
    creating the View() object and running it
    """
    scrapy = View()
    scrapy.run()
