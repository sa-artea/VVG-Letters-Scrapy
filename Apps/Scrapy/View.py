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
from .Controller import Controller

"""
The view is in charge of the interaction with the user
selecting the options to scrap the web and load the data
into the CSV files.
"""

# ___________________________________________________
#  data input
# ___________________________________________________

# URL for the webpage to recover the paintings
galleryPage = "https://www.vangoghmuseum.nl/en/collection?q=&Artist=Vincent+van+Gogh"

# local root dirpath where the data will be save
localGallery = "C:\\Users\\Felipe\\Universidad de los andes\\CoIArt - General\\04 - Data\\01 - Vincent\\01 - Raw"

# real rootpath to work with
workPath = localGallery
workPath = os.path.dirname(workPath)

# subdirs in the local root path needed to process data
paintsFolder = "01 - Paints"
lettersFolder = "02 - Letters"
# scrapped subfolder
rawFolder = "01 - Raw"


#La ruta se obtiene con el dirpath y el filename y el dirpath.split(os.path.sep)[-1] agrega la clase

# ___________________________________________________
#  Functions to print webpage recovered data
# ___________________________________________________

class View(object):
    """[summary]

    Args:
        object ([type]): [description]
    """

    galleryControl = Controller()
    galleryLocalPath = ""
    galleryPage = ""

    def __init__(self, *args, **kwargs):
        
        self.galleryControl = Controller()

    def printMenu(self):
        """
        menu options
        """
        print("===== WELCOME =====")
        print("1- Start gallery")
        print("2- Load paintings in gallery")
        print("3- Update paintings basic data")
        print("4- other ffuncionality XXXXXXX")
        print("5- other ffuncionality XXXXXXX")
        print("6- other ffuncionality XXXXXXX")
        print("7- other ffuncionality XXXXXXX")
        print("8- other ffuncionality XXXXXXX")
        print("9- Save gallery data")
        print("0- EXIT")


    def run(self):
        """menu excution
        """
        while True:
            self.printMenu()
            inputs = input('Select an option to continue\n')

            if int(inputs[0]) == 1:
                print("Starting gallery...")
                galleryControl = Controller(galleryPage, 
                                                localGallery,
                                                paintsFolder,
                                                rawFolder)
                # # cont es el controlador que se usará de acá en adelante
                # cont = controller.initCatalog()
                galleryControl.gallerySetUp()

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
