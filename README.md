# Vincent Van Gogh Gallery Scrapper

This is a project to train a Machine Learning model based in the Vinvent Van
Gogh collection data. In here the script scrap the Webpage, recovers all the
possible data from Vincent, Including the paint description, its tag,
collection's data, and related work

Originaly developed for the final project for the tittle of Digital humanities
Msc dregree between 2019 - 2021.

This code was refactored and its comentaries extended for the official
presentation for the 2020/2021 Uniandes Digital Humanities graduated program.

---

## **Project Structure**

**LICENSE:** MIT Project license description.

**README:** Project general description.

**PROJECT STRUCTURE:**

* _**\*\App**_ is the main folder with the MVC (Model-View-Controller)
  architecture of the script, to run it execute the _view.py_ file and follow
  the console instructions.

  * _**Model.py**_ aaaaaa.
  * _**View.py:**_ sssssssss.
  * _**Controller.py:**_ ssssssssssssss.
* _**\*\Data**_ is the folder containing the CSV files containing the gallery's
  scraped data.
  * _**VanGoghGallery_large.csv**_ Gallery's large file with 964 register of Vincent Van
    Gogh work.
  * _**VanGoghGallery_small.csv**_ Gallery's small file with 61 register of Vincent Van
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

## Important Notes

* _**Config.py**_ files are Python scripts to work around the relative import of the
  project local dependencies. It is needed in all script folders such as _lib_,
  and _**\*\Recovery**_.
* _**Selenium**_ needs a special instalation and configuration to execute in the
  local repository. For more information go to the URLs:
  * [Selenium with Python](https://selenium-python.readthedocs.io/index.html)
  * [mozilla/geckodriver](https://github.com/mozilla/geckodriver/releases)

---
