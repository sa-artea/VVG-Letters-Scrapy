# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Extraer datos de WEB
# 
# Este Script se concentra en extraer la informacion y datos de la galeria del museo Van Gogh y las cartas escritas por el mismo artista para guardar los archivos de texto, png y otros datos necesarios para crear el set de datos de entrenamiento para un modelo de Machine Larning. Se utiliza BeautifulSoup para extraer la informacion desde los portales WEB de interes
# 
# ## Objetivos
# 
# Extraer las imagenes, datos y metadatos de cada elemento dentro de la coleccion del museoVan Gogh.
# 
# ## Fuente de Datos
# 
# Las fuentes de datos para el conjunto de datos son:
# 
# * Galeria de obras y trabajo de Van Gogh: https://vangoghmuseum.nl/en/search/collection?q=&artist=Vincent%20van%20Gogh
# * Archivo de cartas escritas por Van Gogh: http://vangoghletters.org/vg/search/simple?term=
# * Ruta de carpetas de recursos de las cartas escritas por Van Gogh: http://vangoghletters.org/vg/letters/
# 

# %%
# importar librerias necesarias para scrapyWEB
import re
import os
import copy
import json
import urllib
import requests
import validators
import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# importar librerias para hacer un dataframe de referencia
import numpy as np
import pandas as pd
import pandas_profiling as profile

# %% [markdown]
# ## Galeria de Obras de vangoghmuseum.nl
# %% [markdown]
# ### Procesamiento de las pinturas en la galeria
# 
# el proceso sigue los siguientes pasos, para facilidad de la estructura se propone un formato JSON por cada uno de los frames que se desean guardar en formato TXT, al final cada carpeta debe tener 4 archivos TXT mas una imagen en formato PNG. Los pasos a seguir son los siguientes:
# 
# * Chequeo que los enlaces existan y creo las carpetas necesarias.
# * Extraigo las anotaciones de busqueda cada uno de los elementos de la galeria desde el objeto "Search in the collection:".
# * Extraigo los datos archivisticos de cada elemento de la galeria desde el objeto "OBJECT DATA".
# * Extraigo los trabajos relacionados si existen de cada elemento de la galeria desde el objeto "Related work".
# * Extraigo la imagen en formato PNG de cada elemento de la galeria en el desde el objeto "DOWNLOAD IMAGE"
# 
# 
# #### Enlaces utiles para el proceso
# 
# - Extract links from webpage (BeautifulSoup): https://pythonspot.com/extract-links-from-webpage-beautifulsoup/
# - How to: Find all tags with some given name and attributes: https://kite.com/python/examples/1734/beautifulsoup-find-all-tags-with-some-given-name-and-attributes
# - Beautiful Soup can't find the part of the HTML I want: https://stackoverflow.com/questions/51982930/beautiful-soup-cant-find-the-part-of-the-html-i-want
# - Como chequear que un enlace esta vivo: https://stackoverflow.com/questions/51639585/checking-if-a-website-exist-with-python3
# - Como utilizar libreria Request y el metodo GET: https://realpython.com/python-requests/
# - Manejo de errores en Python 3 URL 1: https://www.python-course.eu/python3_exception_handling.php
# - Manejo de errores en Python 3 URL 2: https://www.tutorialspoint.com/python3/python_exceptions.htm
# - Descargar una imagen desde un URL: https://stackabuse.com/download-files-with-python/
# - Reconocer si un string es un URL valido URL 1: https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
# - Reconocer si un string es un URL valido URL 2: https://www.codespeedy.com/check-if-a-string-is-a-valid-url-or-not-in-python/
# - Reconocer si un string tiene un substring importante URL: https://stackoverflow.com/questions/50432978/find-substring-of-keyword-using-beautifulsoup
# - Remplazar signos de puntuacion entre palabras por espacios URL: https://stackoverflow.com/questions/44263446/python-regex-to-add-space-after-dot-or-comma
# - Como guardar un archivo JSON en Python: https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file
# - Recomendaciones de uso del JSON en Python: https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
# - Como actualizar un dataframe con informacion de otro: https://stackoverflow.com/questions/49928463/python-pandas-update-a-dataframe-value-from-another-dataframe
# %% [markdown]
# ### Definicion del DataFrame para la galeria
# defino las columnas necesarias del DataFrame para saber que he podido recuperar y que no, TRUE es que si lo tengo, FALSE de lo contrario

# %%
# lista de columnas para trabajar el DataFrame de la galeria, sirve para manejar la calidad del proceso
# conocer los errores y ver que datos faltan por cada elemento de la galeria
soupCol = [
    "ID", # identificador unico de la galeria, tambien es el nombre del folder dentro del directorio local
    "NAME", # nombre del elemento en la galeria
    "ELEMENT_URL", # enlace del elemento recuperado del ScrapyWEB
    "DOWNLOAD_URL", # enlace de la imagen dentro del elemento de la galeria

    "HAS_ID", # booleano que identifica si se tiene un folder local del elemento
    "HAS_NAME", # booleano que identifica si se tiene el nombre del elemento
    
    "HAS_DESCRIPTION", # booleano que identifica si se tiene la seccion de descripcion en el HTML del elemento
    "HAS_DOWNLOAD", # booleano que identifica si se tiene la seccion de enlace de descarga en el HTML del elemento
    "HAS_TAGS", # booleano que identifica si se tiene la seccion de tags de busqueda en el HTML del elemento
    "HAS_DATA", # booleano que identifica si se tiene la seccion de datos de archivo en el HTML del elemento
    "HAS_RELATEDW", # booleano que identifica si se tiene la seccion de trabajo relacionado en el HTML del elemento
    
    "ERR_ID", # si no se puede crear la carpeta con el ID se guarda el error aca
    "ERR_NAME", # si no se obtiene el nombre se guarda el error aca
    
    "ERR_DESCRIPTION", # si no se obtiene la descripcion se guarda el error aca 
    "ERR_DOWNLOAD", # si no se obtiene el enlace de descarga se guarda el error aca 
    "ERR_TAGS", # si no se obtiene los tags de busqueda se guarda el error aca 
    "ERR_DATA", # si no se obtiene los datos de archivo se guarda el error aca 
    "ERR_RELATEDW", # si no se obtiene el trabajo relacionado se guarda el error aca 
    
    "DESCRIPTION", # aqui guardo el JSON con la informacion de la descripcion
    "TAGS", # aqui guardo el JSON con la informacion de los tags de busqueda
    "DATA", # aqui guardo el JSON con la informacion de los datos de coleccion
    "RELATEDW", # aqui guardo el JSON con la informacion del trabajo relacionado con cada una de las obras
]


# %%
# creo el dataFrame vacio con las columnas necesarias
paintsFrame = pd.DataFrame(columns = soupCol)


# %%
# pruebo si todo cargo bien
paintsFrame.head()

# %% [markdown]
# ### Pagina Fuente (Root Page)
# desde la pagina fuente recupero todos los enlaces a las obras de Vangohg y despues con la lista de enlaces recupero la informacion necesaria
# 
# #### Creando el indice de la coleccion
# creo el URL de busqueda en la pagina principal de la coleccion para extraer los URLs de los elementos creados por Van Gogh, para pruebas mantengo un numero limitado de URLs a recuperar.

# %%
# Se recorre la pagina principal y recuperan los enlaces de l 
# numero de paginas/obras/enlaces a iterar

paints = 1200
defaultPaints = 50

# maximo numero de pinturas conocidas
maxPaints = 1443

# busqueda base en la coleccion de Vangogh

paintsSearch = "https://vangoghmuseum.nl/en/search/collection?q=&artist=Vincent%20van%20Gogh&pagesize="
paintsRoot = "https://vangoghmuseum.nl"

# por defecto pruebo 50 elementos de la coleccion
paintsPage = paintsSearch + str(defaultPaints)

# si el numero de enlaces a buscar esta en el rango a , **ropiado
if paints <= maxPaints and paints > 0:
    paintsPage = paintsSearch + str(paints)

# si el numero de enlaces es superior al maximo
elif paints > maxPaints:
    paintsPage = paintsSearch + str(maxPaints)

# si hay algo raro
else:
    paintsPage = paintsSearch + str(defaultPaints)

# reviso que cargue bien la pagina base
print("--- Search URL ---")
print(paintsPage)


# %%
# lista de enlaces, IDs nombres a elementos de la coleccion
links = list()
ids = list()
names = list()

# objetos necesarios para scrapy en beatifulsoup: handler y resultados
soup = None
linkSoup = list()
nameSoup = list()
errIDs = list()

# diccionario caracterisico para la busqueda para el enlace del elemento de la galeria
linkAttr = {"class":"link-teaser triggers-slideshow-effect", "href":re.compile("^/en/collection/")}

# diccionario caracterisico para la busqueda del nombre del elemento de la galeria
nameAttr = {"class":"text-base text-dark"}

try:
    # GET del URL
    pageReq = requests.get(paintsPage)

    # si el GET me responde bien con codigo 200
    if pageReq.status_code == 200:

        # uso beautifulSoup
        soup = BeautifulSoup(pageReq.content, "html.parser")

        # esta es la seccion del HTML donde estan los enlaces con tag 'a'
        linkSoup = soup.body.findAll("a", attrs = linkAttr)
        
        # esta es la seccion del HTML donde estan los enlaces con tag 'h3'
        nameSoup = soup.body.findAll("h3", attrs = nameAttr)
        
        # si no hay errores agrego un mensaje vacio para no danhar el dataframe
        errIDs.append(None)

# si algo pasa aca esto esta muy mal
except Exception as e:
    print("In URL: " + paintsPage + "\nError: " + str(e))
    print("Status Code: " + str(linkReq.status_code))
    errIDs.append(e)


# %%
# saco los links e IDs a las paginas que quiero dentro de la coleccion
# estan los elementos de tipo link-teaser y la expresion regular del href
names = list()
errNames = list()
hasNames = list()

for name in nameSoup:

    try:

        # reconstruyo el enlace completo
        tempName = re.sub("\s+", " ", name.string)
        tempName = tempName[1:-1]
        names.append(tempName)
        
        # si no hay errores agrego un mensaje vacio para no danhar el dataframe
        errNames.append(None)
        hasNames.append(bool(True))

    except Exception as e:
        print("Error in: " + str(e))
        errNames.append(e)
        hasNames.append(bool(False))


# %%
# saco los links e IDs a las paginas que quiero dentro de la coleccion
# estan los elementos de tipo link-teaser y la expresion regular del href
ids = list()
links = list()

# lista de mensjaes de error y de booleanos de la operacion de sobre IDs
errIDs = list()
hasIDs = list()

for link in linkSoup:

    try:

        # reconstruyo el enlace completo
        tempLink = urllib.parse.urljoin(paintsRoot, link.get("href"))
        tempID = link.get("href").replace("/en/collection/", "")
        
        # nombre e ID para la columna del dataFrame
        ids.append(tempID)
        links.append(tempLink)
        
        # si no hay errores agrego un mensaje vacio para no danhar el dataframe
        errIDs.append(None)
        hasIDs.append(bool(True))

    except Exception as e:
        print("Error in: " + str(e))
        errIDs.append(e)
        hasIDs.append(bool(False))


# %%
# creo un frame para la busqueda que se desea hacer 
searchFrame = pd.DataFrame(columns = soupCol)

# se actualizan los datos de este dataframe con lo que se busco anteriormente
searchFrame["ID"] = ids
searchFrame["ELEMENT_URL"] = links 
searchFrame["NAME"] = names
searchFrame["ERR_ID"] = errIDs
searchFrame["HAS_ID"] = hasIDs
searchFrame["ERR_NAME"] = errNames
searchFrame["HAS_NAME"] = hasNames


# %%
# chequeo que lo que busque esta bien formado
searchFrame.info()
searchFrame.describe()


# %%
# si existe el CSV de busquedas nteriorres se carga lo que existe
galleryFile = "VanGoghGalleryIndex.csv"
dataFolder = "data"

if os.path.exists(dataFolder):
    
    # si el CSV de index ya existe
    galleryBackup = os.path.join(os.getcwd(), dataFolder, galleryFile)
    
    if os.path.exists(galleryBackup):
         
        # lo leo y lo cargo en el DataFrame
        paintsFrame = pd.read_csv(galleryBackup, sep = ",", encoding = "utf-8", engine = "python")#, index_col = [0])


# %%
# agregos los detalles de la nueva busqueda sobre el dataframe de la busqueda anterior
paintsFrame = pd.concat([searchFrame, paintsFrame]).drop_duplicates(["ID", "NAME"], keep = "last").sort_index()


# %%
#chequeo la informacion recuperada de la busqueda
print("Extracted links in search: " + str(len(links)))
print("Repeated link elements: " + str(len(links) != len(set(links))))

print("Extracted IDs in search: " + str(len(ids)))
print("Repeated IDs elements: " + str(len(ids) != len(set(ids))))

print("Extracted names in search: " + str(len(names)))
print("Repeated names elements: " + str(len(names) != len(set(names))))

print("Shape: " + str(paintsFrame.shape))

#chquueo como va todo
paintsFrame.info()
paintsFrame.head()


# %%
# guardando los links en TXT y CSV para backup del proceso y control de calidad
galleryIndex = "VanGoghGalleryIndex.txt"
galleryFile = "VanGoghGalleryIndex.csv"
dataFolder = "data"

# guardando archivo original de texto
# si no existe el directorio
if not os.path.exists(dataFolder):
    
    os.makedirs(dataFolder)

# si existe el directorio
else: 
    
    # sobreescribo el archivo siempre
    # guardo los enlaces en un TXT por si acaso
    with open(os.path.join(os.getcwd(), dataFolder, galleryIndex), "w", encoding = "utf-8", errors = "ignore") as file:
        for link in links:
            file.write("%s\n" % link)
    
    # guardo el DataFrame segun las ultimas actualizaciones
    paintsFrame.to_csv(os.path.join(os.getcwd(), dataFolder, galleryFile), sep = ",", index = False, encoding = "utf-8", mode = "w")

# %% [markdown]
# ### Directorio y Carpetas para persistencia
# configuro donde se va a guardar la informacion inicial dentro de OneDrive (gitHub no me deja), creo las carpetas y desacoplo el computador donde corre el script. Despues ejecuto los siguientes pasos:
# 
# - Creo el folder fuente "01 - Raw".
# - Dentro del folder fuente creo los folderes "01 - Paints" y "02 - Letters".
# - Creo las carpetas necesarias dentro de "01 - Paints" con el ID del dataframe.

# %%
# defino los directorios locales donde se va a persistir la informacion
# no olvidarse del cambiar "\" a "\\" en los filepath de windows por que si no no sirve nada
# dir de santiago
SFAM_ROOT = "C:\\Users\\Felipe\\OneDrive - Universidad de Los Andes\\03 - PhD\\04 - Clases\\05 - IA en Arte y Disenho\\03 - Proyecto\\01 - Data\\01 - Raw"
# dir de daniela
DCP_ROOT = ""
# variable intermedia para independizar, se comenta uno u otro segun donde se corra
WORK_ROOT = SFAM_ROOT
# WORK_ROOT = DCP_ROOT

# nombres de carpetas utiles donde se guarda la informacion
rawFolder = "01 - Raw"
paintsFolder = "01 - Paints"
lettersFolder = "02 - Letters"

#La ruta se obtiene con el dirpath y el filename y el dirpath.split(os.path.sep)[-1] agrega la clase
DATA_ROOT = os.path.dirname(WORK_ROOT)
print(DATA_ROOT)


# %%
# preparar el directorio de trabajo
# si la ruta de trabajo local esta definida
workPath = ""

# si no eexiste el ROOT apropiado, esto lo debe arreglar el usuario
if not os.path.exists(WORK_ROOT):
    
    print("Make sure the WORK_ROOT is correct in your local HD!!!...")

# si si existe el root apropiado, configuro los folderes para guardar la informacion
elif os.path.exists(WORK_ROOT):

    # concateno los folders para la nueva carpeta de trabajo
    workPath = os.path.join(DATA_ROOT, rawFolder, paintsFolder)

    # si todo va bien y necesito crear nuevo folder de trabajo
    if not os.path.exists(workPath):
        
        # creo folderes nuevos
        os.makedirs(workPath)
        print("creating proper folder configuration!!!...")
    
    # si los folderes ya existen
    if os.path.exists(workPath):
        
        print("Working folders and config are cool... carry on!...")

# %% [markdown]
# ### Crear subfolders de las pinturas
# Con la columna de "ELEMENT_URL" e "ID" del data frame se hacen los siguientes pasos:
# 
# - Revisar los enlaces de "ELEMENT_URL" para ver si se puede recuperar la informacion de la galeria.
# - crear folders por cada elemento de la galeria con nombre basado en el "ID".
# - si ya estan las cosas no se repite el trabajo.

# %%
# recorro el arreglo de enlaces habilitados para extraer la informacion
# creo las carpetas necesarias, si ya existen no las sobreescribo.
links = list(paintsFrame["ELEMENT_URL"])
# en este caso los IDs son los nombres de los folders en local
folders = list(paintsFrame["ID"])

# variables de control de calidad del proceso, en este caso en las columnas, "ID", "HAS_ID", "ERR_ID"
errList = list()
hasList = list()

#inicio del ciclo para los enlaces, zip funciona para iterar 2 arreglos al tiempo
for folder in folders:
            
    # chequeo si el enlace sirve para sacar la informacion
    try:
                                
        # creo path para cada elemento en la coleccion
        tempPaintFolder = os.path.join(workPath, folder)

        # creo la carpeta del nuevo elemento de la coleccion si no existe
        if not os.path.exists(tempPaintFolder):

            os.makedirs(tempPaintFolder)
            # si no hay errores agrego un mensaje vacio para no danhar el dataframe
            errList.append(None)
            hasList.append(bool(True))
            
        # si existe la carpeta no hago nada
        elif os.path.exists(tempPaintFolder):
            # print("Folder " + str(folder) + " already exists...")
            # si no hay errores agrego un mensaje vacio para no danhar el dataframe
            errList.append(None)
            hasList.append(bool(True))

    except Exception as e:
        print("In URL: " + link + "\nError: " + str(e))
        print("Status Code: " + str(linkReq.status_code))
        errList.append(e)
        hasList.append(bool(False))


# %%
# actualizo el dataFrame para ver si hay errores
paintsFrame["HAS_ID"] = hasList
paintsFrame["ERR_ID"] = errList


# %%
# chequeo como va el dataframe de procesamiento
paintsFrame.info()
paintsFrame.describe()


# %%
# guardando los links en TXT y CSV para backup del proceso y control de calidad
galleryFile = "VanGoghGalleryIndex.csv"
dataFolder = "data"

# actualizando archivo original CSV
# si no existe el directorio
if not os.path.exists(dataFolder):
    
    os.makedirs(dataFolder)

# si existe el directorio
else: 
    
    # guardo el DataFrame segun las ultimas actualizaciones
    paintsFrame.to_csv(os.path.join(os.getcwd(), dataFolder, galleryFile), sep = ",", index = False, encoding = "utf-8", mode = "w")

# %% [markdown]
# ### Recuperar enlace de imagen de la galeria
# Con la columna de "ELEMENT_URL", "ID" y "DOWNLOAD_URL" del dataFrame se hacen los siguientes pasos:
# 
# - Revisar si existe un enlace valido en "DOWNLOAD_URL", si no existe se sigue adelante.
# - Si no existe el enlace valido, utilizo
# Revisar los enlaces de "ELEMENT_URL" para ver si se puede recuperar la informacion de la galeria.
# - crear folders por cada elemento de la galeria con nombre basado en el "ID".
# - si ya estan las cosas no se repite el trabajo.

# %%
# recorro el arreglo de enlaces habilitados para extraer la informacion
# creo las carpetas necesarias, si ya existen no las sobreescribo.
links = list(paintsFrame["ELEMENT_URL"])
# en este caso los IDs son los nombres de los folders en local
folders = list(paintsFrame["ID"])
# lista de enlaces de descarga de imagenes en la galeria
downloads = list(paintsFrame["DOWNLOAD_URL"])
# lista de errores en el CSV
errors = list(paintsFrame["ERR_DOWNLOAD"])
# lista de existencia en el CSV
proofs = list(paintsFrame["HAS_DOWNLOAD"])

# lista de posibles nuevos enlaces de imagenes en la galeria
newData = list()

# variables de control de calidad del proceso, en este caso en las columnas, "ID", "HAS_ID", "ERR_ID"
errList = list()
hasList = list()

# atributos de la busqueda en beatifulsoup para la imagen tradicional
downAttrs = {"class":"button dark-hover", "href":re.compile("^/download/")}

# atributos de la busqueda en beatifulsoup para el resumen de carta
# "col set-header-image is-page a4portrait"
# "col set-header-image is-page a4landscape"
letterAttrs = {"class":re.compile("a4portrait|a4landscape")}

counter = 0

print("Number of elements in Gallery: " + str(len(links)))
print("Number of local folders for the Gallery: " + str(len(folders)))
print("Number of expected links for download: " + str(len(downloads)))

#inicio del ciclo para los enlaces, zip funciona para iterar 2 arreglos al tiempo
for link, folder, down, err, has in zip(links, folders, downloads, errors, proofs):
    
    # chequeo si el enlace sirve para sacar la informacion
    try:
        
        # inicializo uuna variable temporal
        tempLink = ""
        # print(counter)
        
        # si ya existe el URL de descarga lo repito en la columna
        if validators.url(str(down)) and validators.url(link):
            
            # si no hay errores agrego un mensaje vacio para no danhar el dataframe
            errList.append(err)
            hasList.append(has)
            newData.append(down)
            counter += 1
            
        # chequeo si existe un enlace de descarga de imagen y uno del elemento de la galeria
        elif not validators.url(str(down)) and validators.url(link):
            
            # GET del URL
            linkReq = requests.get(link)
        
            # si el GET me responde bien con codigo 200
            if linkReq.status_code == 200:
         
                # creo path para cada elemento en la coleccion
                tempPaintFolder = os.path.join(workPath, folder)

                # si existe la carpeta, descargo la imagen de la obra dentro de la coleccion de una vez
                if os.path.exists(tempPaintFolder):

                    # parser del cuerpo del elemento de la coleccion
                    linkSoup = BeautifulSoup(linkReq.content, "html.parser")
                    
                    # si es una obra dentro de la galeria
                    if linkSoup.find("a", attrs = downAttrs) != None:
                    
                        # busco todos los elementos de tipo class="button dark-hover"
                        downloadSoup = linkSoup.find("a", attrs = downAttrs)

                        # creo el enlace para descargar la imagen
                        tempLink = urllib.parse.urljoin(paintsRoot, downloadSoup.get("href"))

                        # pido el enlace de la imagen
                        downReq = requests.get(tempLink)

                        # creo el nombre y la direccion del archivo que quiero guardar en la carpeta
                        fileName = urlparse(tempLink)
                        fileName = fileName.path.split("/")[len(fileName.path.split("/"))-1]
                        filePath = os.path.join(tempPaintFolder, fileName)
                        
                        # si el archivo no existe lo guardo
                        if not os.path.exists(filePath):

                            # creo un archivo jpg para guardar la imagen del enlace
                            with open(filePath, "wb") as file:
                                file.write(downReq.content)
                                file.close()
                        
                        # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                        errList.append(None)
                        hasList.append(bool(True))
                        
                        # no importa lo que pase guardo el link de descarga 
                        newData.append(tempLink)
                        counter += 1
                    
                    # si es una carta y no tiene su foto
                    elif linkSoup.find("div", attrs = letterAttrs) != None:
                        
                        # print("Download File Unavailable in: " + str(link))
                        err = "Download file unavailable in URL: " + str(link) + "\n Request time: " + str(datetime.datetime.now())
                        
                        # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                        errList.append(err)
                        hasList.append(bool(False))
                        
                        # guardo el link del elemento padre de la descarga 
                        newData.append(link)                                                 
                        counter += 1
                    
                    # no es nada de lo que espero
                    elif linkSoup.find("a", attrs = downAttrs) == None or linkSoup.find("div", attrs = letterAttrs) == None:
                        
                        # print("this is weird!!!!!")
                        err = "Download file NOT FOUND in URL: " + str(link) + "\n Request time: " + str(datetime.datetime.now())

                        # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                        errList.append(err)
                        hasList.append(bool(False))
                        
                        # guardo el link del elemento padre de la descarga 
                        newData.append(link)                                                 
                        counter += 1                        

    except Exception as e:
        print("In URL: " + link + "\nError: " + str(e))
        print("Status Code: " + str(linkReq.status_code))
        newData.append("In URL: " + link + "\nError: " + str(e))
        errList.append(e)
        hasList.append(bool(False))


# %%
print("Number of Download operations: " + str(counter))
print("Number of downloads: " + str(len(newData)))
print("Number of completed operations: " + str(len(hasList)))
print("Number of error reports: " + str(len(errList)))


# %%
# actualizo el dataFrame para ver si hay errores
paintsFrame["DOWNLOAD_URL"] = newData
paintsFrame["HAS_DOWNLOAD"] = hasList
paintsFrame["ERR_DOWNLOAD"] = errList


# %%
# chequeo como va el dataframe de procesamiento
paintsFrame.info()
paintsFrame.describe()


# %%
# guardando los links en TXT y CSV para backup del proceso y control de calidad
galleryFile = "VanGoghGalleryIndex.csv"
dataFolder = "data"

# actualizando archivo original CSV
# si no existe el directorio
if not os.path.exists(dataFolder):
    
    os.makedirs(dataFolder)

# si existe el directorio
else: 
    
    # guardo el DataFrame segun las ultimas actualizaciones
    paintsFrame.to_csv(os.path.join(os.getcwd(), dataFolder, galleryFile), sep = ",", index = False, encoding = "utf-8", mode = "w")

# %% [markdown]
# ### Recuperar la descripcion del elemento de la galeria
# 
# Con la columna de "ELEMENT_URL", "ID", "HAS_DESCRIPTION" y "ERR_DESCRIPTION" del dataFrame se hacen los siguientes pasos:
# 
# - Revisar el enlace en "ELEMENT_URL" si el enlace esta activo se sigue adelante.
# - se recupera la seccion donde esta la descripcion del elemento.
# - se actualiza el dataframe para mantener la trasabilidad del proceso.
# - si la descripcion ya esta, no se repite el trabajo.
# 
# se supone que los subfolders de los elementos ya existen.

# %%
# recorro el arreglo de enlaces habilitados para extraer la informacion
# creo las carpetas necesarias, si ya existen no las sobreescribo.
links = list(paintsFrame["ELEMENT_URL"])
# en este caso los IDs son los nombres de los folders en local
folders = list(paintsFrame["ID"])
# deberia haber un JSON en esta columna
descriptions = list(paintsFrame["DESCRIPTION"])
# lista de errores en el CSV
errors = list(paintsFrame["ERR_DESCRIPTION"])
# lista de existencia en el CSV
proofs = list(paintsFrame["HAS_DESCRIPTION"])

# variables de control de calidad del proceso, en este caso en las columnas, "HAS_DESCRIPTION", "ERR_DESCRIPTION"
errList = list()
hasList = list()

# lista donde se guarda la nueva informacion que se recupera de la descripcion y contenido de la obra.
newData = list()

# atributos de la busqueda en beatifulsoup para una pintura
soupTag = "article"
soupAttrs = {"class":"col"}

# atributos de la busqueda en beatifulsoup para una carta
letterTag = "div"
letterAttrs = {"class":"col set-header-text"}

# formato del diccionario para el JSON de persistencia de la descripcion del elemento
infoDictSchema = {
    "tittle": str(), # nombre o titulo de la obra.
    "authorship": { # diccionario para la autoria de la obra, nombre del autor, lugar y fecha aproximada.
        "name": str(),
        "place": str(),
        "date": str(),
    }, 
    "description": { # diccionario para la descripcion basica de la obra, medio y dimensiones.
        "medium": str(),
        "dimensions": str(),
    },
    "credits": { # diccionario para describir los creditos asociados con la obra.
        "holder": str(),
        "place": str(),
    }, 
    "content": { # diccionario con la descripcion detallada del contenido de la obra y de ser necesario los links asociados
        "text": str(),
        "references": list()
    } 
}

# contador de la operacion
counter = 0

print("Number of elements in Gallery: " + str(len(links)))
print("Number of local folders for the Gallery: " + str(len(folders)))
print("Number of expected descriptions: " + str(len(descriptions)))

#inicio del ciclo para los enlaces, zip funciona para iterar 2 arreglos al tiempo
for link, folder, des, err, has in zip(links, folders, descriptions, errors, proofs):

    # chequeo si el enlace sirve para sacar la informacion
    try:
        # inicializo uuna variable temporal
        tempInfoDict = copy.deepcopy(infoDictSchema)

        # GET del URL
        linkReq = requests.get(link)

        # si el GET me responde bien con codigo 200
        if linkReq.status_code == 200:
            
            # creo path para cada elemento en la coleccion
            tempPaintFolder = os.path.join(workPath, folder)
            
            # creo el nombre del archivo JSON donde guardo la descripcion
            fileName = "des_" + folder + ".json"
            filePath = os.path.join(tempPaintFolder, fileName)

            # si lo que quiero guardar ya existe
            if os.path.exists(tempPaintFolder) and os.path.exists(filePath):

                # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                hasList.append(has)           
                errList.append(err)
                
                # agrego el JSON en una columna del dataframe
                newData.append(des)
                counter += 1
                # print(counter)
            
            # si existe la carpeta y no existe el JSON, proceso la informacion de la descripcion
            elif os.path.exists(tempPaintFolder) and not os.path.exists(filePath):
                
                # parse del cuerpo del elemento de la coleccion
                linkSoup = BeautifulSoup(linkReq.content, "html.parser")
                
####################################################################################################################
####################################################################################################################
################################ PROCESANDO UNA OBRA DENTRO DE LA GALERIA ##########################################
####################################################################################################################
####################################################################################################################
                
                # si lo que estoy describiendo es una obra
                if linkSoup.find(soupTag, attrs = soupAttrs) != None:

                    # busco todos los elementos de tipo class="article"
                    downloadSoup = linkSoup.find(soupTag, attrs = soupAttrs)

                    # recuperando la informacion del titulo
                    tempInfoDict["tittle"] = downloadSoup.find("a", attrs = {"class":"text-underline-none", "name":"info"}).text
                    # print("---------------- Tittle -----------------\n" + tempInfoDict["tittle"])

                    # recuperando la informacion de la autoria de la obra, nombre del autor, lugar y fecha aproximada.
                    tempData = downloadSoup.find("p", attrs = {"class":"text-bold"}).text

                    # limpiando el texto de caracteres innecesarios
                    tempData = re.sub(" \s+", "", tempData)
                    tempData = re.sub("\n", "", tempData)
                    # print("---------------- Recovered Authorship Data-----------------\n" + str(tempData))
                    tempData = tempData.split(",")

                    if len(tempData) == 2:

                        # nombre del autor, lugar de autoria y fecha aproximada
                        tempInfoDict["authorship"]["name"] = tempData[0]
                        tempInfoDict["authorship"]["date"] = tempData[1]
                        # print("---------------- Authorship -----------------\n" + str(tempInfoDict["authorship"]))

                    elif len(tempData) == 3:

                        # nombre del autor, lugar de autoria y fecha aproximada
                        tempInfoDict["authorship"]["name"] = tempData[0]
                        tempInfoDict["authorship"]["place"] = tempData[1]
                        tempInfoDict["authorship"]["date"] = tempData[2]
                        # print("---------------- Authorship -----------------\n" + str(tempInfoDict["authorship"]))

                    # palabra clave en el esquema de la obra
                    keyWord = "Credits"

                    # recuperando la descripcion de la en un diccionario que contiene medio y dimensiones.
                    tempData = downloadSoup.find("p", attrs = {"class":"text-bold"}).findNext("p").text
                    # print("---------------- Recovered description Data-----------------\n" + str(tempData))

                    tempData = re.sub(" \s+", "", tempData)
                    tempData = re.sub("\n", "", tempData)
                    tempData = tempData.split(keyWord)
                    # print("---------------- Recovered description Data-----------------\n" + str(tempData))

                    # si encuentro el parrafo con los creditos con la estructura apropiada, dividido por ":"
                    if len(tempData) > 1:

                        # print("---------------- description after if -----------------\n" + str(tempData))
                        # tomo el primer elemento
                        tempData = tempData[0]
                        tempData = tempData.split(",")  
                        # print("---------------- description before compare -----------------\n" + str(tempData))

                        if len(tempData) == 1:

                            # print("---------------- description after split -----------------\n" + str(tempData))
                            # guardo en el diccionario el medio y las dimensiones
                            tempInfoDict["description"]["dimensions"] = tempData[0]
                            # print("---------------- description -----------------\n" + str(tempInfoDict["description"]))

                        elif len(tempData) == 2:

                            # print("---------------- description after split -----------------\n" + str(tempData))
                            # guardo en el diccionario el medio y las dimensiones
                            tempInfoDict["description"]["medium"] = tempData[0]
                            tempInfoDict["description"]["dimensions"] = tempData[1]
                            # print("---------------- description -----------------\n" + str(tempInfoDict["description"]))

                        elif len(tempData) > 2:

                            # print("---------------- description after split -----------------\n" + str(tempData))
                            # guardo en el diccionario el medio y las dimensiones
                            tempInfoDict["description"]["dimensions"] = tempData.pop()
                            tempInfoDict["description"]["medium"] = tempData
                            # print("---------------- description -----------------\n" + str(tempInfoDict["description"]))


                    # recuperando la descripcion de los creditos asociados con la obra.
                    tempData = downloadSoup.find("p", attrs = {"class":"text-bold"}).findNext("p").text
                    # limpio y preparo lo que encontre
                    tempData = re.sub(" \s+", "", tempData)
                    tempData = re.sub("\n", "", tempData)
                    tempData = tempData.split(":")                        

                    # si encuentro el parrafo con los creditos con la estructura apropiada, dividido por ":"
                    if len(tempData) == 2:

                        # tomo el ultimo elemento
                        tempData = tempData[len(tempData)-1]
                        # print("---------------- Recovered credits Data-----------------\n" + str(tempData))
                        tempData = tempData.split(",")      

                        # guardo en el diccionario el poseedor y locacion de los creditos
                        tempInfoDict["credits"]["holder"] = tempData[0]
                        tempInfoDict["credits"]["place"] = tempData[1]
                        # print("---------------- credits -----------------\n" + str(tempInfoDict["credits"]))

                    # si existe contenido dentro de la descripcion del elemento, no necesariamente existe!!!
                    if downloadSoup.find("hr", attrs = {"class":"reset-left"}) != None:               

                        # recuperando el contenido de la obra, OJO aqui puede haber enlaces a otros lados!!!!
                        tempData = downloadSoup.find("hr", attrs = {"class":"reset-left"}).findNext("p")
                        # print("---------------- Recovered content Data-----------------\n" + str(tempData))

                        # limpio el texto y guardo en el diccionario el texto del contenido
                        # si no hay espacios entre signos de puntionacion los pongo
                        tempData = re.sub(r"(?<=[.,;:])(?=[^\s])", r" ", tempData.text)
                        tempInfoDict["content"]["text"] = tempData

                        # lo vuelvo a recuperar porque lo altere anteriormente
                        tempData = downloadSoup.find("hr", attrs = {"class":"reset-left"}).findNext("p")

                        # guardo en el diccionario la lista de enlaces vacia
                        tempInfoDict["content"]["references"] = list()

                        # lista de posibles enlaces externos
                        linkList = list()

                        # creo una lista para guardar los links dentro del contenido si es que existen.
                        if len(tempData.findAll("a")) > 0:

                            # print("there are " + str(counter) + " links inside the description!!!!")
                            # counter += 1

                            for ref in tempData.findAll("a"):

                                newLink = {"text":ref.text, "link":ref.get("href")}
                                linkList.append(copy.deepcopy(newLink))

                        # guardo en el diccionario la lista de enlaces relevantes del texto.
                        tempInfoDict["content"]["references"] = copy.deepcopy(linkList)
                        # print("---------------- content -----------------\n" + str(tempInfoDict["description"]))

                    # esto siempre tiene que pasar!!!!
                    # transformo el dict a JSON.
                    jsonInfo = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)

                    # guardo en un archivo el JSON de la descripcion.
                    with open(filePath, "w+", encoding = "utf-8") as file:
                        file.write(jsonInfo)
                        file.close()

                    # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                    errList.append(None)
                    hasList.append(bool(True))
                    
                    # guardo un JSON creado en el CSV y en la carpeta
                    newData.append(jsonInfo)
                    counter += 1
                    # print(counter)
                    
####################################################################################################################
####################################################################################################################
############################### PROCESANDO UNA CARTA DENTRO DE LA GALERIA ##########################################
####################################################################################################################
####################################################################################################################

                # si lo que estoy describiendo es una carta
                elif  linkSoup.find(letterTag, attrs = letterAttrs) != None:
                                        
                    # recuperando la informacion del titulo
                    letterSoup = linkSoup.find(letterTag, attrs = letterAttrs)
                    
                    # recuperando el titulo de la carta/elemento
                    tempInfoDict["tittle"] = letterSoup.find("h1", attrs = {"class":"hr-accent"}).text
                    
                    # recuperando la informacion de la autoria de la obra, nombre del autor, lugar y fecha aproximada.
                    tempData = letterSoup.find("p", attrs = {"class":"text-bold"}).text

                    # limpiando el texto de caracteres innecesarios
                    tempData = re.sub(" \s+", "", tempData)
                    tempData = re.sub("\n", "", tempData)
                    # print("---------------- Recovered Authorship Data-----------------\n" + str(tempData))
                    tempData = tempData.split(",")
                    
                    if len(tempData) == 2:

                        # nombre del autor, lugar de autoria y fecha aproximada
                        tempInfoDict["authorship"]["name"] = tempData[0]
                        tempInfoDict["authorship"]["date"] = tempData[1]
                        # print("---------------- Authorship -----------------\n" + str(tempInfoDict["authorship"]))

                    elif len(tempData) == 3:

                        # nombre del autor, lugar de autoria y fecha aproximada
                        tempInfoDict["authorship"]["name"] = tempData[0]
                        tempInfoDict["authorship"]["place"] = tempData[1]
                        tempInfoDict["authorship"]["date"] = tempData[2]
                        # print("---------------- Authorship -----------------\n" + str(tempInfoDict["authorship"]))
                    
                    # palabra clave en el esquema de la obra
                    keyWord = "Credits"

                    # recuperando la descripcion de la en un diccionario que contiene medio y dimensiones.
                    tempData = letterSoup.find("p", attrs = {"class":"text-bold"}).findNext("p").text
                    # print("---------------- Recovered description Data-----------------\n" + str(tempData))

                    tempData = re.sub(" \s+", "", tempData)
                    tempData = re.sub("\n", "", tempData)
                    tempData = tempData.split(keyWord)
                    # print("---------------- Recovered description Data-----------------\n" + str(tempData))

                    # si encuentro el parrafo con los creditos con la estructura apropiada, dividido por ":"
                    if len(tempData) > 1:

                        # print("---------------- description after if -----------------\n" + str(tempData))
                        # tomo el primer elemento
                        tempData = tempData[0]
                        tempData = tempData.split(",")  
                        # print("---------------- description before compare -----------------\n" + str(tempData))

                        if len(tempData) == 1:

                            # print("---------------- description after split -----------------\n" + str(tempData))
                            # guardo en el diccionario el medio y las dimensiones
                            tempInfoDict["description"]["dimensions"] = tempData[0]
                            # print("---------------- description -----------------\n" + str(tempInfoDict["description"]))

                        elif len(tempData) == 2:

                            # print("---------------- description after split -----------------\n" + str(tempData))
                            # guardo en el diccionario el medio y las dimensiones
                            tempInfoDict["description"]["medium"] = tempData[0]
                            tempInfoDict["description"]["dimensions"] = tempData[1]
                            # print("---------------- description -----------------\n" + str(tempInfoDict["description"]))

                        elif len(tempData) > 2:

                            # print("---------------- description after split -----------------\n" + str(tempData))
                            # guardo en el diccionario el medio y las dimensiones
                            tempInfoDict["description"]["dimensions"] = tempData.pop()
                            tempInfoDict["description"]["medium"] = tempData
                            # print("---------------- description -----------------\n" + str(tempInfoDict["description"]))

                    # recuperando la descripcion de los creditos asociados con la obra.
                    tempData = letterSoup.find("p", attrs = {"class":"text-bold"}).findNext("p").text
                    # limpio y preparo lo que encontre
                    tempData = re.sub(" \s+", "", tempData)
                    tempData = re.sub("\n", "", tempData)
                    tempData = tempData.split(":")                        

                    # si encuentro el parrafo con los creditos con la estructura apropiada, dividido por ":"
                    if len(tempData) == 2:

                        # tomo el ultimo elemento
                        tempData = tempData[len(tempData)-1]
                        # print("---------------- Recovered credits Data-----------------\n" + str(tempData))
                        tempData = tempData.split(",")      

                        # guardo en el diccionario el poseedor y locacion de los creditos
                        tempInfoDict["credits"]["holder"] = tempData[0]
                        tempInfoDict["credits"]["place"] = tempData[1]
                        # print("---------------- credits -----------------\n" + str(tempInfoDict["credits"]))                    
                    
                    # transformo el dict a JSON.
                    jsonInfo = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)

                    # guardo en un archivo el JSON de la descripcion.
                    with open(filePath, "w+", encoding = "utf-8") as file:
                        file.write(jsonInfo)
                        file.close()

                    # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                    errList.append(None)
                    hasList.append(bool(True))
                    
                    # guardo un JSON creado en el CSV y en la carpeta
                    newData.append(jsonInfo)
                    counter += 1
                    # print(counter)
                    
####################################################################################################################
####################################################################################################################
################################### PROCESANDO UN ELEMENTO NO RECONOCIDO ###########################################
####################################################################################################################
####################################################################################################################                    

                # si lo que estoy describiendo no es ni carta ni obra
                elif linkSoup.find(soupTag, attrs = soupAttrs) == None or linkSoup.find(letterTag, attrs = letterAttrs) == None:
                
                    # print("this is weird!!!!!")
                    err = "Description of element NOT FOUND in URL:" + str(link) + "\n Request time: " + str(datetime.datetime.now())

                    # transformo el dict a JSON.
                    jsonInfo = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)

                    # guardo en un archivo el JSON de la descripcion.
                    with open(filePath, "w+", encoding = "utf-8") as file:
                        file.write(jsonInfo)
                        file.close()

                    # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                    errList.append(None)
                    hasList.append(bool(True))
                    
                    # guardo un JSON vacio en el CSV y en la carpeta
                    newData.append(jsonInfo)
                    counter += 1
                    # print(counter)        

    except Exception as e:
        print("In URL: " + link + "\nError: " + str(e))
        print("Status Code: " + str(linkReq.status_code))
        newData.append(copy.deepcopy(infoDictSchema))
        errList.append(e)
        hasList.append(bool(False))


# %%
print("Number of Description operations: " + str(counter))
print("Number of Descriptions: " + str(len(newData)))
print("Number of completed operations: " + str(len(hasList)))
print("Number of error reports: " + str(len(errList)))


# %%
# actualizo el dataFrame para ver si hay errores
paintsFrame["HAS_DESCRIPTION"] = hasList
paintsFrame["ERR_DESCRIPTION"] = errList

# creo una nueva columna para guardar los los diccionarios/JSON dentro del CVS, tambien los guardo en JSON aparte!!!!
paintsFrame["DESCRIPTION"] = newData


# %%
# guardando los links en TXT y CSV para backup del proceso y control de calidad
galleryFile = "VanGoghGalleryIndex.csv"
dataFolder = "data"

# actualizando archivo original CSV
# si no existe el directorio
if not os.path.exists(dataFolder):
    
    os.makedirs(dataFolder)

# si existe el directorio
else: 
    
    # guardo el DataFrame segun las ultimas actualizaciones
    paintsFrame.to_csv(os.path.join(os.getcwd(), dataFolder, galleryFile), sep = ",", index = False, encoding = "utf-8", mode = "w")


# %%
# chequeo como va el dataframe de procesamiento
paintsFrame.info()
paintsFrame.head()

# %% [markdown]
# ### Recuperar la lista de anotaciones del elemento en la galeria
# 
# Con la columna de "ELEMENT_URL", "ID", "TAGS", "HAS_TAGS" y "ERR_TAGS" del dataFrame se hacen los siguientes pasos:
# 
# - Revisar el enlace en "ELEMENT_URL" si el enlace esta activo se sigue adelante.
# - se recupera la seccion donde esta las anotaciones de busqueda del elemento, esta bajo el texto de "Search in the collection:".
# - se actualiza el dataframe para mantener la trasabilidad del proceso.
# - si las anotaciones ya estan, no se repite el trabajo.
# 
# se supone que los subfolders de los elementos ya existen.

# %%
print("Number of Tags operations: " + str(counter))
print("Number of Search Tags: " + str(len(newData)))
print("Number of completed operations: " + str(len(hasList)))
print("Number of error reports: " + str(len(errList)))


# %%
# recorro el arreglo de enlaces habilitados para extraer la informacion
# creo las carpetas necesarias, si ya existen no las sobreescribo.
links = list(paintsFrame["ELEMENT_URL"])
# en este caso los IDs son los nombres de los folders en local
folders = list(paintsFrame["ID"])
# deberia haber un JSON en esta columna
tags = list(paintsFrame["TAGS"])
# lista de errores en el CSV
errors = list(paintsFrame["ERR_TAGS"])
# lista de existencia en el CSV
proofs = list(paintsFrame["HAS_TAGS"])

# variables de control de calidad del proceso, en este caso en las columnas, "HAS_DESCRIPTION", "ERR_DESCRIPTION"
errList = list()
hasList = list()

# lista donde se guarda la nueva informacion que se recupera de la descripcion y contenido de la obra.
newData = list()

# atributos de la busqueda en beatifulsoup
soupTag = "ul"
soupAttrs = {"class":"list-wrapping"}

# formato del diccionario para el JSON de persistencia para las anotaciones del elemento
dataDictSchema = {
    "tags": { # diccionario con la lista detallada de las anotaciones de la obra
        "references": list(), # la lista tiene el link y texto/tag asociado
    } 
}
# contador de la operacion
counter = 0

print("Number of elements in Gallery: " + str(len(links)))
print("Number of local folders for the Gallery: " + str(len(folders)))
print("Number of expected tags: " + str(len(tags)))

#inicio del ciclo para los enlaces, zip funciona para iterar 2 o mas arreglos al tiempo
for link, folder, tag, err, has in zip(links, folders, tags, errors, proofs):
    
    # chequeo si el enlace sirve para sacar la informacion
    try:
        # inicializo uuna variable temporal
        tempInfoDict = copy.deepcopy(dataDictSchema)

        # GET del URL
        linkReq = requests.get(link)

        # si el GET me responde bien con codigo 200
        if linkReq.status_code == 200:
            
            # creo path para cada elemento en la coleccion
            tempPaintFolder = os.path.join(workPath, folder)
            
            # creo el nombre del archivo JSON donde guardo la descripcion
            fileName = "tags_" + folder + ".json"
            filePath = os.path.join(tempPaintFolder, fileName)

            # si ya existe lo que voy a escribir
            if os.path.exists(tempPaintFolder) and os.path.exists(filePath):
                
                # solo lo tomo del dataframe y lo vuelvo a cargar
                jsonData = tag

                # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                errList.append(err)
                hasList.append(has)           
                counter += 1
                # print(counter)  
            
            # si existe la carpeta y no existe el JSON, proceso la informacion de la descripcion
            elif os.path.exists(tempPaintFolder) and not os.path.exists(filePath):
                
                # parse del cuerpo del elemento de la coleccion
                linkSoup = BeautifulSoup(linkReq.content, "html.parser")
                
                # reviso que exista tags de busqueda en el elemento, hay algunas cartas que no lo tienene
                if linkSoup.find(soupTag, attrs = soupAttrs) != None:
                
                    # busco todos los elementos de tipo class="list-wrapping"
                    tagsSoup = linkSoup.find(soupTag, attrs = soupAttrs)
                
                    # saco la informacion que necesito de los tags de busqueda
                    tempData = tagsSoup.findAll("a", attrs = {"class":"button outline neutral text-titlecase"})

                    # lista de posibles enlaces externos
                    linkList = list()

                    # recopilo la lista dentro del elemento encontrado
                    for ref in tempData:#.findAll("a", attrs = {"class":"button outline neutral text-titlecase"}):

                        newLink = {"text":ref.text, "link":ref.get("href")} 
                        linkList.append(copy.deepcopy(newLink))

                    # guardo en el diccionario la lista de enlaces relevantes de las anotaciones.
                    tempInfoDict["tags"]["references"] = copy.deepcopy(linkList)

                    # transformo el dict a JSON.
                    jsonData = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)

                    # guardo en un archivo el JSON de las anotaciones.
                    with open(filePath, "w+", encoding = "utf-8") as file:
                        file.write(jsonData)
                        file.close()

                    # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                    errList.append(None)
                    hasList.append(bool(True))
                    counter += 1
                    # print(counter)  
                    
                # algunas cartas no tienen tags de busqueda, aqui marco cuales son
                elif linkSoup.find(soupTag, attrs = soupAttrs)== None:
                    
                    # print("this is weird, URL: " + str(link))
                    # transformo el dict a JSON.
                    jsonData = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)

                    # guardo en un archivo el JSON de las anotaciones.
                    with open(filePath, "w+", encoding = "utf-8") as file:
                        file.write(jsonData)
                        file.close()

                    err = "Tags unavailable in URL: " + str(link) + "\n Request time: " + str(datetime.datetime.now())
                    
                    # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                    errList.append(err)
                    hasList.append(bool(True))
                    counter += 1
                    # print(counter)
                     
            # agrego el JSON en una columna del dataframe
            newData.append(jsonData)
                    
    except Exception as e:
        print("In URL: " + link + "\nError: " + str(e))
        print("Status Code: " + str(linkReq.status_code))
        newData.append(copy.deepcopy(dataDictSchema))
        errList.append(e)
        hasList.append(bool(False))


# %%
# actualizo el dataFrame para ver si hay errores
paintsFrame["HAS_TAGS"] = hasList
paintsFrame["ERR_TAGS"] = errList

# creo una nueva columna para guardar las anotaciones en JSON dentro del CVS, tambien guardo JSON aparte!!!!
paintsFrame["TAGS"] = newData


# %%
# chequeo como va el dataframe de procesamiento
paintsFrame.info()
paintsFrame.describe()


# %%
# guardando los links en TXT y CSV para backup del proceso y control de calidad
galleryFile = "VanGoghGalleryIndex.csv"
dataFolder = "data"

# actualizando archivo original CSV
# si no existe el directorio
if not os.path.exists(dataFolder):
    
    os.makedirs(dataFolder)

# si existe el directorio
else: 
    
    # guardo el DataFrame segun las ultimas actualizaciones
    paintsFrame.to_csv(os.path.join(os.getcwd(), dataFolder, galleryFile), sep = ",", index = False, encoding = "utf-8", mode = "w")

# %% [markdown]
# ### Recuperar los datos de coleccion del elemento de la galeria
# 
# Con la columna de "ELEMENT_URL", "ID", "DATA", "HAS_DATA" y "ERR_DATA" del dataFrame se hacen los siguientes pasos:
# 
# - Revisar el enlace en "ELEMENT_URL" si el enlace esta activo se sigue adelante.
# - se recupera la seccion donde esta los datos de archivo del elemento.
# - se actualiza el dataframe para mantener la trasabilidad del proceso.
# - si la descripcion ya esta, no se repite el trabajo.
# 
# se supone que los subfolders de los elementos ya existen.

# %%
# recorro el arreglode enlaces habilitados para extraer la informacion
# creo las carpetas necesarias, si ya existen no las sobreescribo.
links = list(paintsFrame["ELEMENT_URL"])
# en este caso los IDs son los nombres de los folders en local
folders = list(paintsFrame["ID"])
# deberia haber un JSON en esta columna
objects = list(paintsFrame["DATA"])
# lista de errores en el CSV
errors = list(paintsFrame["ERR_DATA"])
# lista de existencia en el CSV
proofs = list(paintsFrame["HAS_DATA"])

# variables de control de calidad del proceso, en este caso en las columnas, "ERR_DATA", "HAS_DATA"
errList = list()
hasList = list()

# lista donde se guarda la nueva informacion que se recupera de la descripcion y contenido de la obra.
newData = list()

# atributos de la busqueda en beatifulsoup
soupTag = "dl"
soupAttrs = {"class":"list-table compact"}

# formato del diccionario para el JSON de persistencia de la descripcion del elemento
dataDictSchema = {
    "F_number": str(), # numero de referencia F de la obra.
    "JH_number": str(), # numero de referencia JH de la obra.
    "Obj_number": str(), # numero de referencia del objeto de la obra.
    "L_number": dict(), # numero de referencia exter de la carta
    "dimensions": { # diccionario con las dimensiones basicas de la obra, canvas y marco.
        "canvas": str(),
    },
    "credits": { # diccionario para los creditos asociados con la obra.
        "holder": str(),
        "place": str(),
    },
}

# contador de la operacion
counter = 0

print("Number of elements in Gallery: " + str(len(links)))
print("Number of local folders for the Gallery: " + str(len(folders)))
print("Number of expected data objects: " + str(len(objects)))

#inicio del ciclo para los enlaces, zip funciona para iterar 2 arreglos al tiempo
for link, folder, obj, err, has in zip(links, folders, objects, errors, proofs):
    
    # chequeo si el enlace sirve para sacar la informacion
    try:
        # inicializo una variable temporal
        tempInfoDict = copy.deepcopy(dataDictSchema)

        # GET del URL
        linkReq = requests.get(link)

        # si el GET me responde bien con codigo 200
        if linkReq.status_code == 200:
            
            # creo path para cada elemento en la coleccion
            tempPaintFolder = os.path.join(workPath, folder)
            
            # creo el nombre del archivo JSON donde guardo la descripcion
            fileName = "data_" + folder + ".json"
            filePath = os.path.join(tempPaintFolder, fileName)

            if os.path.exists(tempPaintFolder) and os.path.exists(filePath):

                jsonInfo = obj

                # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                errList.append(err)
                hasList.append(has)
                counter += 1
                # print(counter) 
            
            # si existe la carpeta y no existe el JSON, proceso la informacion de la descripcion
            elif os.path.exists(tempPaintFolder) and not os.path.exists(filePath):
                
                # parse del cuerpo del elemento de la coleccion
                linkSoup = BeautifulSoup(linkReq.content, "html.parser")
                
                # si no existe el objeto DATa dentro del elemento
                if linkSoup.find(soupTag, attrs = soupAttrs) == None:             
                
                    # transformo el dict a JSON.
                    jsonInfo = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)

                    # guardo en un archivo el JSON de la descripcion.
                    with open(filePath, "w+", encoding = "utf-8") as file:
                        file.write(jsonInfo)
                        file.close()

                    # agrego el error y el contador para el dataframe
                    err = "Data Object unavailable in URL: " + str(link) + "\n Request time: " + str(datetime.datetime.now())
                    errList.append(err)
                    hasList.append(bool(False))         
                    counter += 1
                    # print(err)
                    # print(counter)
                    
                # hay ciertos elementos de la galeria que no tienen DATA
                elif linkSoup.find(soupTag, attrs = soupAttrs) != None:
                
                    # busco todos los elementos de tipo class="button dark-hover"
                    dataSoup = linkSoup.find(soupTag, attrs = soupAttrs)                 

                    # encuentro los titulos de las celdas
                    tempDataCol1 = dataSoup.findAll("dt", attrs = {"class":"text-titlecase"})

                    # encuentro los datos no-vacios de las celdas
                    # tempDataCol2 = dataSoup.findAll("dd", string = re.compile("^(?!\s*$).+"))
                    tempDataCol2 = list(d for d in dataSoup.findAll("dd") if len(d.get_text(strip=True)) > 0)
                    
                    # print("------------------------------------ DATA -----------------------------------")
                    # print(len(tempDataCol1) == len(tempDataCol2))
                    # print(len(tempDataCol1), len(tempDataCol2))
                    
                    if len(tempDataCol1) == len(tempDataCol2):

                        for data1, data2 in zip(tempDataCol1, tempDataCol2):

                            # si encuentro el numero F
                            if data1.text == "F-number":

                                # print("------------- F-number -------------------")
                                # print("----- Number Type ----- Number Value -----")
                                # print(data1, data2)
                                # limpio el dato de ser necesario y lo pongo en el diccionario
                                tempInfoDict["F_number"] = data2.text.strip(" ")

                            # si encuentro el numero JH
                            if data1.text == "JH-number":

                                # print("------------- F-number -------------------")
                                # print("----- Number Type ----- Number Value -----")
                                # print(data1, data2)
                                # limpio el dato de ser necesario y lo pongo en el diccionario
                                tempInfoDict["JH_number"] = data2.text.strip(" ")

                            # si encuentro el numero JH
                            if data1.text == "Object number":

                                # print("------------- F-number -------------------")
                                # print("----- Number Type ----- Number Value -----")
                                # print(data1, data2)
                                # limpio el dato de ser necesario y lo pongo en el diccionario
                                tempInfoDict["Obj_number"] = data2.text.strip(" ")
                                
                            # cuando se tiene una carta con referencia a su texto
                            if "Edition" in data1.text:

                                # print("------------- Edition 2009 -------------------")
                                # print("----- Number Type ----- Number Value -----")
                                # print(data1, data2)
                                tempData = data2.text
                                print(tempData, type(tempData))

                                # limpiando el texto de caracteres innecesarios
                                tempData = re.sub(" \s+", "", tempData)
                                tempData = re.sub("\n", " ", tempData)

                                print(tempData)
                                tempInfoDict["L_number"]["text"] = tempData

                                # lista de posibles enlaces externos
                                linkList = list()

                                tempData = data2.findAll("a")

                                # recopilo la lista dentro del elemento encontrado
                                for ref in tempData:

                                    newLink = {"text":ref.text, "link":ref.get("href")} 
                                    linkList.append(copy.deepcopy(newLink))

                                # guardo en el diccionario la lista de enlaces relevantes de las anotaciones.    
                                tempInfoDict["L_number"]["references"] = copy.deepcopy(linkList)
                                
                            # si encuentro los creditos de la obra
                            if "Credits" in data1.text:

                                tempData = data2.text.split(",")

                                if len(tempData) == 2:

                                    tempInfoDict["credits"]["holder"] = tempData[0]
                                    tempInfoDict["credits"]["place"] = tempData[1]
                            
                            # si encuentro las dimensiones de la obra
                            if data1.text == "Dimensions":

                                tempData = data2.text.split(",")
                                
                                if len(tempData) == 1:

                                    tempInfoDict["dimensions"]["canvas"] = tempData[0]
                                
                                if len(tempData) == 2:

                                    tempInfoDict["dimensions"]["canvas"] = tempData[0]
                                    tempInfoDict["dimensions"]["frame"] = tempData[1]                             
                    
                    # transformo el dict a JSON.
                    jsonInfo = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)

                    # guardo en un archivo el JSON de la descripcion.
                    with open(filePath, "w+", encoding = "utf-8") as file:
                        file.write(jsonInfo)
                        file.close()

                    # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                    errList.append(None)
                    hasList.append(bool(True))         
                    counter += 1
                    # print(counter)
                    
            # agrego el JSON en una columna del dataframe
            newData.append(jsonInfo)
                    
    except Exception as e:
        print("In URL: " + link + "\nError: " + str(e))
        print("Status Code: " + str(linkReq.status_code))
        newData.append(copy.deepcopy(dataDictSchema))
        errList.append(e)
        hasList.append(bool(False))


# %%
print("Number of Data object operations: " + str(counter))
print("Number of Data objects: " + str(len(newData)))
print("Number of completed operations: " + str(len(hasList)))
print("Number of error reports: " + str(len(errList)))


# %%
# actualizo el dataFrame para ver si hay errores
paintsFrame["HAS_DATA"] = hasList
paintsFrame["ERR_DATA"] = errList

# creo una nueva columna para guardar los diccionarios/JSON dentro del CVS, tambien los guardo en JSON aparte!!!!
paintsFrame["DATA"] = newData


# %%
# chequeo como va el dataframe de procesamiento
paintsFrame.info()
paintsFrame.head()


# %%
# guardando los links en TXT y CSV para backup del proceso y control de calidad
galleryFile = "VanGoghGalleryIndex.csv"
dataFolder = "data"

# actualizando archivo original CSV
# si no existe el directorio
if not os.path.exists(dataFolder):
    
    os.makedirs(dataFolder)

# si existe el directorio
else: 
    
    # guardo el DataFrame segun las ultimas actualizaciones
    paintsFrame.to_csv(os.path.join(os.getcwd(), dataFolder, galleryFile), sep = ",", index = False, encoding = "utf-8", mode = "w")

# %% [markdown]
# ### Recuperar el trabajo relacionado con el elemento de la galeria
# 
# Con la columna de "ELEMENT_URL", "ID", "RELATEDW", "HAS_RELATEDW" y "ERR_RELATEDW" del dataFrame se hacen los siguientes pasos:
# 
# - Revisar el enlace en "ELEMENT_URL" si el enlace esta activo se sigue adelante.
# - si existe, se recupera la seccion donde esta el trabajo relacionado del elemento.
# - se actualiza el dataframe para mantener la trasabilidad del proceso.
# - si la descripcion ya esta, no se repite el trabajo.
# 
# se supone que los subfolders de los elementos ya existen.

# %%
# recorro el arreglo de enlaces habilitados para extraer la informacion
# creo las carpetas necesarias, si ya existen no las sobreescribo.
links = list(paintsFrame["ELEMENT_URL"])
# en este caso los IDs son los nombres de los folders en local
folders = list(paintsFrame["ID"])
# deberia haber un JSON en esta columna
relationships = list(paintsFrame["RELATEDW"])
# lista de errores en el CSV
errors = list(paintsFrame["ERR_RELATEDW"])
# lista de existencia en el CSV
proofs = list(paintsFrame["HAS_RELATEDW"])

# variables de control de calidad del proceso, en este caso en las columnas, "HAS_DESCRIPTION", "ERR_DESCRIPTION"
errList = list()
hasList = list()

# lista donde se guarda la nueva informacion que se recupera de la descripcion y contenido de la obra.
newData = list()

# atributos de la busqueda en beatifulsoup
soupTag = "section"
soupAttrs = {"class":"page-unit"}

letterTag = "div"
letterAttrs = {"id":"info", "class":"set-overview-body has-footer"}

# formato del diccionario para el JSON de persistencia de la descripcion del elemento
dataDictSchema = {
    "relations": { # diccionario con la lista detallada de las anotaciones de la obra
        "references": list(), # la lista tiene el link y texto/tag asociado
    }
}

# contador de la operacion
counter = 0

print("Number of elements in Gallery: " + str(len(links)))
print("Number of local folders for the Gallery: " + str(len(folders)))
print("Number of expected related work elements: " + str(len(relationships)))

#inicio del ciclo para los enlaces, zip funciona para iterar 2 arreglos al tiempo
for link, folder, relation, err, has in zip(links, folders, relationships, errors, proofs):
    
    print("-------------------- RELATED WORK No. " + str(counter+1) + " ----------------------\nlink: " + str(link))
    # chequeo si el enlace sirve para sacar la informacion
    try:
        # inicializo uuna variable temporal
        tempInfoDict = copy.deepcopy(dataDictSchema)

        # GET del URL
        linkReq = requests.get(link)

        # si el GET me responde bien con codigo 200
        if linkReq.status_code == 200:
            
            print("200 ok")
            # creo path para cada elemento en la coleccion
            tempPaintFolder = os.path.join(workPath, folder)
            
            # creo el nombre del archivo JSON donde guardo la descripcion
            fileName = "relw_" + folder + ".json"
            filePath = os.path.join(tempPaintFolder, fileName)
            
            # si ya existe el archivo JSON
            if os.path.exists(tempPaintFolder) and os.path.exists(filePath):

                jsonInfo = relation

                # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                errList.append(err)
                hasList.append(has)              
                counter += 1
                print("Element No. " + str(counter) +" already there!!!")
            
            # si existe la carpeta y no existe el JSON, proceso la informacion de la descripcion
            elif os.path.exists(tempPaintFolder) and not os.path.exists(filePath):
                
                print("tempPaintFolder exists and JSON does not exists")
                
                # parse del cuerpo del elemento de la coleccion
                linkSoup = BeautifulSoup(linkReq.content, "html.parser")

                # si existen busco todos los elementos de tipo class="page-unit" en el carrusel de la obra
                if linkSoup.find(soupTag, attrs = soupAttrs) != None:
                    
                    print("Painting != none OK")

                    workSoup = linkSoup.find(soupTag, attrs = soupAttrs)
                    
                    # busco la lista de trabajo relacionado de obras
                    if workSoup.find("div", attrs = {"class":"carrousel-wrapper component"}) != None:
                                
                        # lista de posibles enlaces externos
                        linkList = list()
                        
                        # si no existe trabajo relacionado
                        if len(workSoup.findAll("figure")) == 0:

                            jsonInfo = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)

                            with open(filePath, "w+", encoding = "utf-8") as file:
                                file.write(jsonInfo)
                                file.close()
                                
                            # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                            errList.append(None)
                            hasList.append(bool(True))

                            # agrego el JSON en una columna del dataframe
                            newData.append(jsonInfo)
                            counter += 1
                            print("there is NO related work for this painting, operation No.: " + str(counter))
                            
                        elif len(workSoup.findAll("figure")) > 0:
                        
                            tempData = workSoup.findAll("figure", attrs = {"class":"carrousel-item"})

                            for rdata in tempData:
                                
                                tempLink = rdata.find("a")
                                # reconstruyo el enlace completo
                                tempLink = urllib.parse.urljoin(paintsRoot, tempLink.get("href"))
                                
                                # recupero el nombre del enlace
                                tempName = rdata.find("figcaption").text
                                tempName = re.sub(" \s+", "", tempName)
                                tempName = re.sub("\n", "", tempName)
                                
                                newLink = {"text":tempName, "link":tempLink}
                                linkList.append(copy.deepcopy(newLink))
                                
                            # guardo en el diccionario la lista de enlaces relevantes de la obra.
                            tempInfoDict["relations"]["references"] = copy.deepcopy(linkList)

                            # transformo el dict a JSON.
                            jsonInfo = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)
                
                            # guardo en un archivo el JSON de la descripcion.
                            with open(filePath, "w+", encoding = "utf-8") as file:
                                file.write(jsonInfo)
                                file.close()

                            # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                            errList.append(None)
                            hasList.append(bool(True))

                            # agrego el JSON en una columna del dataframe
                            newData.append(jsonInfo)
                            counter += 1
                            print("New related work element created for this painting, operation No.: " + str(counter))
                        
                # si existen las cartas relacionadas se buscan los elementos dentro de la division
                if linkSoup.find(letterTag, attrs = letterAttrs) != None:

                    print("Letter != none OK")
                    
                    workSoup = linkSoup.find(letterTag, attrs = letterAttrs)
                                        
                    # busco la lista de trabajo relacionado de obras
                    # if workSoup.find("ul", attrs = {"class":["cols mmin-cols-2up mm-cols-3up mxl-cols-4up", "cols mm-cols-2up ml-cols-3up"]}) != None:
                    if workSoup.find("ul", attrs = {"class":["cols mm-cols-2up ml-cols-3up", "cols mmin-cols-2up mm-cols-3up mxl-cols-4up"]}) != None:
                        
                        # cols mm-cols-2up ml-cols-3up, cols mmin-cols-2up mm-cols-3up mxl-cols-4up
                        # lista de posibles enlaces externos
                        print("if ul != None")
                        linkList = list()
                        
                        # si no existe trabajo relacionado
                        if len(workSoup.findAll("a")) == 0:
                            
                            jsonInfo = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)

                            with open(filePath, "w+", encoding = "utf-8") as file:
                                file.write(jsonInfo)
                                file.close()

                            # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                            errList.append(None)
                            hasList.append(bool(True))
                            
                            # agrego el JSON en una columna del dataframe
                            newData.append(jsonInfo)
                            counter += 1
                            print("there is NO related work for this letter, operation No.: " + str(counter))

                        elif len(workSoup.findAll("a")) > 0:
                            
                            tempData = workSoup.findAll("a")

                            for rdata in tempData:

                                # recupero el nombre del enlace
                                tempName = None
                                
                                if rdata.find("img", attrs = {"class":"image-lazy"}) != None:
                                
                                    tempName = rdata.find("img", attrs = {"class":"image-lazy"}).get("alt")
                                    tempName = re.sub(" \s+", "", tempName)
                                    tempName = re.sub("\n", "", tempName)

                                    # reconstruyo el enlace completo
                                    tempLink = urllib.parse.urljoin(paintsRoot, rdata.get("href"))

                                    newLink = {"text":tempName, "link":tempLink}
                                    linkList.append(copy.deepcopy(newLink))

                            # guardo en el diccionario la lista de enlaces relevantes de la obra.
                            tempInfoDict["relations"]["references"] = copy.deepcopy(linkList)

                            # transformo el dict a JSON.
                            jsonInfo = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)                        
                            
                            with open(filePath, "w+", encoding = "utf-8") as file:
                                file.write(jsonInfo)
                                file.close()

                            # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                            errList.append(None)
                            hasList.append(bool(True))
                            
                            # agrego el JSON en una columna del dataframe
                            newData.append(jsonInfo)
                            counter += 1
                            print("New letter related work element created, assigned No. is: " + str(counter))
                
                # si el elemento no tiene la estructura esperada
                if linkSoup.find(soupTag, attrs = soupAttrs) == None and linkSoup.find(letterTag, attrs = letterAttrs) == None:
                # else:
                    
                    # guardo en el diccionario la lista de enlaces relevantes de la obra.
                    print("this link is weird!!!... ")# + str(link))
                    tempInfoDict["relations"]["references"] = list()

                    # transformo el dict a JSON.
                    jsonInfo = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)

                    # guardo en un archivo el JSON de la descripcion.
                    with open(filePath, "w+", encoding = "utf-8") as file:
                        file.write(jsonInfo)
                        file.close()

                    err = "Related work is unavailable in URL: " + str(link) + "\n Request time: " + str(datetime.datetime.now())

                    # # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                    errList.append(err)
                    hasList.append(bool(False))
                    # agrego el JSON en una columna del dataframe
                    newData.append(jsonInfo)
                    counter += 1
                    print("Operation No. " + str(counter) + " couldnt find related work element")
                    
    except Exception as e:
        print("In URL: " + link + "\nError: " + str(e))
        print("Status Code: " + str(linkReq.status_code))
        newData.append(copy.deepcopy(dataDictSchema))
        errList.append(e)
        hasList.append(bool(False))


# %%
print("Number of Data object operations: " + str(counter))
print("Number of Data objects: " + str(len(newData)))
print("Number of completed operations: " + str(len(hasList)))
print("Number of error reports: " + str(len(errList)))


# %%
# actualizo el dataFrame para ver si hay errores
paintsFrame["HAS_RELATEDW"] = hasList
paintsFrame["ERR_RELATEDW"] = errList

# creo una nueva columna para guardar los los diccionarios/JSON dentro del CVS, tambien los guardo en JSON aparte!!!!
paintsFrame["RELATEDW"] = newData


# %%
# guardando los links en TXT y CSV para backup del proceso y control de calidad
galleryFile = "VanGoghGalleryIndex.csv"
dataFolder = "data"

# actualizando archivo original CSV
# si no existe el directorio
if not os.path.exists(dataFolder):
    
    os.makedirs(dataFolder)

# si existe el directorio
else: 
    
    # guardo el DataFrame segun las ultimas actualizaciones
    paintsFrame.to_csv(os.path.join(os.getcwd(), dataFolder, galleryFile), sep = ",", index = False, encoding = "utf-8", mode = "w")


# %%
# chequeo como va el dataframe de procesamiento
paintsFrame.info()
paintsFrame.head()

# %% [markdown]
# ## FIN DE TODO
# termine de sacar toda la informacion relevante de la galeria, cada carpeta deberia tener 4 JSON y una imagen asociada.
# 
# Ahora hago un reporte con pandas profiling para ver como me fue

# %%
profile.ProfileReport(paintsFrame)


# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%



# %%
# atributos de la busqueda en beatifulsoup
letterTag = "section"
letterAttrs = {"class":"page-unit"}

# formato del diccionario para el JSON de persistencia de la descripcion del elemento
dataDictSchema = {
    "relations": { # diccionario con la lista detallada de las anotaciones de la obra
        "references": list(), # la lista tiene el link y texto/tag asociado
    }
}

# inicializo uuna variable temporal
tempInfoDict = copy.deepcopy(dataDictSchema)

# GET del URL
link = "https://vangoghmuseum.nl/en/collection/b0243V1962"

testLinks = (
    "https://vangoghmuseum.nl/en/collection/b0243V1962",
    "https://vangoghmuseum.nl/en/collection/b8364bV2006",
    "https://vangoghmuseum.nl/en/collection/d0411V1962",
    "https://vangoghmuseum.nl/en/collection/b0243V1962"
)

counter = 1

for link in testLinks:
    
    print("======================= Test data No: " + str(counter) + " ======================")
    linkReq = requests.get(link)

    # si el GET me responde bien con codigo 200
    if linkReq.status_code == 200:

        print("200 ok")
        # parse del cuerpo del elemento de la coleccion
        linkSoup = BeautifulSoup(linkReq.content, "html.parser")

        # si existen las cartas relacionadas se buscan los elementos dentro de la division
        if linkSoup.find("div", attrs = {"id":"info", "class":"set-overview-body has-footer"}) != None:

            print("!= none OK")

            workSoup = linkSoup.find("div", attrs = {"id":"info", "class":"set-overview-body has-footer"})
            # print(workSoup)

            # <ul class="cols mm-cols-2up ml-cols-3up">
            # busco la lista de trabajo relacionado de obras
            if workSoup.find("ul", attrs = {"class":"cols mm-cols-2up ml-cols-3up"}) != None:

                # cols mm-cols-2up ml-cols-3up
                # lista de posibles enlaces externos
                print("if ul!!!")
                linkList = list()

                # si no existe trabajo relacionado
                if len(workSoup.findAll("a")) == 0:

                    jsonInfo = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)

                    # si no hay errores agrego un mensaje vacio para no danhar el dataframe
                    errList.append(None)
                    hasList.append(bool(True))

                    # agrego el JSON en una columna del dataframe
                    newData.append(jsonInfo)
                    counter += 1
                    print("there is NO related work for this painting, operation No.: " + str(counter))

                elif len(workSoup.findAll("a")) > 0:

                    tempData = workSoup.findAll("a")
                    linkList = list()

                    for rdata in tempData:

                        # recupero el nombre del enlace
                        tempName = None

                        if rdata.find("img", attrs = {"class":"image-lazy"}) != None:

                            tempName = rdata.find("img", attrs = {"class":"image-lazy"}).get("alt")
                            tempName = re.sub(" \s+", "", tempName)
                            tempName = re.sub("\n", "", tempName)

                            # reconstruyo el enlace completo
                            tempLink = urllib.parse.urljoin(paintsRoot, rdata.get("href"))

                            newLink = {"text":tempName, "link":tempLink}
                            linkList.append(copy.deepcopy(newLink))

                    # guardo en el diccionario la lista de enlaces relevantes de la obra.
                    tempInfoDict["relations"]["references"] = copy.deepcopy(linkList)

                    # transformo el dict a JSON.
                    jsonInfo = json.dumps(copy.deepcopy(tempInfoDict), ensure_ascii = False, indent = 4)

    print(tempInfoDict)
    print(jsonInfo)
    counter += 1


