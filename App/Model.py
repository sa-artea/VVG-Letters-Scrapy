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

# ===============================
# native python libraries
# ===============================
import os
import copy
import csv
import re
import unicodedata
import urllib
import time

# ===============================
# extension python libraries
# ===============================
import pandas as pd
import cv2

# ===============================
# developed python libraries
# ===============================
import Conf
from Lib.Utils import Err
from Lib.Recovery.Content import Page
from Lib.Recovery.Cleaner import Topic
assert Topic
assert Page
assert Err
assert Conf

# global config variables
CFG_FOLDER = "Config"
CFG_SCHEMA = "df-schema.ini"

# loading config schema into the program
DATA_SCHEMA = Conf.configGlobal(CFG_FOLDER, CFG_SCHEMA)

# default template for the element/paint dict in gallery
DEFAULT_FRAME_SCHEMA = eval(DATA_SCHEMA.get("DEFAULT", "columns"))


# ================================================
# API for the scrapping the gallery of paintings
# ================================================
class Gallery():
    """
    this class implement the gallery of the model, containing all its
    elements (ie.: painintgs) contains all gallery data in memory and
    helps create the data_frame for it.
    """

    # =========================================
    # class variables
    # =========================================
    webg_path = str()
    localg_path = str()
    imgd_path = str()
    schema = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
    data_frame = pd.DataFrame(columns=DEFAULT_FRAME_SCHEMA)
    wpage = Page()

    # =========================================
    # functions to create a new gallery
    # =========================================
    def __init__(self, *args, **kwargs):
        """
        creator of the class gallery()

        Args:
            webg_path (str): URL for the gallery to scrap data
            localg_path (str): local dirpath for the gallery data
            schema (list): array with the column names for the model
            data_frame (data_frame, optional): panda df with data (ie.: paints)
            in the gallery, you can pass an existing df, Default is empty
            wpage (Page): the current webpage the controller is scrapping

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            Model (Model): return a new Model() object
        """
        try:

            # default creator attributes
            self.webg_path = str()
            self.localg_path = str()
            self.imgd_path = str()
            self.schema = copy.deepcopy(DEFAULT_FRAME_SCHEMA)
            self.data_frame = pd.DataFrame(columns=DEFAULT_FRAME_SCHEMA)
            self.wpage = Page()

            # when arguments are pass as parameters
            if len(args) > 0:
                for arg in args:
                    # URL of the remote gallery to scrap
                    if args.index(arg) == 0:
                        self.webg_path = arg

                    # local dirpath to save the gallery CSV
                    if args.index(arg) == 1:
                        self.localg_path = arg

                    # local dirpath to save the images
                    if args.index(arg) == 2:
                        self.imgd_path = arg

                    # dataframes containing the data of the gallery
                    if args.index(arg) == 3:
                        self.data_frame = arg

            # if there are dict decrators in the creator
            if len(kwargs) > 0:

                for key in list(kwargs.keys()):

                    # updating schema in the model
                    if key == "schema":
                        self.schema = copy.deepcopy(kwargs[key])
                        self.data_frame = pd.DataFrame(columns=self.schema)

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: __init__")




#============================================================================================================
    def load_body(self, url):
        self.wpage = Page(url)
        self.wpage.load_body()

    def scrapRoutes(self):
        pattern = r"^[RM]{2}[0-9]+|^[0-9]{3}"
        return self.wpage.get_elements(tag="a",pattern=pattern)
    
    def scrapMetadata(self,route,tag="div",attrs={"class":"content"}):
        data = self.wpage.scrapMetadata(route,tag=tag,attrs=attrs)
        for key in data:
            data[key] = self.clrtext(data[key])
        return data
    
    def scrapOriginalText(self,route, tag="div",attrs ={"class":"content"}):
        original_txt = self.wpage.scrapAtPosition(tag=tag,attrs=attrs, position=3, route=route)
        original_txt = self.clrtext(original_txt) 
        return original_txt

    def scrapTranslationText(self, route, tag="div",attrs ={"class":"content"}):
        translation_txt = self.wpage.scrapAtPosition(tag=tag,attrs=attrs, position=5, route=route)
        translation_txt = self.clrtext(translation_txt) 
        return translation_txt
    
    def scrapNotesText(self, route, tag="div",attrs ={"class":"content"}):
        notes_txt = self.wpage.scrapAtPosition(tag=tag,attrs=attrs, position=7, route=route)
        notes_txt = self.clrtext(notes_txt) 
        return notes_txt

    def scrapAllData(self,route):
        #TODO cambiar ScrapAtPosition por ScrapElements y hacer consultas sobre los elementos.
        data = self.scrapMetadata(route,tag="div",attrs={"class":"content"})
        time.sleep(2)

        data['ORIGINAL'] = self.scrapOriginalText(tag ="div",attrs={"class":"content"}, route=route)
        time.sleep(2)

        data['TRANSLATION'] =  self.scrapTranslationText(tag ="div",attrs={"class":"content"}, route=route)
        time.sleep(2)

        data['NOTES'] = self.scrapNotesText(tag ="div",attrs={"class":"content"}, route=route)
        time.sleep(2)

        artworks = self.scrapArtworks(route)

        for key in artworks:
            if key != "ARTWORKSLINK":
                for i in range(len(artworks[key])):
                    artworks[key][i] = self.clrtext(artworks[key][i]) 
            data[key] = ", ".join(artworks[key])

        for title, link, imgf in zip(artworks["ARTWORKSTITLE"], artworks["ARTWORKSLINK"], artworks["ARTWORKSID"]):
            if len(link) and len(title) and len(imgf):
                print("Title:",title,"Link:",link,"ID:",imgf)
                self.getArtworksImages(route,link,title, imgf)

        return data

    def scrapArtworks(self,route):
        return self.wpage.scrapArtworks(route)

    def getArtworksImages(self,route,url,name, imgf):
        gfolder="Artworks/"+route
        if not os.path.exists(gfolder):
            os.mkdir(gfolder)
        return self.get_imgf(gfolder,url,name, imgf)

    def save(self,data):
        self.data_frame = self.data_frame.append(data,ignore_index=True)

    def write_pc(self):
        self.data_frame.to_csv("SALACHO3.csv")
    


#============================================================================================================




    # =========================================
    # Index functions
    # =========================================

    def scrapidx(self, gurl, stime, div, attrs):
        """
        Scrap the gallery index and recover all the elements in it

        Args:
            gurl (str): gallery URL to scrap data
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine
            the search and scrap
            stime (float): waiting time between requests

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bs-obj): div and attrs filtered beatifulsoup object
        """
        try:
            # reset working web page
            self.wpage = Page()
            ans = None

            # getting the basic element list from gallery online index
            self.wpage.get_collection(gurl, stime)
            ans = self.wpage.findin(div, attributes=attrs)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: scrapidx")














    def scrapagn(self, div, attrs):
        """
        Using the scrapidx() results, scrap for new information
        to complete the dataframe index

        Args:
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bs-obj): div and attrs filtered beatifulsoup object
        """
        try:
            ans = None
            ans = self.wpage.findin(div, attributes=attrs)
            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: scrapagn")

    def newidx(self, cols, data):
        """
        creates a new dataframe in the model based on the columns
        names and new data.

        Args:
            columns (list): list of column names to create the new dataframe
            data (list:list, pandas/numpy matrix): data for the columns the
            new dataframe

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): true if the function created a new df-frame,
            false otherwise
        """
        try:
            ans = False
            self.data_frame = pd.DataFrame(columns=self.schema)

            for col, td in zip(cols, data):

                self.data_frame[col] = td
                ans = True

            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: newidx")

    def get_idxid(self, gsoup, ide, clean):
        # TODO: remove after implement the Topic() class
        """
        get the unique identifier (ID) of the gallery elements (paints) and
        list them to introduce them itto the dataframe

        Args:
            gsoup (bs-obj): list with gallery elements in Beatiful Soup format
            ide (str): HTML <div> keyword to extract the element (paint) ID

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list with the elements (paints) IDs
        """
        try:

            ans = list()

            for element in gsoup:

                tid = element.get(ide).replace(clean, "")
                ans.append(tid)

            # returning answer
            return ans

            # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: get_idxid")

    def get_idxurl(self, gsoup, rurl, urle):
        # TODO: remove after implement the Topic() class
        """
        get the list of the elements inside the gallery index based on the root
        domain url and html div tags

        Args:
            gsoup (bs-obj): beatifulSoup object containing the gallery's
            element list
            rurl (str): root URL of the domain to complete the element url
            urle (str): HTML <div> keyword to process the Page's scraped
            gallery urls

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list with each of the gallery's unique urls
        """
        try:

            ans = list()

            for title in gsoup:

                turl = urllib.parse.urljoin(rurl, title.get(urle))
                ans.append(turl)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: get_idxurl")

    def get_idxtitle(self, gsoup, etitle):
        # TODO: remove after implement the Topic() class
        """
        get the element titles from the gallery main page

        Args:
            gsoup (bs-obj): beatifulSoup object containing the gallery's
            element list
            etitle HTML <div> keyword to process the scraped data from
            the gallery's soup to get the element titles

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): gallery element (paints) titles in string
        """
        try:

            ans = list()
            for element in gsoup:
                # default unknown element name

                title = "untitled"

                # if we know the name of the element
                if element.get(etitle) is not None:
                    title = element.get(etitle)

                # update the answer
                ans.append(title)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: get_idxtitle")

    # =========================================
    # Scrap columns functions in Index
    # =========================================

    def scrape(self, eurl, div, attrs, **kwargs):
        """
        scrap elements within a link based on the <div>, html marks
        and other attributes or decoratos

        Args:
            eurl (str): gallery's element url
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bs-obj): HTML divs as a beatifulsoup object
        """
        try:

            # reset working web page
            self.wpage = Page()

            # get the body of the element url
            rstatus = self.wpage.get_body(eurl)
            ans = None

            if rstatus == 200:
                # find element inside the html body
                ans = self.wpage.findin(
                    div,
                    attributes=attrs,
                    multiple=kwargs.get("multiple"))
            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: scrape")

    def get_imgfn(self, eurl, div, attrs):
        """
        scrap elements within a link based on the <div>, html marks
        and other attributes or decoratos

        Args:
            eurl (str): gallery's element url
            div (str): HTML <div> keyword to search and scrap
            attrs (dict): decorative attributes in the <div> keyword to refine

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bs-obj): HTML divs as a beatifulsoup object
        """
        try:

            # reset working web page
            self.wpage = Page()

            # get the headers and the content from the url
            rstatus = self.wpage.get_header(eurl)
            rstatus = self.wpage.get_content()

            ans = str()

            if rstatus == 200:
                # find attribute inside the headers
                if attrs.items() <= self.wpage.shead.items():
                    headers = self.wpage.shead
                    ans = headers.get(div)
                    ans = str(ans)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: XXXXX")

    def clean_imgfn(self, text, elem, clean):
        """
        scrap elements within a link based on the <div>, html marks
        and other attributes or decoratos

        Args:
            text (str): text to be clean
            elem (str): keyword to split the str and process
            clean (str): keyword to clean in the text

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (str): clean file name with extension
        """
        try:

            ans = None
            ans = text.split(elem)[1].strip().strip(clean)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: clean_imgfn")

    def get_imgf(self, gfolder, dlurl, pfn, imgf):
        # TODO: remove after implement the Topic() class
        # TODO: aniadir doc imgf
        """
        save the paint file from the asset URL in the local folder path

        Args:
            gfolder (str): root local dirpath where the file is going to be
            save
            dlurl (str): url address with the downlodable image file
            pfn (str): filename to save the image

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (bool): True if the file was downloaded in the local dirpath,
            False if not
        """
        try:
            # default answer
            ans = False

            
            fp = gfolder+"/"+ imgf+".jpg"

            # if the file doesnt exists
            if not os.path.exists(fp):

                # saving file from content requests in bit form
                data = self.wpage.getImage(dlurl)
                with open(fp, "wb") as file:

                    file.write(data)
                    file.close()
                    ans = True
                    return ans

            # if the file already exists
            elif os.path.exists(fp):

                ans = True
                return ans

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: get_imgf")

    def updata(self, column, data):
        """
        updates a single column with new data, the size of the data needs to be
        the same as the existing records

        Args:
            column (str): name of the column in the dataframe to update
            data (list/np.array): dataframe of the data to update

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dataframe.info()): updated pandas dataframe description
        """
        try:
            ans = False
            self.data_frame[column] = data
            if self.data_frame[column] is not None:
                ans = True
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: updata")

    # =========================================
    # consult functions
    # =========================================

    def getdata(self, column):
        """
        gets the data from a given column name, returning a list

        Args:
            column (str): name of the column in the dataframe to update

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): formated copy of the data in the dataframe
        """
        try:

            ans = copy.deepcopy(self.data_frame[column])
            ans = list(ans)
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: getdata")

    def check_gallery(self):
        """
        checks the state of the model's dataframe

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dataframe.info()): pandas dataframe description
        """
        try:
            self.data_frame.info()
            # return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: check_gallery")

    # =========================================
    # update functions
    # =========================================
    def upindex(self, column, data):
        """
        updates a single column according to its index/name in the dataframe

        Args:
            column (str): column name in the dataframe
            data (list): list with the updated data for the pandas dataframe,
            needs to have the same size of the original

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dataframe.info()): pandas dataframe description
        """
        try:

            self.data_frame[column] = data
            ans = self.data_frame.info()
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: upindex")

    # =========================================
    # I/O functions
    # =========================================

    def save_gallery(self, fn, dfolder):
        """
        save the in memory dataframe into a CSV file with UTF-8 encoding

        Args:
            fn (str): file name with .csv extension
            dfolder (file-object): valid dirpath str or array with
            valid folders.

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            # pandas function to save dataframe in CSV file
            ans = False
            gfp = os.path.join(os.getcwd(), dfolder, fn)
            tdata = self.data_frame.to_csv(
                            gfp,
                            sep=",",
                            index=False,
                            encoding="utf-8",
                            mode="w",
                            quoting=csv.QUOTE_ALL
                            )
            if tdata is None:
                ans = True
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: save_gallery")

    def load_gallery(self, fn, dfolder):
        """
        loads the gallery from a CSV file in UTF-8 encoding

        Args:
            fn (str): file name with .csv extension
            dfolder (file-object): valid dirpath str or array with
            valid folders.

        Raises:
            exp: raise a generic exception if something goes wrong
        """
        try:
            # read an existing CSV fileto update the dataframe
            ans = False
            gfp = os.path.join(os.getcwd(), dfolder, fn)
            self.data_frame = pd.read_csv(
                                gfp,
                                sep=",",
                                encoding="utf-8",
                                engine="python",
                                quoting=csv.QUOTE_ALL
                                )
            if self.data_frame is not None:
                ans = True
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: load_gallery")

    def export_imgs(self, sfpn, tfpn, tsufix):
        """
        Export images from source files into target files with CV2

        Args:
            sfpn (list): local filepaths of source images
            tfpn (list): local filepaths of target images
            tsufix (dict): target image file sufix, ie.: "-rgb"

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dict): relative filepaths for the target images
        """
        try:
            # default answer
            ans = dict()
            wans = dict()
            for key in tsufix.keys():
                wans[key] = str()

            # checking if both list have images
            eq1 = (len(sfpn) > 0) and (len(tfpn) > 0)
            # checking if the target files and the keys equal
            eq2 = (len(tfpn) == len(tsufix.keys()))

            # evaluating both conditions
            if eq1 and eq2:

                # iterating in the source files
                for sf in sfpn:

                    # iterating in the target files paths and keys
                    for tf, key in zip(tfpn, tsufix.keys()):
                        # default temporal variables
                        complete = False
                        tdf = None

                        # checking if is RGB
                        # if any("rgb" in s for s in (tf, key)):
                        if "rgb" in tf:
                            # opening the source file
                            tdf = cv2.imread(sf, cv2.IMREAD_UNCHANGED)
                            # exporting/saving to RBG file
                            complete = cv2.imwrite(tf, tdf)

                        # checking if is B&W
                        # elif any("bw" in s for s in (tf, key)):
                        elif "bw" in tf:
                            # opening the source file
                            tdf = cv2.imread(sf, cv2.IMREAD_GRAYSCALE)
                            # convert = cv2.COLOR_BGR2GRAY
                            # tdf = cv2.cvtColor(tdf, convert)
                            # exporting/saving to B&W file
                            complete = cv2.imwrite(tf, tdf)

                        # updating answer dict
                        if complete is True:
                            # recovering the important relative path
                            tf = os.path.normpath(tf)
                            tf = tf.split(os.sep)
                            tf = tf[len(tf)-4:len(tf)]
                            tf = os.path.join(*tf)
                            td = {key: tf}
                            wans.update(td)

            # returning answer
            ans = copy.deepcopy(wans)
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: export_imgs")

    def export_shapes(self, tfpn, tsufix):
        """
        Export images from source files into target files with CV2

        Args:
            tfpn (list): local filepaths of target images
            tsufix (dict): target image file sufix, ie.: "-rgb"

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dict): relative filepaths for the target images
        """
        try:
            # default answer
            ans = dict()
            wans = dict()
            for key in tsufix.keys():
                wans[key] = str()

            # checking if list have images
            if len(tfpn) > 0:

                # checking if the target files and the keys equal
                if len(tfpn) == len(tsufix.keys()):

                    # iterating ordered keys
                    sort_sufix = sorted(tsufix.keys(), reverse=False)
                    for tf, key in zip(tfpn, sort_sufix):
                        tf = str(tf)
                        # default temporal variables
                        tdf = None
                        complete = False
                        tshape = list()

                        # checking if it is RGB
                        # if any("rgb" in s for s in (tf, key)):
                        if "rgb" in tf:
                            # opening file in RBG
                            tdf = cv2.imread(tf, cv2.IMREAD_UNCHANGED)
                            # exporting/saving to RBG shape
                            tshape = list(tdf.shape)
                            complete = True

                        # checking if it is B&W
                        # elif any("bw" in s for s in (tf, key)):
                        if "bw" in tf:
                            # opening file in B&W
                            tdf = cv2.imread(tf, cv2.IMREAD_GRAYSCALE)
                            # exporting/saving to B&W shape
                            tshape = list(tdf.shape)
                            complete = True

                        # updating answer dict
                        if complete is True:
                            td = {key: tshape}
                            wans.update(td)

            # # returning answer
            ans = copy.deepcopy(wans)
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: export_shapes")

    def get_srcimgs(self, sfp, sfext):
        """
        Recover the images inside the localpath using the file extension

        Args:
            sfp (str): local folderpath of the source image to scan
            sfext (str): source image file extension, ie.: "jpg"

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list of the source images local filepaths
        """
        try:
            # default answer
            ans = list()
            files = os.listdir(sfp)

            # cheking if there is files in folder
            if len(files) > 0:
                # finding the proper image extension file
                for f in files:
                    if f.endswith(sfext):
                        fn = os.path.join(sfp, f)
                        ans.append(fn)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: get_srcimgs")

    def set_tgtimgs(self, sfpn, tfp, tfext, tsufix):
        """
        Creates the target images in the localpath using the file
        extensions

        Args:
            sfpn (list): source local filepaths of images
            tfp (str): target local folderpath to set the images
            tfext (dict): target image file extension, ie.: "jpg"
            tsufix (dict): target image file sufix, ie.: "-rgb"

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (list): list of the target images local filepaths
        """
        try:
            # default answer
            ans = list()

            # checking if source folder has viable files
            if len(sfpn) > 0:

                # checking source file list
                for sf in sfpn:
                    # recover the source file
                    sfn = os.path.split(sf)
                    sfn = sfn[len(sfn)-1]
                    # strip from original file ext
                    sfn = sfn.split(".")[0]

                    # creating target files with sufix and extension
                    for te, ts in zip(tfext.keys(), tsufix.keys()):
                        # specific target filename + extension
                        tfn = sfn + tsufix.get(ts) + "." + tfext.get(te)
                        tfn = os.path.join(tfp, tfn)
                        ans.append(tfn)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: set_tgtimgs")

    # =========================================
    # clean scraped information functions
    # =========================================

    def clean_description(self, soup, elem, clean):
        # TODO: remove after implement the Topic() class
        """
        Clean the page's description from the beatifulSoup object

        Args:
            soup (bs-obj): beatifulSoup object with the description data
            elem (str): HTML <div> keyword to scrap the description data
            clean (list): secondary <div> to clean the description data

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dict): Element (paint) clean description
        """
        try:
            # get the title in the painting page
            ans = dict()

            # some pages dont follow the most commond diagram
            if soup is not None:

                if len(soup) > 0:

                    # finding title <h1> in the soup
                    value = soup[0].find(elem[0])
                    # cleaning data
                    key = value.attrs.get(clean[0])[0]
                    key = str(key).replace(clean[1], "", 1)
                    key = self.clrtext(key)

                    value = str(value.string).strip()
                    value = self.clrtext(value)

                    # creating the dict to return to save as JSON
                    td = {key: value}
                    # updating answer dict
                    ans.update(copy.deepcopy(td))

                    # finding all description paragraphs <p> in the soup
                    description = soup[0].findAll(elem[1])
                    for element in description:

                        key = element.attrs.get(clean[0])[0]
                        key = str(key)
                        key = key.replace(clean[1], "", 1)
                        key = self.clrtext(key)

                        value = str(element.string).strip()
                        value = self.clrtext(value)

                        # creating the dict to return to save as JSON
                        td = {key: value}

                        # updating answer dict
                        ans.update(copy.deepcopy(td))

                    # getting description text section
                    key = soup[1]
                    key = key.attrs.get(clean[0])[0]
                    key = str(key)
                    key = key.replace(clean[1], "", 1)
                    key = self.clrtext(key)

                    # getting section description text
                    text = soup[1].find(elem[1])
                    value = str()
                    for txt in text:
                        txt = txt.string
                        txt = str(txt)
                        value = value + txt

                    # cleaning data
                    value = str(value).strip()
                    value = self.clrtext(value)

                    # updating answer dict
                    td = {key: value}
                    ans.update(copy.deepcopy(td))

                    # finding all the related links in the description
                    links = soup[1].findAll(elem[2])
                    for link in links:
                        key = str(link.string)
                        key = self.clrtext(key)

                        # getting the link URL
                        value = link.get(clean[2])
                        # reconstructing all the url from the page
                        value = str(value)
                        td = {key: value}

                        # creating the dict to return to save as JSON
                        td = {key: value}

                        # updating answer dict
                        ans.update(copy.deepcopy(td))

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: clean_description")

    def clean_searchtags(self, rurl, soup, elem, clean):
        # TODO: remove after implement the Topic() class
        """
        Clean the page's search-tags from the beatifulSoup object

        Args:
            rurl (str): root URL of the domain to complete the search-tags
            soup (bs-obj): beatifulSoup object with the search-tags data
            elem (str): HTML <div> keyword to scrap the search-tags data
            clean (str): secondary <div> keyword to clean the data from
            the scrap

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dict): Element (paint) clean search-tags
        """
        try:
            # default answer
            ans = dict()

            # checking if searchtags exists
            if soup is not None:

                # checking is the correct collection search tags
                if len(soup) > 0:

                    # finding searhtags <a> in the sou
                    tags = soup[0].findAll(elem)

                    # processing the search tags
                    if len(tags) > 0 and isinstance(tags, list) is True:

                        for tag in tags:
                            # cleaning data
                            key = str(tag.string)
                            key = self.clrtext(key)
                            url = tag.get(clean)

                            # reconstructing all the url from the page
                            value = str(urllib.parse.urljoin(rurl, url))
                            td = {key: value}

                            # updating answer dict
                            ans.update(copy.deepcopy(td))

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: clean_searchtags")

    def clean_objdata(self, soup, elem):
        # TODO: remove after implement the Topic() class
        """
        Clean the page's object-data from the beatifulSoup object

        Args:
            soup (bs-obj): beatifulSoup object with the object-data data
            elem (str): HTML <div> keyword to scrap the object-data data

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dict): Element (paint) clean object-data
        """
        try:
            # default answer
            ans = dict()

            # checking if object-data exists
            if soup is not None:

                # finding <dt> and <dd> from the soup
                keys = soup.findAll(elem[0])
                values = soup.findAll(elem[1])

                # soup keys and values must have data
                if len(keys) > 0 and len(values) > 0:

                    # looping over the <dt> and <dd> data
                    for key, value in zip(keys, values):

                        # cleaning data for dictionary
                        key = str(key.string)
                        key = self.clrtext(key)

                        value = str(value.string)
                        value = self.clrtext(value)

                        # temp dict for complete answer
                        td = {key: value}
                        # updating answer dict
                        ans.update(copy.deepcopy(td))

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: clean_objdata")

    def clean_relwork(self, rurl, soup, elem, clean):
        # TODO: remove after implement the Topic() class
        """
        process the scraped data from the beatifulSoup object and saves the
        related work information into a JSON files

        Args:
            rurl (str): domain root URL to complete the related-work link
            soup (bs-obj): beatifulSoup object with the related-work data
            elem (str): HTML <div> keyword to scrap the related-work data
            clean (list): secondary <div> to clean the related-work data

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (dict): Element (paint) clean related-work
        """
        try:
            # default answer
            ans = dict()

            # checking if searchtags exists
            if soup is not None:

                # finding searhtags <article> in the sou
                relworks = soup[0].findAll(elem)

                # processing related work
                i = 1
                for rw in relworks:
                    # cleaning data and getting all keys and values
                    key = str(rw.find(clean[0]).string)
                    key = self.clrtext(key)

                    url = rw.find(clean[1])
                    url = url.get(clean[2])
                    value = str(urllib.parse.urljoin(rurl, url))

                    # may names are similar in related work
                    if key in ans.keys():

                        # creating alternate key for the dict
                        key = key + " " + str(i)
                        i += 1

                    # updating answer dict
                    td = {key: value}
                    ans.update(copy.deepcopy(td))

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: clean_relwork")

    def clean_dlurl(self, gsoup, rurl, urle):
        # TODO: remove after implement the Topic() class
        """
        recovers the download URL for a gallery element

        Args:
            gsoup (bs-obj): beatifulSoup object with gallery element list
            rurl (str): domain root URL to complete the gallery index
            urle (str): HTML <div> keyword to scrap the gallery index
            urls to download files

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans (str): unique URL with the downloadable element's file
        """
        try:
            ans = None

            if gsoup is not None:
                url = gsoup.get(urle)
                ans = urllib.parse.urljoin(rurl, url)

            # returning answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: clean_dlurl")

    def clrtext(self, text):
        # TODO: remove after implement the Topic() class
        """
        clean text from HTML, remove all inconvinient characters such as:
        extra spaces, extra end-of-line, and non utf-8 characters

        Args:
            text (str): text to clean

        Raises:
            exp: raise a generic exception if something goes wrong

        Returns:
            ans(str): clean text
        """
        try:
            # asigning text as ans
            ans = str(text)

            # attempt striping
            ans = ans.strip()

            # fix encoding
            ans = unicodedata.normalize('NFD', ans)
            ans = ans.encode('ascii', 'ignore')
            ans = ans.decode("utf-8")
            ans = str(ans)

            # removing extra spaces
            ans = re.sub(r" \s+", " ", ans)
            # removing newlines
            ans = re.sub(r"\n", ". ", ans)
            ans = re.sub(r"\r",". ", ans)

            # remove pesky single quote
            ans = re.sub(r"'", "", ans)
            ans = re.sub(r"’", "", ans)

            # HTML weird leftovers
            ans = re.sub(r"None{1,3}", " ", ans)

            # Remove some punctuations 
            ans = re.sub(r";", "", ans)
            ans = re.sub(r",", "", ans)


            # final cast and rechecking
            ans = str(ans)
            # ans = re.sub(r"\W", " ", ans)
            ans = re.sub(r" \s+", " ", ans)



            # return answer
            return ans

        # exception handling
        except Exception as exp:
            Err.reraise(exp, "Gallery: clrtext")
