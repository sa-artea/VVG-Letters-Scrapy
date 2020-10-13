import time
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin

##### Web scrapper for infinite scrolling page #####
driver = webdriver.Chrome(
    executable_path=r"E:\Chromedriver\chromedriver_win32_chrome83\chromedriver.exe")
driver.get("https://www.reddit.com/search/?q=r%2FCOVID19")
time.sleep(2)  # Allow 2 seconds for the web page to open
# You can set your own pause time. My laptop is a bit slow so I use 1 sec
scroll_pause_time = 1
screen_height = driver.execute_script(
    "return window.screen.height;")   # get the screen height of the web
i = 1

while True:
    # scroll one screen height each time
    driver.execute_script(
        "window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
    i += 1
    time.sleep(scroll_pause_time)
    # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
    scroll_height = driver.execute_script("return document.body.scrollHeight;")
    # Break the loop when the height we need to scroll to is larger than the total scroll height
    if (screen_height) * i > scroll_height:
        break

##### Extract Reddit URLs #####
urls = []
soup = BeautifulSoup(driver.page_source, "html.parser")
for parent in soup.find_all(class_="y8HYJ-y_lTUHkQIc1mdCq _2INHSNB8V5eaWp4P0rY_mE"):
    a_tag = parent.find(
        "a", class_="SQnoC3ObvgnGjWt90zD9Z _2INHSNB8V5eaWp4P0rY_mE")
    base = "https://www.reddit.com/search/?q=covid19"
    link = a_tag.attrs['href']
    url = urljoin(base, link)
    urls.append(url)
