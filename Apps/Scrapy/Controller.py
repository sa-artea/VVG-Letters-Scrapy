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

# ___________________________________________________
# extension python libraries
# ___________________________________________________
import numpy as np
import pandas as pd

# ___________________________________________________
# developed python libraries
# ___________________________________________________
from .Model import Gallery
from .Model import Paint

"""
The controller mediates between the view and the model, there are
some operations implemented in this class, specially the load and save
functions as well as functions to merge the results from different
elements in the models or various models.
"""

# default template for the element/paint dict in gallery
DEFAULT_PANDAS_FRAME = {
    # unique ID for an element in the gallery, its also its folder name in the localdir
    "ID": str(),
    "NAME": str(),              # name of the element inside the gallery
    "PAINT_URL": str(),         # element (paint) URL/link recovered with ScrapyWEB
    "HAS_ID": bool(),           # boolean indicating if the paint has a folder on the localdir
    "HAS_NAME": bool(),         # boolean indicating if the paint has a name in the gallery
}

# default number of paintings in the gallery
DEFAULT_NUM_PAINTS = 50

class Controller (object):
    """[summary]

    Args:
        object ([type]): [description]
    """

    def __init__(self, *args, **kwargs):

        self.galleryHome = ""
        self.gallery = list()
        self.galleryFrame = pd.DataFrame(columns = DEFAULT_PANDAS_FRAME)
        self.maxPaints = DEFAULT_NUM_PAINTS

    def gallerySetUp(self, parameter_list):
        pass

    def loadGallery(self, filepath, **kwargs):
        pass

    def saveGallery(self, filepath, **kwargs):
        pass

    def addPaint(self, parameter_list):
        pass

# ___________________________________________________
#  Funciones para la carga de datos y almacenamiento
#  de datos en los modelos
# ___________________________________________________


# class Controller:
#     def __init__(self, root):
#         self.model = Model()
#         self.model.myMoney.addCallback(self.MoneyChanged)
#         self.view1 = View(root)
#         self.view2 = ChangerWidget(self.view1)
#         self.view2.addButton.config(command=self.AddMoney)
#         self.view2.removeButton.config(command=self.RemoveMoney)
#         self.MoneyChanged(self.model.myMoney.get())

#     def AddMoney(self):
#         self.model.addMoney(10)

#     def RemoveMoney(self):
#         self.model.removeMoney(10)

#     def MoneyChanged(self, money):
#         self.view1.SetMoney(money)


# if __name__ == '__main__':
#     root = tk.Tk()
#     root.withdraw()
#     app = Controller(root)
#     root.mainloop()
