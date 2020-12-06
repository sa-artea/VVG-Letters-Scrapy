import pandas as pd
import os
import json
import sys

from pandas.core.frame import DataFrame

rootPath = "C:\\Users\\Felipe\\Universidad de los andes\\ISIS1225 - Documents\\General\\202020\\Material\\Cursos\\2020-20\\Proyecto\\Datos"
fileList = list()
# lastName = ["", "", ""]
# extension = ".csv"

for file in os.listdir(rootPath):
    if file.endswith(".json"):
        fileList.append(os.path.join(rootPath, file))

for fn in fileList:
    
    print("Reading JSON file...")
    print(fn)

    dataFrame = pd.read_json(fn, orient='records')
    newf = fn.replace("json", "csv")
    dataFrame.to_csv(newf, sep=",", index=False, encoding="utf-8", mode="w")
    print("New CSV file created!!!")
    print(newf)

