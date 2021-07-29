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
# =======================================================
# native python libraries
# =======================================================
import sys
import re
import os
import copy

# =======================================================
# extension python libraries
# =======================================================
# NONE IN VIEW

# =======================================================
# developed python libraries
# =======================================================
import Conf
from App.Controller import Controller
from App.Model import Gallery
assert Controller
assert Gallery
assert Conf
assert re

# =======================================================
#  Global data config
# =======================================================

CFG_FOLDER = "Config"
CFG_APP = "app-config.ini"
CFG_SCHEMA = "df-schema.ini"
CFG_WEB_TAGS = "html-tags.ini"
CFG_DATA_APP = Conf.configGlobal(CFG_FOLDER, CFG_APP)

# url query for VVG gallery request
# vvg_search = CFG_DATA_APP.get("Requests", "small")
vvg_search = CFG_DATA_APP.get("Requests", "large")
# vvg_search = CFG_DATA_APP.get("Requests", "extensive")

print("=================== Config INI Gallery Search ===================")
print(str(vvg_search) + "\n\n")

# root URL of the gallery
vvg_url = CFG_DATA_APP.get("Requests", "root")

# local root dirpath where the data CHANGE IN .INI!!!!
vvg_localpath = CFG_DATA_APP.get("Paths", "localPath")

# real rootpath to work with
galleryf = os.path.normpath(vvg_localpath)
print("================== Config INI Local Path Gallery ==================")
print(galleryf)
print(os.path.isdir(vvg_localpath))

# subdirs in the local root path needed to process data
artworksf = CFG_DATA_APP.get("Paths", "artworksFolder")
lettersf = CFG_DATA_APP.get("Paths", "lettersFolder")

# scrapped subfolder
srcf = CFG_DATA_APP.get("Paths", "sourceFolder")

# app subfoder
dataf = CFG_DATA_APP.get("Paths", "dataFolder")
imgf = CFG_DATA_APP.get("Paths", "imageFolder")

# cresting the export file for the data
bfn = CFG_DATA_APP.get("ExportFiles", "basicfile")
fext = CFG_DATA_APP.get("ExportFiles", "fext")

# change according to the request in the .INI!!!!
# fsize = CFG_DATA_APP.get("ExportFiles", "small")
fsize = CFG_DATA_APP.get("ExportFiles", "large")
# fsize = CFG_DATA_APP.get("ExportFiles", "extensive")

expf = bfn + fsize + "." + fext
print("================== Config INI Export File Name ==================")
print(str(expf) + "\n\n")

# loading config schema into the program
dfschema = Conf.configGlobal(CFG_FOLDER, CFG_SCHEMA)

# setting schema for the element/paint gallery dataframe
VVG_DF_COLS = eval(dfschema.get("DEFAULT", "columns"))

# column names for creating a new index and model in the program
# WC = VVG_DF_COLS[VVG_DF_COLS.index(
# "ID"):VVG_DF_COLS.index("COLLECTION_URL")+1]
#index_start_cols = copy.deepcopy(WC)

print("================== Columns for a new DF-Schema ==================")
#print(index_start_cols, "\n")

# column names for creating the JSON in the folders
json_index_cols = copy.deepcopy(VVG_DF_COLS[VVG_DF_COLS.index(
    "ID"):VVG_DF_COLS.index("LOCATION")+1])

print("================= JSON Columns in the DF-Schema =================")
#print(json_index_cols, "\n")

# =======================================================
#  data input to start creating index and scraping
# =======================================================

# dummy vars for the index of the dataframe
id_col = str(VVG_DF_COLS[VVG_DF_COLS.index("ID")])
title_col = str(VVG_DF_COLS[VVG_DF_COLS.index("TITLE")])
author_col = str(VVG_DF_COLS[VVG_DF_COLS.index("AUTHOR")])
addressee_col = str(VVG_DF_COLS[VVG_DF_COLS.index("ADDRESSEE")])
date_col = str(VVG_DF_COLS[VVG_DF_COLS.index("DATE")])
location_col = str(VVG_DF_COLS[VVG_DF_COLS.index("LOCATION")])
original_col = str(VVG_DF_COLS[VVG_DF_COLS.index("ORIGINAL")])
translation_col = str(VVG_DF_COLS[VVG_DF_COLS.index("TRANSLATION")])
notes_col = str(VVG_DF_COLS[VVG_DF_COLS.index("NOTES")])
artworks_title_col = str(VVG_DF_COLS[VVG_DF_COLS.index("ARTWORKSTITLE")])
artworks_f_col = str(VVG_DF_COLS[VVG_DF_COLS.index("ARTWORKSF")])
artworks_jh_col = str(VVG_DF_COLS[VVG_DF_COLS.index("ARTWORKSJH")])
artworks_link_col = str(VVG_DF_COLS[VVG_DF_COLS.index("ARTWORKSLINK")])
artworks_id_col = str(VVG_DF_COLS[VVG_DF_COLS.index("ARTWORKSID")])
url_col = str(VVG_DF_COLS[VVG_DF_COLS.index("URL")])


class View():
    """
    the View is the console interface for the program, connect to the
    Model() with the Controller()

    The view is in charge of the interaction with the user selecting
    the options to scrap the web and load the data into the CSV files.
    """
    # ====================================================
    # class variables
    # ====================================================
    gallery_controller = Controller()
    gallery_model = Gallery()
    localg_path = str()
    imgd_path = str()
    webg_path = str()
    schema = VVG_DF_COLS

    # config file for scraped html tags
    scrapy_cfg = None

    # input variables
    inputs = -1

    def __init__(self, *args):
        """
        Class View creator

        Args:
            webg_path (str): URL of the museum gallery
            localg_path (str): the local directory to save the data
            scrapy_cfg (str): costume INI file with HTML tags to scrap

        Raises:
            exp: raise a generic exception if something goes wrong

        """
        try:
            # generic creation
            self.gallery_model = Gallery()
            self.gallery_controller = Controller()
            self.localg_path = str()
            self.imgd_path = str()
            self.webg_path = str()
            self.schema = copy.deepcopy(VVG_DF_COLS)
            self.scrapy_cfg = Conf.configGlobal(CFG_FOLDER, CFG_WEB_TAGS)
            self.inputs = -1

            # if args parameters are input in the creator
            if len(args) > 0:

                for i in range(0, len(args)-1):
                    if i == 0:
                        self.webg_path = args[i]

                    if i == 1:
                        self.localg_path = args[i]

                    if i == 2:
                        self.imgd_path = args[i]

                    if i == 3:
                        self.scrapy_cfg = Conf.configGlobal(args[i])

                wg = self.webg_path
                gp = self.localg_path
                ip = self.imgd_path
                mod = self.gallery_model
                self.gallery_model = Gallery(wg, gp, ip)
                sch = self.schema
                self.gallery_controller = Controller(wg, gp, ip,
                                                     model=mod,
                                                     schema=sch)

        # exception handling
        except Exception as exp:
            raise exp

    def menu(self):
        """
        menu options console display

        Raises:
            exp: raise a generic exception if something goes wrong
        """

        try:
            print("\n====================== WELCOME ======================\n")
            # create a new index based in the root url
            print("1) Scrap the letters ids from the VVG Gallery and their URLs")
            # save in files all the scrapped data
            print("2) Save Gallery data (saving into *.CSV)")
            # load preavious scraped data into model
            print("3) Load Gallery data (loading from *.CSV)")
            # load preavious scraped data into model
            print("4) Check Gallery data (reading current *.CSV)")
            # recovers the basic data from the gallery query
            print(
                "5) Get Gallery elements metadata (TITLE, AUTHOR, ADDRESSEE, DATE, LOCATION)")
            # complement the basic data created from option 6) and 12)
            print("6) Get Gallery elements original text (ORIGINAL)")
            print("7) Get Gallery elements translation text (TRANSLATION)")
            print("8) Get Gallery elements notes (NOTES)")
            print("9) Get Gallery elements artworks (ARTWORKSTITLE, ARTWORKSF, ARTWORKSJH, ARTWORKSLINK, ARTWORKSID)")
            print("10) Download Gallery elements artworks images")
            print("11) Export DataFrame to JSON Files (from CSV to Local dir)")
            print("99) Auto script for options (3, 4, 5, 6, 7, 8, 9, 10, 11)")
            print("0) EXIT (last option)")
            # finish program

        # exception handling
        except Exception as exp:
            raise exp

    def setup(self):
        """
        Configuring the view class in the main

        Raises:
            exp: print the exception and restart the setup() method
        """
        try:
            # setting gallery base webpage
            self.webg_path = vvg_search
            gf = galleryf
            sf = srcf
            lf = lettersf
            cf = os.getcwd()
            df = dataf
            igf = artworksf

            # setting up local dir for saving data
            self.localg_path = self.gallery_controller.setup_local(gf, sf, lf)
            self.imgd_path = self.gallery_controller.setup_local(cf, df, igf)
            print("============== Creating the Gallery View ==============")
            print("View gallery localpath: " + str(self.localg_path))
            print("View images localpath: " + str(self.imgd_path))
            print("View gallery Web URL: " + str(self.webg_path))
            print("\n")

            # creating the gallery model
            wg = self.webg_path
            gp = self.localg_path
            ip = self.imgd_path
            vdfc = VVG_DF_COLS

            self.gallery_model = Gallery(wg, gp, ip, schema=vdfc)
            print("============== Creating Gallery Model ==============")
            print("Model gallery localpath: " +
                  str(self.gallery_model.localg_path))
            print("Model images localpath: " +
                  str(self.gallery_model.imgd_path))
            print("Model gallery Web URL: " +
                  str(self.gallery_model.webg_path))
            print("\n")

            gm = self.gallery_model

            # creating the gallery controller
            self.gallery_controller = Controller(wg, gp, ip,
                                                 model=gm,
                                                 schema=vdfc)
            print("============ Crating Gallery Controller ============")
            print("Controller gallery localpath: " +
                  str(self.gallery_controller.localg_path))
            print("Controller images localpath: " +
                  str(self.gallery_controller.imgd_path))
            print("Controller Web gallery URL: " +
                  str(self.gallery_controller.webg_path))
            print("\n")

        # exception handling
        except Exception as exp:
            print(exp)
            self.setup()

    def one(self, *args):
        """
        Scrap the links/routes of the letters in the VVG letters page.

        Args:
            vvg_url (str): web gallery URL search for the collection

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            print("Starting a new Gallery (ID, URL)")
            print("...")
            gc = self.gallery_controller
            gp = self.localg_path
            gc = self.gallery_controller

            routes = gc.scrap_routes(args[0])
            print("Gallery IDs were processed...")
            links = gc.build_links(routes)
            print("Gallery collection URLs were processed...")
            data = (routes, links)
            ans = gc.newdf(args[1:], data)
            print("New Gallery Model was created...")
            gc.create_localfolders(gp, args[1])
            print("Local Gallery folders were created...")
            return ans
        except Exception as exp:
            raise exp

    def two(self, *args):
        """
        Option 2, saves the in-memory data into CSV and creates the
        local dirpath for the files if it doesnt exists

        Args:
            expf (str): export file name, Default CSV
            dataf (str): data folder name for the app

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): boolean to confirm success of the task
        """
        try:
            print("Saving gallery Model into CSV file...")
            gc = self.gallery_controller
            ans = gc.save_gallery(args[0], args[1])
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def three(self, *args):
        """
        Option 3, loads the in memory of the CSV data and creates the
        local dirpath for the files if it doesnt exists

        Args:
            id_col (str): df-schema column name of the ID
            expf (str): export file name, Default CSV
            dataf (str): data folder name for the app

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): boolean to confirm success of the task
        """
        try:
            print("Loading Gallery CSV file into Model...")

            gc = self.gallery_controller
            gp = self.localg_path
            ans = gc.load_gallery(args[0], args[1])
            gc.create_localfolders(gp, args[2])
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def four(self):
        """
        Option 4, checks the in memory dataframe

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            print("Checking Gallery Model status (dataframe from CSV)")
            gc = self.gallery_controller
            gc.check_gallery()

        # exception handling
        except Exception as exp:
            raise exp

    def five(self, *args):
        """
        Option 5, based on the results of option 1, it scrap the
        metadata of each URL gallery element

        Args:
            vvg_url (str): web gallery URL search for the collection
            id_col (str): df-schema column name of the ID
            metadata_cols (list): list with the df-schema column names of TITLE, 
            AUTHOR, ADDRESSEE, DATE, LOCATION
        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): boolean to confirm success of the task
        """
        try:
            print(
                "Recovering elements metadata (TITLE, AUTHOR, ADDRESSEE, DATE, LOCATION)")
            gc = self.gallery_controller
            meta_data = gc.scrap_metadata(*args)
            ans = True
            for col in args[2]:
                ans = ans and gc.updata(col, meta_data[col])
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def six(self, *args):
        """
        Option 6, based on the results of option 1, it scrap the original text of 
        all the letters in the VVG letters page.

        Args:
            vvg_url (str): web gallery URL search for the collection
            id_col (str): df-schema column name of the ID
            original_col (str): df-schema column name of the ORIGINAL 

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            print("Recovering elements original text (ORIGINAL)")
            gc = self.gallery_controller
            original_texts = gc.scrap_original_texts(args[0], args[1])
            ans = gc.updata(args[2], original_texts)
            return ans

        except Exception as exp:
            raise exp

    def seven(self, *args):
        """
        Option 7, based on the results of option 1, it scrap the translation text of 
        all the letters in the VVG letters page.

        Args:
            vvg_url (str): web gallery URL search for the collection
            id_col (str): df-schema column name of the ID
            translation_col (str): df-schema column name of the TRANSLATION 

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            print("Recovering elements translation text (TRANSLATION)")
            gc = self.gallery_controller
            translation_texts = gc.scrap_translation_texts(args[0], args[1])
            ans = gc.updata(args[2], translation_texts)
            return ans
        except Exception as exp:
            raise exp

    def eight(self, *args):
        """
        Option 8, based on the results of option 1, it scrap the text of the notes of 
        all the letters in the VVG letters page.

        Args:
            vvg_url (str): web gallery URL search for the collection
            id_col (str): df-schema column name of the ID
            notes_col (str): df-schema column name of the NOTES 

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            print("Recovering elements notes text (NOTES)")
            gc = self.gallery_controller
            notes_texts = gc.scrap_notes_texts(args[0], args[1])
            ans = gc.updata(args[2], notes_texts)
            return ans
        except Exception as exp:
            raise exp

    def nine(self, *args):
        """
        Option 9, based on the results of option 1, it scrap the artworks related to 
        all the letters in the VVG letters page.

        Args:
            vvg_url (str): web gallery URL search for the collection
            id_col (str): df-schema column name of the ID
            artworks_cols (list): list with the df-schema column names of ARTWORKSTITLE, 
            ARTWORKSF, ARTWORKSJH, ARTWORKSLINK, ARTWORKSID

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            print(
                "Recovering elements artworks (ARTWORKSTITLE, ARTWORKSF, ARTWORKSJH, ARTWORKSLINK, ARTWORKSID)")
            gc = self.gallery_controller
            artworks = gc.scrap_artworks(*args)
            ans = True
            for col in args[2]:
                ans = ans and gc.updata(col, artworks[col])
            return ans
        except Exception as exp:
            raise exp

    def ten(self, *args):
        """
        Option 10, based on the results of option 1 and option 9, it downloads the artworks related to 
        all the letters in the VVG letters page.

        Args:
            vvg_url (str): web gallery URL search for the collection
            id_col (str): df-schema column name of the ID
            artworks_link_col (str): df-schema column name of the artworks_links
            artworks_id_col (str): df-schema column name of the artworks_ids
            artworks_path (str): path to save artworks paintings

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            print("Downloading artworks paintings")
            gc = self.gallery_controller
            ans = gc.get_artworks_images(*args)
            return ans

        except Exception as exp:
            raise exp

    def eleven(self, *args):  # TAMBIÉN FALTA
        """
        Option 11, export all scraped columns into JSON file in the
        designated local folders

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            print("Exporting pandas-df to JSON in local gallery")

            gc = self.gallery_controller
            gp = self.localg_path

            # JSON export for the following columns:
            # - desccription
            # - search tags
            # - object date
            # - related work
            for temp_cname in args[1]:
                gc.export_json(
                    gp,
                    args[0],
                    temp_cname,
                    temp_cname.lower())

        # exception handling
        except Exception as exp:
            raise exp

    def printre(self, report):
        """
        prints the report tittle in the console

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            print("=================== REPORT ===================")
            print("TASK COMPLETED: ", report)

        # exception handling
        except Exception as exp:
            raise exp

    def run(self):
        """
        Running the view class in the main

        Raises:
            exp: print the exception and restart the self.run() method
        """
        try:

            while True:
                self.menu()
                inp = self.inputs
                ans = False

                # known if the is auto or manual input
                if inp < 0:
                    inp = input("Select an option to continue\n")

                # starting a new gallery
                if int(inp) == 1:
                    ans = self.one(vvg_url, id_col, url_col)

                # saving gallery in file
                elif int(inp) == 2:
                    ans = self.two(expf, dataf)

                # loading gallery in memory
                elif int(inp) == 3:
                    ans = self.three(expf, dataf, id_col)

                # checking gallery in memory
                elif int(inp) == 4:
                    self.four()
                    ans = True

                # recovering letter metadata
                elif int(inp) == 5:
                    metadata_cols = [title_col, author_col,
                                     addressee_col, date_col, location_col]
                    ans = self.five(vvg_url, id_col, metadata_cols)

                # recovering letter original text
                elif int(inp) == 6:
                    ans = self.six(vvg_url, id_col, original_col)

                # recovering letter translation text
                elif int(inp) == 7:
                    ans = self.seven(vvg_url, id_col, translation_col)

                # recovering letter notes text
                elif int(inp) == 8:
                    ans = self.eight(vvg_url, id_col, notes_col)

                # recovering letter artworks
                elif int(inp) == 9:
                    artworks_cols = [artworks_title_col, artworks_f_col, artworks_jh_col, artworks_link_col,
                                     artworks_id_col]
                    ans = self.nine(vvg_url, id_col, artworks_cols)

                elif int(inp) == 10:
                    ans = self.ten(vvg_url, id_col, artworks_link_col,
                                   artworks_id_col, vvg_localpath)

                # exporting CSV columns into JSON foles
                elif int(inp) == 11:
                    self.eleven(id_col, json_index_cols)
                    ans = True

                elif int(inp) == 99:
                    # list of automatic steps
                    # (3, 4, 2, 5, 2, 6, 2, 7, 2, 8, 2, 9, 2, 10, 11, 2)
                    print("Auto executing options 3 to 11!!!...")
                    ans = True
                    ans = ans and self.three(expf, dataf, id_col)

                    metadata_cols = [title_col, author_col,
                                     addressee_col, date_col, location_col]
                    ans = ans and self.five(vvg_url, id_col, metadata_cols)
                    ans = ans and self.two(expf, dataf)

                    ans = ans and self.six(vvg_url, id_col, original_col)
                    ans = ans and self.two(expf, dataf)

                    ans = ans and self.seven(vvg_url, id_col, translation_col)
                    ans = ans and self.two(expf, dataf)

                    ans = ans and self.eight(vvg_url, id_col, notes_col)
                    ans = ans and self.two(expf, dataf)

                    artworks_cols = [artworks_title_col, artworks_f_col, artworks_jh_col, artworks_link_col,
                                     artworks_id_col]
                    ans = ans and self.nine(vvg_url, id_col, artworks_cols)
                    ans = ans and self.two(expf, dataf)

                    ans = ans and self.ten(
                        vvg_url, id_col, artworks_link_col, artworks_id_col, vvg_localpath)

                    self.eleven(id_col, json_index_cols)
                    ans = self.two(expf, dataf)

                    self.inputs = -1

                # exit program
                elif int(inp) == 0:
                    sys.exit(0)

                # other option selected
                else:
                    print("Invalid option, please try again...")

                # printing report after finishing task
                self.printre(ans)

        # exception handling
        except Exception as exp:
            print(exp)
            self.run()


# main of the program
if __name__ == "__main__":
    # creating the View() object and running it
    scrapy = View()
    scrapy.setup()
    scrapy.run()
