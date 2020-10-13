import time
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

browser = webdriver.Firefox()
# browser = webdriver.Firefox(driverPath)

browser.get("https://www.vangoghmuseum.nl/en/collection?q=&Artist=Vincent+van+Gogh&Type=painting%2Cdrawing%2Csketch%2Cprint%2Cletter+sketch%2Cstudy%2Ctrial+proof%2Csketchbook")
time.sleep(1)

while expression:
    pass

elem = browser.find_element_by_tag_name("body")

no_of_pagedowns = 5

while no_of_pagedowns:
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.2)
    no_of_pagedowns-=1

post_elems = browser.find_elements_by_class_name("collection-art-object-wrapper")

for post in post_elems:
    print(post)

