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

#___________________________________________
# importing test framework and necesarry libraries
#___________________________________________
import config
import pytest

#___________________________________________
# importing costume scrapping module
#___________________________________________
from Lib.Recovery.Pages import page as page

#___________________________________________
# asserting imports in the module
#___________________________________________
assert pytest
assert config

"""
these are test fo r the class page to know if its acceptable
framwork pytest.
"""

@pytest.fixture
def data():
    """
    url->str: fixture test url for the pytest assertions
    altUrl->str: fixture test url for the pytest assertions
    dialect->str: fixture test parse dialect for the pytest assertions
    """
    pytest.url = "https://www.google.com/"
    pytest.altUrl = "https://www.microsoft.com/"
    pytest.dialect = "html.parser"


def test_newPage(data):
    """
    test for the __init__/creator of a new page object
    """
    # creator without parameters
    newPage = page()
    
    # asserting equal URL, dialect, request, head soup and body soup
    assert newPage.url == ""
    assert newPage.dialect == pytest.dialect
    assert newPage.request == None
    assert newPage.shead == None
    assert newPage.sbody == None

    url = pytest.url
    dialect = "pytest.dialect"

    # creator with 1 parameter
    newPage = page(url)

    # asserting equal URL, dialect, request, head soup and body soup
    assert newPage.url == pytest.url
    assert newPage.dialect == pytest.dialect
    assert newPage.request == None
    assert newPage.shead == None
    assert newPage.sbody == None

    # cretor with 2 parameters
    newPage = page(url, dialect = dialect)

    # asserting equal URL, dialect, request, head soup and body soup
    assert newPage.url == pytest.url
    assert newPage.dialect != pytest.dialect
    assert newPage.request == None
    assert newPage.shead == None
    assert newPage.sbody == None


def test_getPage(data):
    """
    this test want to assert the URL web request of the page() class with the url set in the creator and updating its value as a parameter in the function

    Args:
        data: fixture data for tests of page()
    """

    # invocing creation method
    url = pytest.url
    dialect = pytest.dialect
    testPage = page(pytest.url, dialect = pytest.dialect)

    # asserting equal URL, dialect, request, head soup and body soup
    assert testPage.url == url
    assert testPage.dialect == dialect
    assert testPage.request == None

    # requesting  webpage with existing URL
    status = testPage.getPage()
    assert status == 200

    # requesting  webpage updating the URL
    url = pytest.altUrl
    status = testPage.getPage(url)
    assert testPage.url == pytest.altUrl
    assert status == 200


def test_setSoup():
    pass

def test_findInBody():
    pass


# @pytest.fixture
# def booktagsfile():
#     booktagsfile = 'GoodReads/book_tags-small.csv'
#     return booktagsfile


# @pytest.fixture
# def catalog():
#     """
#     Llama la funcion de inicializacion del catalogo del modelo.
#     """
#     # catalog es utilizado para interactuar con el modelo
#     catalog = control.initCatalog()
#     assert catalog is not None
#     return catalog


# def test_load_movies(catalog, booksfile, tagsfile, booktagsfile):
#     control.loadData(catalog, booksfile, tagsfile, booktagsfile)
#     assert control is not None
#     assert control.booksSize(catalog) == 149
#     assert control.tagsSize(catalog) == 34252
#     books = control.getBooksYear(catalog, 2008)
#     assert lt.size(books) == 4
