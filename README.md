# Vincent van Gogh Gallery Scrapper

Tp train a Machine Learning model based in the Vincent van Gogh collection data.
In here the script scrap the museum Webpage, recovers all the possible information
from Vincent, Including the paints description, its search tags, collection's data,
the image file, and related work.

This script creates a local gallery from the Web request within an specific path
and creates a CSV file compiling all the data recovered from the online gallery.

Each option in the menu complete the Gallery information scraping an specific column.

1. Creates the gallery's index, recovering the ID, the title and the target URL to
   scrap the rest of the information.
2. Saves the gallery's information into a CSV file.
3. Loads the gallery's information from the CSV file.
4. Check the current gallery's dataframe description.
5. Scrap the basic description data for each gallery's objects.
6. Recover the download link to the image of each gallery's objects.
7. Sets a boolean flag for each available image is available in the local directory.
8. Scrap the search-tags related to each gallery's objects.
9. Scrap the museum's Object-Data related to each gallery's objects.
10. Scrap the related work of each of the gallery's objects.
11. Export each available image into RGB and B&W images.
12. Export all available data from the dataframe to JSON files in the local directory.
13. Full automatic execution from step 5 to step 12.

Originaly developed for the final project for the tittle of Digital humanities
Msc. degree between 2020 - 2021.

The code was refactored and commented for the official and final presentation
for the 2020/2021 project of the Uniandes Digital Humanities graduate program.

---

## **Development Enviroment**

#TODO

---

## **Project Structure**

**LICENSE:** MIT Project license description.

**README:** Project general description.

**PROJECT STRUCTURE:**

* _**\*\App**_ is the main folder with the MVC (Model-View-Controller)
  architecture of the script, to run it execute the _view.py_ file and follow
  the console instructions.

  * _**Model.py**_ module containing the _Gallery_ class, in here the _pandas_
    dataframe works with the _Page_ implementation to format the scrapped data.
  * _**View.py:**_ Console interface to create, populate and save the gallery's dataframe.
  * _**Controller.py:**_ module connecting the _Model.py_ and the _View.py_, it
    controls the export process to JSON format and all the data cleaning functions.
* _**\*\Data**_ is the folder containing the CSV files containing the gallery's
  scraped data.
  * _**vanGoghGallery_large.csv**_ Gallery's large file with 964 register of Vincent van
    Gogh work.
  * _**vanGoghGallery_small.csv**_ Gallery's small file with 61 register of Vincent van
    Gogh work. Useful for functional tests.

* _**\*\Lib**_ is the main folder containing modules and classes useful for
  scrapping the gallery's online data.
  * _**\*\Recovery**_ Containts the _Content.py_ module with the _Page_ class
    for scrapping the VVG museum HTMLs.
  * _**\*\Utils**_ Containts the _Error.py_ module with the _reraise_ method to
    traceback errors in the code's execution.

* _**\*\Tests**_ is the folder containing basic experiments and proofe of
  concept of the code developed in _**\*\Lib**_.
  * _**test_page.py**_ basic tests for the _Page_ class and its methods.
  * _**test_selenium_bs4.py**_ proofe of concept to use selenium with bs4 in the
    collection index.

---

## Data Structure

The description of the CSV files inside the _**\*\Data**_ folder goes as follows:

* _ID:_ element ID in the gallery and local folder name.
* _TITLE:_ tittle of the element in the gallery.
* _COLLECTION\_URL:_ recovered element (paint) URL.
* _DOWNLOAD\_URL:_ direct image URL/link for the image in the gallery.
* _HAS\_PICTURE:_ boolean if there is a picture file in the local folder.
* _DESCRIPTION:_ JSON with the description of the element.
* _SEARCH\_TAGS:_ JSON with the collection tags of the element.
* _OBJ\_DATA:_ JSON with the museum object data of the element.
* _RELATED\_WORKS:_ JSON with the related work text and URLs of the element.
* _IMG\_DATA:_ numpy RGB matrix created from the original image.
* _IMG\_SHAPE:_ numpy shape information from the original image.

---

## Important Notes

* _**Config.py**_ files are Python scripts to work around the relative import of the
  project local dependencies. It is needed in all script folders such as _lib_,
  and _**\*\Recovery**_.
* _**Selenium**_ needs a special instalation and configuration to execute in the
  local repository. For more information go to the URLs:
  * [Selenium with Python](https://selenium-python.readthedocs.io/index.html)
  * [mozilla/geckodriver](https://github.com/mozilla/geckodriver/releases)

---
