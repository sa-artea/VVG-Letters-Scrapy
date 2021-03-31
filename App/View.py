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

"""
The view is in charge of the interaction with the user
selecting the options to scrap the web and load the data
into the CSV files.
"""

# =======================================================
#  Global data config
# =======================================================

cfgFolder = "Config"
cfgApp = "app-config.ini"
cfgSchema = "df-schema.ini"
cfgWebTags = "html-tags.ini"
dataApp = Conf.configGlobal(cfgFolder, cfgApp)

# url query for VVG gallery request
vvg_search = dataApp.get("Requests", "small")
# vvg_search = dataApp.get("Requests", "large")
# vvg_search = dataApp.get("Requests", "extensive")

print("=================== Config INI Gallery Search ===================")
print(str(vvg_search) + "\n\n")

# root URL of the gallery
vvg_url = dataApp.get("Requests", "root")

# local root dirpath where the data CHANGE IN .INI!!!!
vvg_localpath = dataApp.get("Paths", "localPath")

# real rootpath to work with
galleryf = os.path.normpath(vvg_localpath)
print("================== Config INI Local Path Gallery ==================")
print(galleryf)
print(os.path.isdir(vvg_localpath))

# subdirs in the local root path needed to process data
paintf = dataApp.get("Paths", "paintsFolder")
lettersf = dataApp.get("Paths", "lettersFolder")

# scrapped subfolder
srcf = dataApp.get("Paths", "sourceFolder")

# app subfoder
dataf = dataApp.get("Paths", "dataFolder")
imgf = dataApp.get("Paths", "imageFolder")

# cresting the export file for the data
bfn = dataApp.get("ExportFiles", "basicfile")
fext = dataApp.get("ExportFiles", "fext")

# change according to the request in the .INI!!!!
fsize = dataApp.get("ExportFiles", "small")
# fnsize = dataApp.get("ExportFiles", "large")
# fnsize = dataApp.get("ExportFiles", "extensive")

expf = bfn + fsize + "." + fext
print("================== Config INI Export File Name ==================")
print(str(expf) + "\n\n")

# loading config schema into the program
dfschema = Conf.configGlobal(cfgFolder, cfgSchema)

# setting schema for the element/paint gallery dataframe
VVG_DF_COLS = eval(dfschema.get("DEFAULT", "columns"))

# column names for creating a new index and model in the program
WC = VVG_DF_COLS[VVG_DF_COLS.index(
    "ID"):VVG_DF_COLS.index("COLLECTION_URL")+1]
index_start_cols = copy.deepcopy(WC)

print("================== Columns for a new DF-Schema ==================")
print(index_start_cols, "\n")

# column names for creating the JSON in the folders
json_index_cols = copy.deepcopy(VVG_DF_COLS[VVG_DF_COLS.index(
    "DESCRIPTION"):VVG_DF_COLS.index("RELATED_WORKS")+1])

print("================= JSON Columns in the DF-Schema =================")
print(json_index_cols, "\n")

# =======================================================
#  data input to start creating index and scraping
# =======================================================

# dummy vars for the index of the dataframe
id_col = str(VVG_DF_COLS[VVG_DF_COLS.index("ID")])
title_col = str(VVG_DF_COLS[VVG_DF_COLS.index("TITLE")])
curl_col = str(VVG_DF_COLS[VVG_DF_COLS.index("COLLECTION_URL")])
dl_col = str(VVG_DF_COLS[VVG_DF_COLS.index("DOWNLOAD_URL")])
haspic_col = str(VVG_DF_COLS[VVG_DF_COLS.index("HAS_PICTURE")])
desc_col = str(VVG_DF_COLS[VVG_DF_COLS.index("DESCRIPTION")])
search_col = str(VVG_DF_COLS[VVG_DF_COLS.index("SEARCH_TAGS")])
obj_col = str(VVG_DF_COLS[VVG_DF_COLS.index("OBJ_DATA")])
rwork_col = str(VVG_DF_COLS[VVG_DF_COLS.index("RELATED_WORKS")])
img_col = str(VVG_DF_COLS[VVG_DF_COLS.index("IMG_DATA")])
shape_col = str(VVG_DF_COLS[VVG_DF_COLS.index("IMG_SHAPE")])

# list with steps for dataframe automatic generator
AUTO_LIST = (3, 4, 5, 6, 2, 7, 2, 8, 2, 9, 2, 10, 2, 11, 12)


class View(object):
    """
    the View is the console interface for the program, connect to the Model()
    with the Controller()
    """
    # ====================================================
    # class variables
    # ====================================================
    galleryControl = Controller()
    galleryModel = Gallery()
    galleryPath = str()
    imagesPath = str()
    webGallery = str()
    schema = VVG_DF_COLS

    # config file for scraped html tags
    scrapyCfg = None

    # input variables
    inputs = -1

    def __init__(self, *args, **kwargs):
        """
        Class View creator

        Args:
            webGallery (str, optional): URL of the museum gallery
            galleryPath (str, optional): the local directory to save the data
            scrapyCfg (str, optional): costume INI file with HTML tags to scrap

        Raises:
            exp: raise a generic exception if something goes wrong

        """
        try:
            # generic creation
            self.galleryModel = Gallery()
            self.galleryControl = Controller()
            self.galleryPath = str()
            self.imagesPath = str()
            self.webGallery = str()
            self.schema = copy.deepcopy(VVG_DF_COLS)
            self.scrapyCfg = Conf.configGlobal(cfgFolder, cfgWebTags)
            self.inputs = -1

            # if args parameters are input in the creator
            if len(args) > 0:

                for i in range(0, len(args)-1):
                    if i == 0:
                        self.webGallery = args[i]

                    if i == 1:
                        self.galleryPath = args[i]

                    if i == 2:
                        self.imagesPath = args[i]

                    if i == 3:
                        self.scrapyCfg = Conf.configGlobal(args[i])

                wg = self.webGallery
                gp = self.galleryPath
                ip = self.imagesPath
                self.galleryModel = Gallery(wg, gp, ip)
                mod = self.galleryModel
                sch = self.schema
                self.galleryControl = Controller(wg, gp, ip,
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
            print("1) Start gallery index (scrap ID, TITLE & COLLECTION_URL)")
            # save in files all the scrapped data
            print("2) Save gallery data (saving into *.CSV)")
            # load preavious scraped data into model
            print("3) Load gallery data (loading from *.CSV)")
            # load preavious scraped data into model
            print("4) Check gallery data (reading current *.CSV)")
            # recovers the basic data from the gallery query
            print("5) Get Gallery's elements description (DESCRIPTION)")

            # complement the basic data created from option 6) and 12)
            print("6) Get Gallery's elements download URLs (DOWNLOAD_URL)")
            print("7) Download Gallery's elements image files (HAS_PICTURE)")
            print("8) Get Gallery's elements search-tags (SEARCH_TAGS)")
            print("9) Get Gallery's elements collection-data (OBJ_DATA)")
            print("10) Get Gallery's elements related work (RELATED_WORKS)")
            print("11) Process Gallery's images (IMG_DATA, IMG_SHAPE)")
            print("12) Export DataFrame to JSON Files (from CSV to Local dir)")
            print("99) Auto script for options (3, 5, 6, 7, 8, 9, 10, 11, 12)")
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
            self.webGallery = vvg_search
            gf = galleryf
            sf = srcf
            pf = paintf
            cf = os.getcwd()
            df = dataf
            igf = imgf

            # setting up local dir for saving data
            self.galleryPath = self.galleryControl.SetUpLocal(gf, sf, pf)
            self.imagesPath = self.galleryControl.SetUpLocal(cf, df, igf)
            print("============== Creating the Gallery View ==============")
            print("View gallery localpath: " + str(self.galleryPath))
            print("View images localpath: " + str(self.imagesPath))
            print("View gallery Web URL: " + str(self.webGallery))
            print("\n")

            # creating the gallery model
            wg = self.webGallery
            gp = self.galleryPath
            ip = self.imagesPath
            VDFC = VVG_DF_COLS

            self.galleryModel = Gallery(wg, gp, ip, schema=VDFC)
            print("============== Creating Gallery Model ==============")
            print("Model gallery localpath: " +
                  str(self.galleryModel.galleryPath))
            print("Model images localpath: " +
                  str(self.galleryModel.imagesPath))
            print("Model gallery Web URL: " +
                  str(self.galleryModel.webGallery))
            print("\n")

            gm = self.galleryModel

            # creating the gallery controller
            self.galleryControl = Controller(wg, gp, ip, model=gm, schema=VDFC)
            print("============ Crating Gallery Controller ============")
            print("Controller gallery localpath: " +
                  str(self.galleryControl.galleryPath))
            print("Controller images localpath: " +
                  str(self.galleryControl.imagesPath))
            print("Controller Web gallery URL: " +
                  str(self.galleryControl.webGallery))
            print("\n")

        # exception handling
        except Exception as exp:
            print(exp)
            self.setup()

    def getWebTags(self, column, *args, **kwargs):
        """
        gets the HTML tags from a config file needed by beatifulsoup to
        create the dataframe column with the same name

        Args:
            column (str): name of the column to get the HTML tags

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list with the 4 HTML tags in the following order:
                - divs: main HTML tag to look for in the scrap
                - attrs: optional HTML tags to look for with the main tag
                - elements: main HTML tag to recover in the scrap
                - cleanup: optional HTML tags for clean up scraped data
        """
        try:
            # default ans for the method
            ans = (None, None, None, None)
            cfg = self.scrapyCfg

            # checking config file
            if cfg.has_section(column):

                # prepping all to process config file
                ans = list()
                # get all keys in an option
                keys = cfg.options(column)
                # get datatype from first key
                types = cfg.get(column, keys[0])
                # eval() the type list and removing the first key
                types = eval(types)
                keys.pop(0)

                # iterating the column keys and types
                for k, t in zip(keys, types):
                    # getting column, option value
                    temp = cfg.get(column, k)

                    # ifs for different types
                    if t in (dict, list, tuple, None):
                        temp = eval(temp)
                    elif t is int:
                        temp = int(temp)
                    elif t is float:
                        temp = float(temp)
                    elif t is str:
                        temp = str(temp)
                    ans.append(temp)

                return ans

            else:
                return ans

        # exception handling
        except Exception as exp:
            raise exp

    def getImgTags(self, column, *args, **kwargs):
        """
        gets the image tags from a config file needed to process the files
        to Black & White (B&W) and in color (RGB)

        Args:
            column (str): name of the column to get the image tags

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list of 1 or 2 image tags in the following order:
                - fext: file extension to save the file
                - rgb: size of the shape np.array for color images
                - bw: size of the shape np.array for b&w images
        """
        try:
            # default ans for the method
            ans = (None, None, None)
            cfg = self.scrapyCfg

            # checking config file
            if cfg.has_section(column):

                # prepping all to process config file
                ans = list()
                # get all keys in an option
                keys = cfg.options(column)
                # get datatype from first key
                types = cfg.get(column, keys[0])
                # eval() the type list and removing the first key
                types = eval(types)
                keys.pop(0)

                # iterating the column keys and types
                for k, t in zip(keys, types):
                    # getting column, option value
                    temp = cfg.get(column, k)

                    # ifs for different types
                    if t in (dict, list, tuple, None):
                        temp = eval(temp)
                    elif t is str:
                        temp = str(temp)
                    ans.append(temp)

                return ans

            else:
                return ans

        # exception handling
        except Exception as exp:
            raise exp

    def optOne(self, *args):
        """
        Option 1, it creates a new dataframe with new IDs, Tittles and
        gallery URLs to further scrap data from

        Args:
            id_col (str, optional): df-schema column name of the ID
            title_col (str, optional): df-schema column name of the TITLE
            curl_col (str, optional): df-schema column name of the COLLECTION
            vvg_url (str, optional): web gallery URL search for the collection

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): boolean to confirm success of the task
        """
        try:
            ans = False
            gc = self.galleryControl
            wg = self.webGallery
            gp = self.galleryPath

            # starting the gallery index (gain) from scratch
            id_ins = self.getWebTags(args[0])
            gain = gc.scrapIndex(wg, 5.0, id_ins[0], id_ins[1])
            id_data = gc.getIndexID(gain, id_ins[2], id_ins[3])
            print("Gallery IDs were processed...")

            ti_ins = self.getWebTags(args[1])
            gain = gc.scrapAgain(ti_ins[0], ti_ins[1])
            title_data = gc.getIndexTitle(gain, ti_ins[2])
            print("Gallery Titles were processed...")

            url_ins = self.getWebTags(args[2])
            gain = gc.scrapAgain(url_ins[0], url_ins[1])
            url_data = gc.getIndexURL(gain, args[3], url_ins[2])
            print("Gallery collection URLs were processed...")

            index_data = (id_data, title_data, url_data)
            index_start_cols = copy.deepcopy(args)
            ans = gc.newDataFrame(index_start_cols, index_data)
            print("New Gallery Model was created...")
            gc.createLocalFolders(gp, id_col)
            print("Local Gallery folders were created...")
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def optTwo(self, *args):
        """
        Option 2, saves the in-memory data into CSV and creates the
        local dirpath for the files if it doesnt exists

        Args:
            expf (str, optional): export file name, Default CSV
            dataf (str, optional): data folder name for the app

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): boolean to confirm success of the task
        """
        try:
            ans = False
            gc = self.galleryControl
            ans = gc.saveGallery(args[0], args[1])
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def optThree(self, *args):
        """
        Option 3, loads the in memory of the CSV data and creates the
        local dirpath for the files if it doesnt exists

        Args:
            id_col (str, optional): df-schema column name of the ID
            expf (str, optional): export file name, Default CSV
            dataf (str, optional): data folder name for the app

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): boolean to confirm success of the task
        """
        try:
            gc = self.galleryControl
            gp = self.galleryPath
            gc.loadGallery(args[0], args[1])
            gc.createLocalFolders(gp, args[2])

        # exception handling
        except Exception as exp:
            raise exp

    def optFour(self):
        """
        Option 4, checks the in memory dataframe

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            gc = self.galleryControl
            gc.checkGallery()

        # exception handling
        except Exception as exp:
            raise exp

    def optFive(self, *args):
        """
        Option 5, based on the results of option 1, it scrap the
        description of each URL gallery element

        Args:
            desc_col (str, optional): df-schema column name of the DESCRIPTION
            curl_col (str, optional): df-schema column name of the COLLECTION

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): boolean to confirm success of the task
        """
        try:
            ans = False
            gc = self.galleryControl
            opt_ins = self.getWebTags(args[0])
            descrip_data = gc.scrapDescriptions(
                args[1],
                opt_ins[0],
                opt_ins[1],
                opt_ins[2],
                opt_ins[3],
                multiple=True)

            ans = gc.updateData(args[0], descrip_data)
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def optSix(self, *args):
        """
        Option 6, based on the results of option 1, it scrap the
        image download URL each gallery element

        Args:
            dl_col (str, optional): df-schema column name of the DOWNLOAD_URL
            curl_col (str, optional): df-schema column name of the COLLECTION
            vvg_url (str, optional): web gallery URL search for the collection

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): boolean to confirm success of the task
        """
        try:
            ans = False
            gc = self.galleryControl
            opt_ins = self.getWebTags(args[0])
            urlpic_data = gc.scrapPaintLinks(
                args[1],
                args[2],
                opt_ins[0],
                opt_ins[1],
                opt_ins[2],
                multiple=False)

            ans = gc.updateData(args[0], urlpic_data)
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def optSeven(self, *args):
        """
        Option 7, based on the results of option 1, it download the
        actual image from each gallery element

        Args:
            dl_col (str, optional): df-schema column name of the DOWNLOAD_URL
            haspic_col (str, optional): df-schema column name of the
            HAS_PICTURE

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): boolean to confirm success of the task
        """
        try:
            ans = False
            gc = self.galleryControl
            gp = self.galleryPath
            opt_ins = self.getWebTags(args[1])
            haspic_data = gc.downloadPaints(
                                args[0],
                                gp,
                                opt_ins[0],
                                opt_ins[1],
                                opt_ins[2],
                                opt_ins[3],
                                multiple=False)
            ans = gc.updateData(args[1], haspic_data)
            return ans
        # exception handling
        except Exception as exp:
            raise exp

    def optEight(self, *args):
        """
        Option 8, based on the results of option 1, it scrap the search
        tags in each gallery element in the gallery

        Args:
            search_col (str, optional): df-schema column name of SEARCH TAGS
            curl_col (str, optional): df-schema column name of the COLLECTION
            vvg_url (str, optional): web gallery root URL for the collection

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): boolean to confirm success of the task
        """
        try:
            ans = False
            gc = self.galleryControl
            opt_ins = self.getWebTags(args[0])
            search_data = gc.scrapSearchTags(
                                args[1],
                                args[2],
                                opt_ins[0],
                                opt_ins[1],
                                opt_ins[2],
                                opt_ins[3],
                                multiple=True)

            ans = gc.updateData(args[0], search_data)
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def optNine(self, *args):
        """
        Option 9, based on the results of option 1, it scrap the
        object-data of each gallery element in the gallery

        Args:
            obj_col (str, optional): df-schema column name of OBJ_DATA
            curl_col (str, optional): df-schema column name of the COLLECTION

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): boolean to confirm success of the task
        """
        try:
            ans = False
            gc = self.galleryControl
            opt_ins = self.getWebTags(args[0])
            object_data = gc.scrapObjsData(
                                args[1],
                                opt_ins[0],
                                opt_ins[1],
                                opt_ins[2],
                                multiple=False)

            ans = gc.updateData(args[0], object_data)
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def optTen(self, *args):
        """
        Option 10, based on the results of option 1, it scrap the
        related work of each gallery element in the gallery

        Args:
            rwork_col (str, optional): df-schema column name for RELATED_WORKS
            curl_col (str, optional): df-schema column name of the COLLECTION
            vvg_url (str, optional): web gallery URL search for the collection

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): boolean to confirm success of the task
        """
        try:
            ans = False
            gc = self.galleryControl
            opt_ins = self.getWebTags(args[0])
            rwork_data = gc.scrapPageRelWork(
                                args[1],
                                args[2],
                                opt_ins[0],
                                opt_ins[1],
                                opt_ins[2],
                                opt_ins[3],
                                multiple=True)

            ans = gc.updateData(args[0], rwork_data)
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def optEleven(self, *args):
        """
        Option 11,

            img_col,
            shape_col,
            id_col)

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            ans = False
            gc = self.galleryControl
            wg = self.webGallery
            gp = self.galleryPath
            ip = self.imagesPath

            opt_ins = self.getWebTags(args[0])
            opt_img = self.getImgTags(args[1])
            print(opt_img)
            print(opt_ins)

            # create the local data/img folders
            print(ip)
            print(id_col)
            gc.createLocalFolders(ip, id_col)

            # export the images in RGB and B&W
            # TODO: AQUI VOY!!!!!
            # img_data, shape_data = gc.exportImages()
            # update the CSV columns with the data

            # START OF OLD CODE =============
            # img_data, shape_data = gc.exportImages(
            #     args[2],
            #     opt_ins[0],
            #     args[3], # galleryf,
            #     args[4], # srcf,
            #     args[5]) # paintf)

            # ans = gc.updateData(args[0], img_data)
            # ans = gc.updateData(args[1], shape_data)
            # END OF OLD CODE =============
            return ans

        # exception handling
        except Exception as exp:
            raise exp

    def optTwelve(self, *args):
        """
        Option 12, export all scraped JSON
        columns into JSON file in the designated local folders

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            gc = self.galleryControl
            gp = self.galleryPath

            # JSON export for the following columns:
            # - desccription
            # - search tags
            # - object date
            # - related work
            for temp_cname in args[1]:
                gc.exportToJSON(
                    gp,
                    args[0],
                    temp_cname,
                    temp_cname.lower())

        # exception handling
        except Exception as exp:
            raise exp

    def printReport(self, report):
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
                # self.inputs = input('Select an option to continue\n')
                inp = self.inputs

                # known if the is auto or manual input
                if inp < 0:
                    inp = input('Select an option to continue\n')

                # starting gallery object to scrap data
                if int(inp) == 1:
                    print("Starting a new Gallery (ID, TITLE, COLLECTION_URL)")
                    print("...")
                    ans = self.optOne(id_col,
                                      title_col,
                                      curl_col,
                                      vvg_url)
                    self.printReport(ans)
                    self.optFour()

                elif int(inp) == 2:
                    print("Saving gallery Model into CSV file...")
                    ans = self.optTwo(expf,
                                      dataf)
                    self.printReport(ans)
                    self.optFour()

                elif int(inp) == 3:
                    print("Loading Gallery's CSV file into Model...")
                    ans = self.optThree(expf,
                                        dataf,
                                        id_col)
                    self.printReport(ans)
                    self.optFour()

                elif int(inp) == 4:
                    print("Checking Gallery Model status (dataframe from CSV)")
                    self.printReport(True)
                    self.optFour()

                elif int(inp) == 5:
                    print("Recovering elements description (DESCRIPTION)")
                    ans = self.optFive(desc_col,
                                       curl_col)
                    self.printReport(ans)
                    self.optFour()

                elif int(inp) == 6:
                    print("Recovering pictures download urls (DOWNLOAD_URL)")
                    ans = self.optSix(dl_col,
                                      curl_col,
                                      vvg_url)
                    self.printReport(ans)
                    self.optFour()

                elif int(inp) == 7:
                    print("Downloading Gallery's picture (HAS_PICTURE)")
                    ans = self.optSeven(dl_col, haspic_col)
                    self.printReport(ans)
                    self.optFour()

                elif int(inp) == 8:
                    print("Recovering Gallery's search tags (SEARCH_TAGS)")
                    ans = self.optEight(search_col,
                                        curl_col,
                                        vvg_url)
                    self.printReport(ans)
                    self.optFour()

                elif int(inp) == 9:
                    print("Recovering Gallery's object-data (OBJ_DATA)")
                    ans = self.optNine(obj_col,
                                       curl_col)
                    self.printReport(ans)
                    self.optFour()

                elif int(inp) == 10:
                    print("Recovering Gallery's related work (RELATED_WORKS)")
                    ans = self.optTen(rwork_col,
                                      curl_col,
                                      vvg_url)
                    self.printReport(ans)
                    self.optFour()

                elif int(inp) == 11:
                    # FIXME: need to correct bugs in this part
                    print("Transforming local images into RGB, B&W + shape")
                    ans = self.optEleven(id_col,
                                         img_col,
                                         shape_col)
                    self.printReport(ans)
                    self.optFour()

                elif int(inp) == 12:
                    print("Exporting pandas-df to JSON in local gallery")
                    self.optTwelve(id_col,
                                   json_index_cols)
                    self.printReport(True)
                    self.optFour()

                elif int(inp) == 99:
                    # list with steps for dataframe automatic generation
                    # (3, 4, 5, 6, 7, 2, 8, 2, 9, 2, 10, 2)
                    print("Auto executing options 5 to 10!!!...")
                    ans = self.optFive(desc_col, curl_col)
                    ans = self.optTwo(expf, dataf)
                    ans = self.optSix(dl_col, curl_col, vvg_url)
                    ans = self.optSeven(dl_col, haspic_col)
                    ans = self.optTwo(expf, dataf)
                    ans = self.optEight(search_col, vvg_url)
                    ans = self.optTwo(expf, dataf)
                    ans = self.optNine(obj_col, curl_col)
                    ans = self.optTwo(expf, dataf)
                    ans = self.optTen(rwork_col, curl_col, vvg_url)
                    ans = self.optTwo(expf, dataf)

                    self.printReport(ans)
                    self.optFour()
                    self.inputs = -1

                elif int(inp) == 0:
                    sys.exit(0)

                else:
                    print("Invalid option, please try again...")

        # exception handling
        except Exception as exp:
            print(exp)
            self.run()


if __name__ == "__main__":
    """
    creating the View() object and running it
    """
    scrapy = View()
    scrapy.setup()
    scrapy.run()
