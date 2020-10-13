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
import config
from Apps.Scrapy.controller import Controller
from Apps.Scrapy.model import Gallery
assert Controller
assert Gallery
assert config

"""
The view is in charge of the interaction with the user
selecting the options to scrap the web and load the data
into the CSV files.
"""

# ___________________________________________________
#  data input
# ___________________________________________________

# URL for the webpage to recover the paintings
# galleryPage = "https://www.vangoghmuseum.nl/en/collection?q=&Artist=Vincent+van+Gogh"
# vincent_page = "https://www.vangoghmuseum.nl/en/collection?q=&Artist=Vincent+van+Gogh&Type=trial+proof%2Cstudy%2Cprint%2Csketch%2Cdrawing%2Cpainting"
# url query excluding the written part of the letters
# galleryPage = "https://www.vangoghmuseum.nl/en/collection?q=&Artist=Vincent+van+Gogh&Type=painting%2Cprint%2Csketch%2Cdrawing%2Cletter+sketch%2Cstudy%2Ctrial+proof"
vincent_page = "https://www.vangoghmuseum.nl/en/collection?q=&Artist=Vincent+van+Gogh&Type=study"
vincent_root = "https://vangoghmuseum.nl"

# local root dirpath where the data will be save
vincent_localpath = "C:\\Users\\Felipe\\Universidad de los andes\\CoIArt - General\\04 - Data\\01 - Vincent\\Source"

# real rootpath to work with
galleryFolder = os.path.dirname(vincent_localpath)

# subdirs in the local root path needed to process data
paintsFolder = "Paints"
lettersFolder = "Letters"
# scrapped subfolder
sourceFolder = "Source"
# app subfoder
dataFolder = "Data"

# default template for the element/paint dict in gallery
VINCENT_DF_COLUMNS = [
    "ID",                   # unique ID for an element in the gallery, its also its folder name in the localdir
    "TITLE",                # tittle of the element inside the gallery
    "COLLECTION_URL",       # element (paint) URL/link recovered with ScrapyWEB
    "DOWNLOAD_URL",         # direct image URL/link for the image in the gallery
    "DESCRIPTION",          # JSON cell with the description of the element in the gallery
    "SEARCH_TAGS",          # JSON cell with the collection tags of the element in the gallery
    "OBJ_DATA",             # JSON cell with the museum object data of the element in the gallery
    "RELATED_WORKS",        # JSON cell with the related work text and URLs of the element in the gallery
    "EXHIBITIONS",          # JSON cell with the list of the exhibitions were the element in the gallery has been displayed
    "LITERATURE",           # JSON cell with the list of the literatire references for the gallery elements

    "HAS_ID",               # boolean indicating if the paint has a folder on the localdir
    "HAS_TITLE",            # boolean indicating if the paint has a tittle in the gallery
    "HAS_DESCRIPTION",      # booleano que identifica si se tiene la seccion de descripcion en el HTML del elemento
    "HAS_DOWNLOAD",         # booleano que identifica si se tiene la seccion de enlace de descarga en el HTML del elemento
    "HAS_TAGS",             # booleano que identifica si se tiene la seccion de tags de busqueda en el HTML del elemento
    "HAS_DATA",             # booleano que identifica si se tiene la seccion de datos de archivo en el HTML del elemento
    "HAS_RELATEDW",         # booleano que identifica si se tiene la seccion de trabajo relacionado en el HTML del elemento
    "HAS_EXHIBIT",          # booleano que identifica si se tiene la seccion de trabajo relacionado en el HTML del elemento
    "HAS_LIT",              # booleano que identifica si se tiene la seccion de trabajo relacionado en el HTML del elemento

    "ERR_ID",               # error string for the ID
    "ERR_TITLE",            # error string for the tittle
    "ERR_DESCRIPTION",      # error string for the description
    "ERR_DOWNLOAD",         # error string for the direct download URL
    "ERR_TAGS",             # error string for the collection search tags
    "ERR_DATA",             # error string for the museum object data
    "ERR_RELATEDW",         # error string for the related work
    "ERR_EXHIBIT",          # error string for the exhibition list
    "ERR_LIT",              # error string for the literature reference list
]

# default number of paintings in the gallery
VINCENT_MAX_PAINTS = 25

# ___________________________________________________
#  data input for scrapping the html and creating index
# ___________________________________________________
# html tags for the general object
index_div = "a"
index_attrs = {
    "class": "collection-art-object-wrapper"
}

# html tags for the unique ID in the collection
id_div = "a"
id_element = "href"
id_attrs = {
    "class": "collection-art-object-wrapper",
    "href": re.compile("^/en/collection/")
}

#  html tags for the tittle of the element
title_div = "a"
title_element = "title"
title_attrs = {
    "class": "collection-art-object-wrapper",
    "title": re.compile(".")
}


html_tags = (index_div,
             title_div,
             id_div,
             )

search_attrs = (index_attrs,
                title_attrs,
                id_attrs,
                )

basicColumns = copy.deepcopy(VINCENT_DF_COLUMNS[VINCENT_DF_COLUMNS.index("ID"):VINCENT_DF_COLUMNS.index("COLLECTION_URL")+1])
print(basicColumns)

vincent_collectionAttrs = {"class": "collection-art-object-list-item"}
vincent_downloadAttrs = {"class": "collection-art-object-list-item"}

# ___________________________________________________
#  Functions to print webpage recovered data
# ___________________________________________________
class View(object):
    """[summary]

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
        print("1) Start gallery index") # create a new index based in the root url
        print("2) Save gallery index") #save in files all the scrapped data
        print("3) Load gallery index") # load preavious scraped data into model

        # persists in the model/dataframe the data recovered in option 1)
        print("4) Compose for basic data of the gallery elements (ID, TITLE, COLLECTION_URL)")

        # complement the basic data created from option 1) and 4)
        print("5) Compose for the description and image of the gallery elements (DESCRIPTION, DOWNLOAD_URL)")
        print("6) Compose for the search tags of the gallery elements (SEARCH_TAGS)")
        print("7) Compose for the collection data of the gallery elements (OBJ_DATA)")
        print("8) Compose for the related works of the gallery elements (RELATED_WORKS)")
        print("9) Compose for the exhibition history of the gallery elements EXHIBITIONS)")
        print("10) Compose for the literature references of the gallery elements  (LITERATURE)")
        print("0- EXIT") # finish program

    def run(self):
        """
        menu excution
        """

        # setting gallery base webpage
        self.galleryWEB = vincent_page
        
        # setting up local dir for saving data
        self.localGallery = self.galleryControl.SetUpLocal(vincent_localpath, sourceFolder, paintsFolder)
        print("\n== == == == == == == \n" + "Setting local working folders in:\n" + str(self.localGallery) + "\n== == == == == == == \n")

        # creating the gallery model
        self.galleryModel = Gallery(self.galleryWEB, self.localGallery, schema = VINCENT_DF_COLUMNS, size = VINCENT_MAX_PAINTS)
        print("== == == == == == == Crating the gallery model == == == == == == ==")

        # creating the gallery controller
        self.galleryControl = Controller(self.galleryWEB, self.localGallery, self.galleryModel, schema = VINCENT_DF_COLUMNS, size = VINCENT_MAX_PAINTS)
        print("== == == == == == == Crating the gallery controller == == == == == == ==")

        while True:
            self.menu()
            inputs = input('Select an option to continue\n')

            # starting gallery object to scrap data
            if int(inputs[0]) == 1:
                print("Starting new gallery index...")
                
                # starting the gallery index
                galleryIndex = self.galleryControl.scrapIndex(self.galleryWEB, 5, id_div, id_attrs)
                id_data = self.galleryControl.getID(galleryIndex, id_element)
                galleryIndex = self.galleryControl.scrapAgain(title_div, title_attrs)
                title_data = self.galleryControl.getTitle(galleryIndex, title_element)
                galleryIndex = self.galleryControl.scrapAgain(id_div, id_attrs)
                link_data = self.galleryControl.getURL(galleryIndex, vincent_root, id_element)

                print(len(id_data), len(title_data), len(link_data))
                for idt, title, link in zip(id_data, title_data, link_data):
                    print("================================================")
                    print(idt)
                    print(title)
                    print(link)


            elif int(inputs[0]) == 2:
                print("loading new paintings into gallery...")
                # print("Cargando información de los archivos ....")
                # controller.loadData(cont, booksfile, tagsfile, booktagsfile)
                # print('Libros cargados: ' + str(controller.booksSize(cont)))
                # print('Autores cargados: ' + str(controller.authorsSize(cont)))
                # print('Géneros cargados: ' + str(controller.tagsSize(cont)))

            elif int(inputs[0]) == 3:
                print("Updating paintings...")

                # number = input("Buscando libros del año?: ")
                # books = controller.getBooksYear(cont, int(number))
                # printBooksbyYear(books)

            elif int(inputs[0]) == 4:
                print("function not yet implemented!!!")
                # authorname = input("Nombre del autor a buscar: ")
                # authorinfo = controller.getBooksByAuthor(cont, authorname)
                # printAuthorData(authorinfo)

            elif int(inputs[0]) == 5:
                print("function not yet implemented!!!")
                # authorname = input("Nombre del autor a buscar: ")
                # authorinfo = controller.getBooksByAuthor(cont, authorname)
                # printAuthorData(authorinfo)

            elif int(inputs[0]) == 6:
                print("gitfunction not yet implemented!!!")
                # authorname = input("Nombre del autor a buscar: ")
                # authorinfo = controller.getBooksByAuthor(cont, authorname)
                # printAuthorData(authorinfo)

            elif int(inputs[0]) == 7:
                print("function not yet implemented!!!")
                # authorname = input("Nombre del autor a buscar: ")
                # authorinfo = controller.getBooksByAuthor(cont, authorname)
                # printAuthorData(authorinfo)

            elif int(inputs[0]) == 8:
                print("function not yet implemented!!!")
                # authorname = input("Nombre del autor a buscar: ")
                # authorinfo = controller.getBooksByAuthor(cont, authorname)
                # printAuthorData(authorinfo)

            elif int(inputs[0]) == 9:
                print("Saving new painting information into gallery files...")
                # authorname = input("Nombre del autor a buscar: ")
                # authorinfo = controller.getBooksByAuthor(cont, authorname)
                # printAuthorData(authorinfo)

            else:
                sys.exit(0)
        sys.exit(0)

if __name__ == "__main__":

    """
    creating the View() object and running it
    """
    scrapy = View()
    scrapy.run()


#     def __init__(self, master):
#         tk.Toplevel.__init__(self, master)
#         self.protocol('WM_DELETE_WINDOW', self.master.destroy)
#         tk.Label(self, text='My Money').pack(side='left')
#         self.moneyCtrl = tk.Entry(self, width=8)
#         self.moneyCtrl.pack(side='left')

#     def SetMoney(self, money):
#         self.moneyCtrl.delete(0, 'end')
#         self.moneyCtrl.insert('end', str(money))


# class ChangerWidget(tk.Toplevel):
#     def __init__(self, master):
#         tk.Toplevel.__init__(self, master)
#         self.addButton = tk.Button(self, text='Add', width=8)
#         self.addButton.pack(side='left')
#         self.removeButton = tk.Button(self, text='Remove', width=8)
#         self.removeButton.pack(side='left')
