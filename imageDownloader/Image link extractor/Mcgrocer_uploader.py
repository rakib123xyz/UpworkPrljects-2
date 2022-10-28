'''
This script is for upload product to shopify webkul seller dashboard.
It has two method to upload.
    1. is for upload by csv along with the image inside the csv.
    2. is for upload by product.csv,image.zip,image.csv

    in order to work with this script you have to import the mentioned package.
    os, time, shutil, selenium,
    webdriver should be installed also.
'''




import os
import sys
import time
import selenium
from os import walk
import shutil
from selenium import webdriver

user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'
chrome_options = webdriver.ChromeOptions()
chrome_options.headless = False
chrome_options.add_argument(f'user-agent={user_agent}')
driver = webdriver.Chrome(chrome_options=chrome_options,executable_path="../../chromedriver.exe")

userName = "Direct.mcgrocer@gmail.com"
passWord = "MdRakiburIslam/1908/"
loginPageUrl = "https://seller.mcgrocer.com/"
uploadPageUrl = "https://seller.mcgrocer.com/index.php?p=add_product_by_csv"


def loginToProductsPanel(userName,passWord,loginPageUrl):
    userName = userName
    password = passWord
    login_page_url = loginPageUrl
    driver.get(login_page_url)
    emailFeild = '''//input[@type="email"]'''
    passWordFeild = '''//input[@type="password"]'''
    submidFeild = '''//*[@id="login_form"]/div[4]/div'''

    driver.find_element("xpath", emailFeild).send_keys(userName)
    driver.find_element("xpath", passWordFeild).send_keys(password)
    time.sleep(1)
    driver.find_element('xpath', submidFeild).click()
    waitForPageLoad()

def waitForPageLoad(text="Loading.."):
    element = driver.find_element("xpath",'//div[@class="loader-div"]')
    isLoading = element.get_attribute("style")
    print(isLoading)
    print(text)

    while isLoading.startswith("display: block;"):

        time.sleep(15)
        try:
            isLoading = element.get_attribute("style")
            print(isLoading)
        except:
            print("submited")
            return

def UploadByMethod1(userName,passWord,loginPageUrl,uploadPageUrl):

    loginToProductsPanel(userName,passWord,loginPageUrl)

    uploadCsvFeild = '''//*[@id="product_csv_file_m2"]'''
    upload_page_url = uploadPageUrl
    validatButton = '''//*[@id="product_csv_validate_m2"]'''
    submitButton = '''//*[@id="product_csv_submit_m2"]'''

    all_files = os.listdir("Mykuns/mykuns_temp/")
    csv_files = list(filter(lambda f: f.endswith('.csv'), all_files))
    print(csv_files)

    for item in csv_files:
        driver.get(upload_page_url)

        path = "temp/" + item
        absPath = r"C:\Users\learn\PycharmProjects\UpworkProjectHelper\imageDownloader\Image link extractor/"

        productsCsv = absPath + path

        driver.find_element('xpath', uploadCsvFeild).send_keys(productsCsv)

        driver.find_element('xpath', validatButton).click()
        waitForPageLoad("Validating")

        className= driver.find_element('xpath', submitButton).get_attribute("class")
        if className.find("enabled-btn"):
            driver.find_element('xpath', submitButton).click()
            waitForPageLoad("Submitting")
            shutil.move(productsCsv, "Mykuns/mykuns_Done/")
            print("uploaded successfully")

        else:
            print("This csv hase problem")

def UploadByMethod2(userName,passWord,loginPageUrl,uploadPageUrl):

    loginToProductsPanel(userName,passWord,loginPageUrl)


    upload_page_url = uploadPageUrl
    uploadCsvFeild = '''//*[@id="product_csv_file"]'''
    uploadZipFeild = '''//*[@id="image_zip_file"]'''
    uploadImageFeild = '''//*[@id="image_csv_file"]'''
    validatButton ='''//*[@id="product_csv_validate"]'''
    submitButton = '''//*[@id="product_csv_submit"]'''

    dirList = os.listdir('Mykuns/mykuns_temp/')
    absPath = r"C:\Users\learn\PycharmProjects\UpworkProjectHelper\imageDownloader\Image link extractor/"
    # abs path shuld be according to script file absollute file path.
    print(dirList)

    for item in dirList:
        driver.get(upload_page_url)

        path ="temp/"+ item
        imageZip = absPath+path +"/images.zip"
        imageCsv = absPath+path + "/image.csv"
        productsCsv = absPath+path + "/products.csv"

        driver.find_element('xpath',uploadCsvFeild).send_keys(productsCsv)
        driver.find_element('xpath', uploadZipFeild).send_keys(imageZip)
        driver.find_element('xpath', uploadImageFeild).send_keys(imageCsv)
        driver.find_element('xpath',validatButton ).click()
        waitForPageLoad()
        driver.find_element('xpath', submitButton).click()
        waitForPageLoad()


UploadByMethod1(userName,passWord,loginPageUrl,uploadPageUrl)





