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
*
* code based on code from URL https://dev.to/mr_h/python-selenium-infinite-scrolling-3o12
"""

import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time

# Your options may be different
options = Options()
opt_str1 = 'permissions.default.image'
opt_str2 = 'dom.ipc.plugins.enabled.libflashplayer.so'
options.set_preference(opt_str1, 2)
options.set_preference(opt_str2, False)


def scroll(driver, timeout):

    scroll_pause_time = timeout

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height


def all_links(url, sleeptime):
    # Setup the firefox driver with some options and a path to the geckodriver
    driver = webdriver.Firefox()
    # implicitly_wait tells the driver to wait before throwing an exception
    driver.implicitly_wait(30)
    # driver.get(url) opens the page
    driver.get(url)
    # This starts the scrolling by passing the driver and a timeout
    scroll(driver, sleeptime)

    # HTML from `<html>`
    html_str1 = "return document.documentElement.innerHTML;"
    html_res = driver.execute_script(html_str1)

    # HTML from `<body>`
    html_res = driver.execute_script("return document.body.innerHTML;")

    # Once scroll returns bs4 parsers the page_source
    soup_a = BeautifulSoup(html_res, "html.parser")
    # Them we close the driver as soup_a is storing the page source

    driver.close()

    linkAttr = {
        "class": "collection-art-object-wrapper",
        "href": re.compile("^/en/collection/")
    }
    answer = soup_a.findAll("a", attrs=linkAttr)
    return answer


if __name__ == "__main__":

    real_url = "https://www.vangoghmuseum.nl/en/collection?q=&Type=print&Artist=Vincent+van+Gogh"

    sleep_time = 3
    linkAttr = {
        "class": "collection-art-object-list-item",
        "href": re.compile("^/en/collection/")
    }
    gallery_list = all_links(real_url, sleep_time)

    print(len(gallery_list))
    for element in gallery_list:
        print("==========================================")
        # print(element.__dict__)
        print(element.get("href"))
