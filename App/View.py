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
vincent_localpath = dataApp.get("Paths", "localPath")

# real rootpath to work with
galleryFolder = os.path.normpath(vincent_localpath)
print("================== Config INI Local Path Gallery ==================")
print(galleryFolder)
print(os.path.isdir(vincent_localpath))

# subdirs in the local root path needed to process data
paintsFolder = dataApp.get("Paths", "paintsFolder")
lettersFolder = dataApp.get("Paths", "lettersFolder")

# scrapped subfolder
sourceFolder = dataApp.get("Paths", "sourceFolder")

# app subfoder
dataFolder = dataApp.get("Paths", "dataFolder")

# cresting the export file for the data
bfn = dataApp.get("ExportFiles", "basicfile")
fext = dataApp.get("ExportFiles", "fext")

# change according to the request in the .INI!!!!
fsize = dataApp.get("ExportFiles", "small")
# fnsize = dataApp.get("ExportFiles", "large")
# fnsize = dataApp.get("ExportFiles", "extensive")

exportFile = bfn + fsize + "." + fext
print("================== Config INI Export File Name ==================")
print(str(exportFile) + "\n\n")

# loading config schema into the program
dataSchema = Conf.configGlobal(cfgFolder, cfgSchema)

# setting schema for the element/paint gallery dataframe
VINCENT_DF_COLS = eval(dataSchema.get("DEFAULT", "columns"))

# column names for creating a new index and model in the program
WC = VINCENT_DF_COLS[VINCENT_DF_COLS.index(
    "ID"):VINCENT_DF_COLS.index("COLLECTION_URL")+1]
start_index_columns = copy.deepcopy(WC)

print("================== Columns for a new DF-Schema ==================")
print(start_index_columns, "\n")

# column names for creating the JSON in the folders
json_index_cols = copy.deepcopy(VINCENT_DF_COLS[VINCENT_DF_COLS.index(
    "DESCRIPTION"):VINCENT_DF_COLS.index("RELATED_WORKS")+1])

print("================= JSON Columns in the DF-Schema =================")
print(json_index_cols, "\n")

# =======================================================
#  data input to start creating index and scraping
# =======================================================

# html tags for the general object
index_div = "a"
index_attrs = {
    "class": "collection-art-object-wrapper"
}

# working variable for the program
curl_col = VINCENT_DF_COLS[VINCENT_DF_COLS.index("COLLECTION_URL")]

# html tags for the unique ID in the collection
id_div = "a"
id_elem = "href"
id_attrs = {
    "class": "collection-art-object-wrapper",
    "href": re.compile("^/en/collection/"),
}

# working variable for the program
id_col = VINCENT_DF_COLS[VINCENT_DF_COLS.index("ID")]

#  html tags for the title of the element
title_div = "a"
title_elem = "title"
title_attrs = {
    "class": "collection-art-object-wrapper",
    # "title": re.compile("."),
}

#  html tags for the url of the element
url_div = "a"
url_elem = "href"
url_attrs = {
    "class": "collection-art-object-wrapper",
}

# =======================================================
#  data input for scraping the html of each element
# =======================================================

# html tags for scrapping gallery element description
desc_div = "section"
desc_attrs = {
    "class": re.compile("art-object-page-content-"),
}
desc_elem = ["h1", "p", "a"]

# working variable for the program
desc_col = VINCENT_DF_COLS[VINCENT_DF_COLS.index("DESCRIPTION")]

# html tags for scrapping and downloding the image
pic_div = "a"
pic_attrs = {
    "class": "btn-icon art-object-header-bar-button",
    "href": re.compile("^/asset/download/"),
}
pic_elem = "href"

# html tags for search annotations in the gallery elements.
search_div = "section"
search_attrs = {
    "class": "artobject-page-collection-links",
}
search_elem = "a"  # ["li", "a"] # ["ul", "li"]

# html tags for object data in the gallery elements.
obj_div = "dl"
obj_attrs = {
    "class": "definition-list",
    # "string": "Object data",
}
obj_elem = ["dt", "dd"]

# html tags for related work in the gallery elements.
rwork_div = "div"
rwork_attrs = {
    "class": "teaser-row content-row grid-row",
}
rwork_elem = "article"

# img file extension to work in the gallery elements
imgf = "jpg"

# =======================================================
#  Functions to print webpage recovered data
# =======================================================
# dummy vars for the index of the dataframe
donwload_col = VINCENT_DF_COLS[VINCENT_DF_COLS.index("DOWNLOAD_URL")]
haspic_col = VINCENT_DF_COLS[VINCENT_DF_COLS.index("HAS_PICTURE")]
search_col = VINCENT_DF_COLS[VINCENT_DF_COLS.index("SEARCH_TAGS")]
objd_col = VINCENT_DF_COLS[VINCENT_DF_COLS.index("OBJ_DATA")]
rwork_col = VINCENT_DF_COLS[VINCENT_DF_COLS.index("RELATED_WORKS")]
img_col = VINCENT_DF_COLS[VINCENT_DF_COLS.index("IMG_DATA")]
shape_col = VINCENT_DF_COLS[VINCENT_DF_COLS.index("IMG_SHAPE")]

# list with steps for dataframe automatic generator
AUTO_LIST = (3, 4, 5, 6, 2, 7, 2, 8, 2, 9, 2, 10, 2, 11, 12)


class View(object):
    """
    the View is the console interface for the program, connect to the Model()
    with the Controller()
    """
    # =======================================================
    # class variables
    # =======================================================
    galleryControl = Controller()
    galleryModel = Gallery()
    galleryPath = str()
    webGallery = str()

    # query input variables
    qDivs = None
    qAttrs = None
    qElements = None
    qCleanups = None

    # automatic query input variables
    autoStepList = AUTO_LIST
    autoStep = 0
    inputs = -1

    def __init__(self, *args, **kwargs):
        """
        Class View creator

        Args:
            webGallery (str, optional): URL of the museum gallery
            galleryPath (str, optional): the local directory to save the data

        Raises:
            exp: raise a generic exception if something goes wrong

        """
        try:
            # generic creation
            self.galleryModel = Gallery()
            self.galleryControl = Controller()
            self.galleryPath = str()
            self.webGallery = str()
            self.qDivs = None
            self.qAttrs = None
            self.qElements = None
            self.qCleanups = None
            self.autoStepList = AUTO_LIST
            self.autoStep = 0
            self.inputs = -1

            # if args parameters are input in the creator
            if len(args) > 0:

                for i in range(0, len(args)-1):
                    if i == 0:
                        self.webGallery = args[i]

                    if i == 1:
                        self.galleryPath = args[i]

                gw = self.webGallery
                lg = self.galleryPath
                mod = self.galleryModel
                self.galleryModel = Gallery(gw, lg)
                self.galleryControl = Controller(gw, lg, model=mod)

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
            print("======================== WELCOME ========================")
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
            print("11) Transform images into matrix (IMG_DATA, IMG_SHAPE)")
            print("12) Export DataFrame to JSON Files (from CSV to Local dir)")
            print("99) Full auto script for steps [3, 5, 8, 9, 10, 11, 12]")
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
            gf = galleryFolder
            sf = sourceFolder
            pf = paintsFolder

            # setting up local dir for saving data
            self.galleryPath = self.galleryControl.SetUpLocal(gf, sf, pf)
            print("============== Creating the Gallery View ==============")
            print("View localdir: " + str(self.galleryPath))
            print("View gallery URL: " + str(self.webGallery))
            print("\n")

            # creating the gallery model
            gw = self.webGallery
            lg = self.galleryPath
            VDFC = VINCENT_DF_COLS

            self.galleryModel = Gallery(gw, lg, schema=VDFC)
            print("============== Creating Gallery Model ==============")
            print("Model localdir: " + str(self.galleryModel.galleryPath))
            print("Model gallery URL: " + str(self.galleryModel.webGallery))
            print("\n")

            gm = self.galleryModel

            # creating the gallery controller
            self.galleryControl = Controller(gw, lg, gm, schema=VDFC)
            print("============== Crating Gallery Controller ==============")
            print("Controller localdir: " +
                  str(self.galleryControl.galleryPath))
            print("Controller remote gallery URL: " +
                  str(self.galleryControl.webGallery))
            print("\n")

        # exception handling
        except Exception as exp:
            print(exp)
            self.setup()

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
                gc = self.galleryControl
                wg = self.webGallery

                # known if the is auto or manual input
                if inp < 0:
                    inp = input('Select an option to continue\n')

                # starting gallery object to scrap data
                if int(inp) == 1:
                    print("Starting a new Gallery (ID, TITLE, COLLECTION_URL)")
                    print("...\n")

                    # starting the gallery index (gain) from scratch
                    gain = gc.scrapIndex(wg, 5, id_div, id_attrs)
                    id_data = gc.getID(gain, id_elem)
                    print("Gallery IDs were processed...")

                    gain = gc.scrapAgain(title_div, title_attrs)
                    title_data = gc.getTitle(gain, title_elem)
                    print("Gallery Titles were processed...")

                    gain = gc.scrapAgain(id_div, id_attrs)
                    link_data = gc.getURL(gain, vvg_url, id_elem)
                    print("Gallery collection URLs were processed...")

                    index_data = (id_data, title_data, link_data)

                    ans = gc.newDataFrame(start_index_columns, index_data)
                    print("New Gallery Model was created...")

                    gc.createLocalFolders(gc.galleryPath, id_col)
                    print("Local Gallery folders were created...")

                    print("=================== REPORT ===================")
                    ans = gc.checkGallery()
                    print(ans)

                elif int(inp) == 2:
                    print("Saving gallery Model into CSV file...")
                    print("...\n")

                    gc.saveGallery(exportFile, dataFolder)

                    print("=================== REPORT ===================")
                    ans = gc.checkGallery()
                    print(ans)

                elif int(inp) == 3:
                    print("Loading Gallery's CSV file into Model...")
                    print("...\n")

                    gc.loadGallery(exportFile, dataFolder)
                    gc.createLocalFolders(gc.galleryPath, id_col)

                    print("=================== REPORT ===================")
                    ans = gc.checkGallery()
                    print(ans)

                elif int(inp) == 4:
                    print("Checking Gallery Model status (dataframe from CSV)")
                    print("...\n")

                    print("=================== REPORT ===================")
                    ans = gc.checkGallery()
                    print(ans)

                elif int(inp) == 5:
                    print("Recovering elements descripion (DESCRIPTION)")
                    print("...\n")

                    descrip_data = gc.scrapPageDescription(
                                        curl_col,
                                        desc_div,
                                        desc_attrs,
                                        desc_elem,
                                        multiple=True)

                    ans = gc.updateData(desc_col, descrip_data)
                    print("=================== REPORT ===================")
                    print(ans)

                elif int(inp) == 6:
                    print("Recovering pictures download urls (DOWNLOAD_URL)")
                    print("...\n")

                    urlpic_data = gc.scrapPagePicture(
                                        curl_col,
                                        vvg_url,
                                        pic_div,
                                        pic_attrs,
                                        pic_elem,
                                        multiple=False)

                    ans = gc.updateData(donwload_col, urlpic_data)
                    print("=================== REPORT ===================")
                    print(ans)

                elif int(inp) == 7:
                    print("Downloading Gallery's picture (HAS_PICTURE)")
                    print("...\n")

                    urlpic_data = gc.getData(donwload_col)
                    haspic_data = gc.downloadPictures(
                                        urlpic_data,
                                        gc.galleryPath)

                    ans = gc.updateData(haspic_col, haspic_data)
                    print("=================== REPORT ===================")
                    print(ans)

                elif int(inp) == 8:
                    print("Recovering Gallery's search tags (SEARCH_TAGS)")
                    print("...\n")

                    search_data = gc.scrapPageSearchTags(
                                        curl_col,
                                        vvg_url,
                                        search_div,
                                        search_attrs,
                                        search_elem,
                                        multiple=True)

                    ans = gc.updateData(search_col, search_data)
                    print("=================== REPORT ===================")
                    print(ans)

                elif int(inp) == 9:
                    print("Recovering Gallery's object-data (OBJ_DATA)")
                    print("...\n")

                    object_data = gc.scrapPageObjData(
                                        curl_col,
                                        obj_div,
                                        obj_attrs,
                                        obj_elem,
                                        multiple=False)

                    ans = gc.updateData(objd_col, object_data)
                    print("=================== REPORT ===================")
                    print(ans)

                elif int(inp) == 10:
                    print("Recovering Gallery's related work (RELATED_WORKS)")
                    print("...\n")

                    rwork_data = gc.scrapPageRelWork(
                                        curl_col,
                                        vvg_url,
                                        rwork_div,
                                        rwork_attrs,
                                        rwork_elem,
                                        multiple=True)

                    ans = gc.updateData(rwork_col, rwork_data)
                    print("=================== REPORT ===================")
                    print(ans)

                elif int(inp) == 11:
                    print("Transforming local images into np.ndarray + shape")
                    print("...\n")

                    img_data, shape_data = gc.exportImages(
                                    id_col,
                                    imgf,
                                    galleryFolder,
                                    sourceFolder,
                                    paintsFolder)

                    ans = gc.updateData(img_col, img_data)
                    ans = gc.updateData(shape_col, shape_data)
                    print("=================== REPORT ===================")
                    print(ans)

                elif int(inp) == 12:
                    print("Exporting pandas-df to JSON in local gallery")
                    print("...\n")

                    # JSON export for the following columns:
                    # - desccription
                    # - search tags
                    # - object date
                    # - related work
                    for temp_cname in json_index_cols:
                        gc.exportToJSON(
                            gc.galleryPath,
                            id_col,
                            temp_cname,
                            temp_cname.lower())

                    ans = gc.checkGallery()
                    print("=================== REPORT ===================")
                    print(ans)

                elif int(inp) == 99:
                    # FIXME not working, entering in a loop
                    for step in self.auto:
                        print("Auto executing option No. " + str(step) + "!!!")
                        self.inputs = step
                        # self.run()
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
