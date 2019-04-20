from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.file_detector import FileDetector
from selenium.common.exceptions import TimeoutException

import requests
import time
import zipfile
import os
import shutil

from passwords import googleUsername, googlePassword
from passwords import wordpressUsername, wordpressPassword

if True:
    browser = webdriver.Chrome()

    url = 'https://www.google.com/accounts/Login?hl=en&continue=http://www.google.co.jp/'
    browser.get(url)

    browser.find_element_by_id("identifierId").send_keys(googleUsername)
    browser.find_element_by_id("identifierNext").click()
    time.sleep(1)
    browser.find_element_by_name("password").send_keys(googlePassword)
    browser.find_element_by_id("passwordNext").click()
    time.sleep(5)

    browser.get("https://storyweaver.org.in")
    time.sleep(10)
    EC.presence_of_element_located((By.CLASS_NAME, 'pb-site-nav-link__title'))
    browser.find_element_by_class_name("pb-site-nav-link__title").click()
    time.sleep(1)
    browser.find_element_by_css_selector("button.pb-button.pb-button--full-width.pb-button--google").click()
    time.sleep(5)

def getInfo(book):
        data = {}

        level = book.find_element_by_class_name("pb-book-card__level").text
        data["level"] = [int(s) for s in level.split() if s.isdigit()][0]
        print("level: ", data["level"])

        data["name"] = book.find_element_by_class_name("pb-book-card__title").text
        print("name: ", data["name"])

        data["url"] = book.find_element_by_class_name("pb-book-card__link").get_attribute("href")
        print("url: ", data["url"])

        data["file"] = data["url"].rsplit('/', 1)[-1]
        data["file"] = data["file"].rsplit('.', 1)[0]

        data["pdf"] = "http://storyweaver.org.in/v0/stories/download-story/" + data["file"] + ".pdf"
        print("pdf: ", data["pdf"])

        print("-----------------------------------")

        return data

if True:
    browser.get("https://storyweaver.org.in/stories?language=English")

    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'pb-book-card__link'))
        WebDriverWait(browser, 100).until(element_present)
    except TimeoutException:
        print("Page failed to load!")
        browser.close()
        quit()

    bookElements = browser.find_elements_by_class_name("pb-book-card__container")

    books = []

    for bookElement in bookElements:
        books.append(getInfo(bookElement))

def downloadPDF(url):
    browser.get(url)
    
    z = None

    file = ("/home/felix/Downloads/" + url.rsplit('/', 1)[-1]).replace("pdf", "zip")

    print(file)

    while True:
        try:
            z = zipfile.ZipFile(file)
            break
        except FileNotFoundError:
            pass

    d = os.path.abspath(z.extract(url.rsplit('/', 1)[-1], "tmp/"))
    z.close()

    return d

def uploadBook(book):
    image = downloadPDF(book["pdf"])

    browser.get("http://157.131.248.17/html/wp-admin/post-new.php?post_type=book")

    browser.find_element_by_id("title").send_keys(book["name"])

    Select(browser.find_element_by_id("set_language")).select_by_visible_text("anglais")
    Select(browser.find_element_by_id("set_level")).select_by_visible_text(str(book["level"]))

    browser.find_element_by_id("set-post-thumbnail").click()

    WebDriverWait(browser, 100).until(EC.element_to_be_clickable((By.ID, "__wp-uploader-id-1")))

    input_tag = "//input[starts-with(@id,'html5_')]"
    browser.find_element_by_xpath(input_tag).send_keys(image)

    WebDriverWait(browser, 200).until(EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        "button.button.media-button.button-primary.button-large.media-button-select"))
    ).click()

    time.sleep(5)

    browser.find_element_by_id("publish").click()

if True:
    browser.get("http://157.131.248.17/html/wp-admin/")
    browser.find_element_by_id("user_login").send_keys(wordpressUsername)
    browser.find_element_by_id("user_pass").send_keys(wordpressPassword)
    browser.find_element_by_id("wp-submit").click()

    uploadBook(books[0])

print("done")