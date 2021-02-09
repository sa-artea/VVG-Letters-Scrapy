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

# ___________________________________________
# importing test framework and necesarry libraries
# ___________________________________________
import config
import pytest

# ___________________________________________
# importing costume scrapping module
# ___________________________________________
from Lib.Recovery.Content import Page as Page

# ___________________________________________
# asserting imports in the module
# ___________________________________________
assert pytest
assert config
assert config

"""
these are test fo r the class page to know if its acceptable
framwork pytest.
"""


@pytest.fixture
def data():
    """
    url->str: fixture test url for the pytest assertions
    altUrl->str: alternative fixture test url for the pytest assertions
    dialect->str: fixture test parse dialect for the pytest assertions
    """
    pytest.url = "https://www.google.com/"
    pytest.altUrl = "https://www.bing.com/"
    pytest.dialect = "html.parser"


@pytest.fixture
def soup():
    """
    division->str: fixture test HTML division for the pytest assertions
    attributes->dict: fixture test dictionary with test HTML decorations for
    pytest assertions
    altDivision->str: alternative test HTML division for pytest assertions
    altAttributes->dict: alternative test HTML divisions for pytest assertions
    """
    pytest.division = "img"
    pytest.attributes = {"alt": "Google", "id": "hplogo"}
    pytest.altDivision = "svg"
    pytest.altAttributes = {"id": "b_logo"}


def test_newPage(data):
    """
    test for the __init__/creator of a new page object.

    Args:
        data: fixture data to test page()
    """
    # creator without parameters
    newPage = Page()
    # asserting equal URL, dialect, request, head soup and body soup
    assert newPage.url == ""
    assert newPage.dialect == pytest.dialect
    assert newPage.request is None
    assert newPage.shead is None
    assert newPage.sbody is None

    url = pytest.url
    dialect = "pytest.dialect"

    # creator with 1 parameter
    newPage = Page(url)

    # asserting equal URL, dialect, request, head soup and body soup
    assert newPage.url == pytest.url
    assert newPage.dialect == pytest.dialect
    assert newPage.request is None
    assert newPage.shead is None
    assert newPage.sbody is None

    # cretor with 2 parameters
    newPage = Page(url, dialect=dialect)

    # asserting equal URL, dialect, request, head soup and body soup
    assert newPage.url == pytest.url
    assert newPage.dialect != pytest.dialect
    assert newPage.request is None
    assert newPage.shead is None
    assert newPage.sbody is None


def test_getPage(data):
    """
    Asserting the creator's URL request with the Page() class and updating its
    value as a parameter

    Args:
        data: fixture data to test Page()
    """

    # invocing creation method
    url = pytest.url
    dialect = pytest.dialect
    testPage = Page(pytest.url, dialect=dialect)

    # asserting equal URL, dialect, request, head soup and body soup
    assert testPage.url == url
    assert testPage.dialect == dialect
    assert testPage.request is None

    # requesting  webpage with existing URL
    status = testPage.getPage()
    assert testPage.url == url
    assert status == 200

    # requesting  webpage updating the URL
    url = pytest.altUrl
    status = testPage.getPage(url)
    assert testPage.url == pytest.altUrl
    assert status == 200


def test_setSoup(data):
    """
    Asserts the soup creation with beautifulsoup library in the Page() class

    Args:
        data: fixture data to test Page()
    """

    # invocing creation method
    url = pytest.url
    dialect = pytest.dialect
    testPage = Page(url, dialect=dialect)

    # requesting page
    status = testPage.getPage()

    # asserting request behavour and inalteration of the body soup/head
    assert testPage.request is not None
    assert testPage.sbody is None
    assert testPage.shead is None

    # setting soup with known parsing dialect
    testPage.setSoup()

    # checking the soup exists al least
    assert testPage.sbody is not None
    assert testPage.shead is not None

    # using other url
    altUrl = pytest.altUrl

    # invocing creation method
    testPage = Page(altUrl)

    # requesting page
    status = testPage.getPage()

    # asserting request behavour and inalteration of the body soup/head
    assert testPage.request is not None
    assert testPage.sbody is None
    assert testPage.shead is None

    # setting soup updating parsing dialect
    testPage.setSoup(dialect=dialect)

    assert testPage.sbody is not None
    assert testPage.shead is not None


def test_findInBody(data, soup):
    """
    Asserts the soup creation with beautifulsoup library in the Page() class

    Args:
        data: fixture data to test Page()
        soup: fixture soup element dictionary to test Page()
    """

    # invocing creation method
    url = pytest.url
    dialect = pytest.dialect
    testPage = Page(url, dialect=dialect)
    # test soup data signation and prep
    div = pytest.division
    attrs = pytest.attributes
    answer = None

    # requesting page
    testPage.getPage()

    # setting soup with known parsing dialect
    testPage.setSoup()

    # finding only one element in ne URL
    answer = testPage.findInBody(div, attributes=attrs, multiple=False)

    # asserting behaviour
    assert answer != -1

    # finding only one element in ne URL
    answer = testPage.findInBody(div, attributes={}, multiple=True)
    # # asserting behaviour
    assert answer != -1
    assert len(answer) > 0
