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
from selenium.common import exceptions

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from Operations import operations
import Operations



# def moveToProducts(terget=0):
#     terget = terget
#     current = 0
#     if terget == 0:
#         pass
#     else:
#         while terget < current:
#             # Go to next page. Loop
#             nextPage = driver.find_element('xpath', '//a[@class="paginate_button next"]')
#
#             # Products remain in page? loop
#             productsAction = driver.find_elements('xpath',
#                                                   '''//table/tbody/tr[@role='row']/td/div[@class="dropdown element_action"]''')
#             for item in productsAction:
#                 if current < terget:
#                     current += 1
#                 else:
#                     return
#
#             nextPage.click()
#             waitForPageLoad()

# option = '''//table/tbody/tr[@role='row']/td/div[@class="dropdown element_action"]'''
#
# edit = '''//table/tbody/tr[@role='row']/td/div/ul//a[@class="prod_edit"]'''
#
#
# nextPage = driver.find_element('xpath','//a[@class="paginate_button next"]')


def main():

    user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = False
    chrome_options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="../../../chromedriver.exe")
    driver.set_page_load_timeout(30)

    userName = Operations.userName
    passWord = Operations.passWord
    loginPageUrl = "https://seller.mcgrocer.com/index.php?p=login"
    productsPage = "https://seller.mcgrocer.com/index.php?p=product"

    def loginToProductsPanel(userName, passWord, loginPageUrl):
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
        driver.get('https://seller.mcgrocer.com/index.php?p=product')
        waitForPageLoad()
        # driver.find_element('xpath','''//div[@id="seller_side_product_table_length"]''').click()
        # driver.find_element('xpath', '''//div[@id="seller_side_product_table_length"]//option[@value='50']''').click()
        # waitForPageLoad("select option")



    def waitForPageLoad(text="Loading.."):
        element = driver.find_element("xpath", '//div[@class="loader-div"]')
        isLoading = element.get_attribute("style")
        print(text)

        while isLoading.startswith("display: block;"):
            print("waiting for " + text)
            time.sleep(3)
            try:
                isLoading = element.get_attribute("style")

            except Exception:
                pass

    # def operations(currentWeight):
    #     currentWeight = float(currentWeight)
    #
    #     if currentWeight <= .99:
    #         return 1
    #     elif currentWeight >= 1 and currentWeight < 1.99:
    #         return currentWeight
    #     elif currentWeight >= 2 and currentWeight < 3.99:
    #         return currentWeight - 1
    #     else:
    #         return currentWeight - 2

    def getCurrentProduct():
        with open('currentPositionLog2.txt', mode='a+') as log:
            log.seek(0)
            target = log.read()
            if target == "":
                print(target)
                target = 0

            return int(target)

    def setCurrentProduct(current):
        with open('currentPositionLog2.txt', mode='w') as log:
            log.write(str(current))


    def handleError():

        while True:
            try:
                driver.find_element('id', 'top_menu')
                return None

            except exceptions.NoSuchElementException:
                driver.refresh()
                waitForPageLoad()

    def read_in_chunks(file_object, chunk_size=1024):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        while True:
            data = file_object.readline()
            if not data:
                break
            yield data



    try:

        loginToProductsPanel(userName, passWord, loginPageUrl)
        baseUrl = "https://seller.mcgrocer.com/index.php?p=add_product&pid="
        with open('Id_list2.txt', mode="r") as f:
            ids = sorted(list(set(f.readlines())))


            index = 0
            for id in ids:
                index += 1
                print("Index : " + str(index))

                target = getCurrentProduct()

                print("Id : " + str(id))

                editUrl = baseUrl + str(id)



                if int(id)==int(target) or target == 0  :



                    #Prssesing goes here
                    driver.get(editUrl)

                    # Has variant? Loop
                    variantsAction = driver.find_elements('xpath',
                                                          '''//div[@id="variant_table"]/table/tbody/tr/td[last()]/div''')
                    editSelector = driver.find_elements('xpath',
                                                    '''//div[@id="variant_table"]/table/tbody/tr/td[last()]/div/ul/li[1]/a''')
                    j = 0
                    for variantItem in variantsAction:
                        handleError()

                        driver.execute_script("arguments[0].scrollIntoView(true);", variantItem)
                        variantItem.click()
                        variant = editSelector[j]
                        j += 1
                        ActionChains(driver).key_down(Keys.CONTROL).click(variant).key_up(Keys.CONTROL).perform()
                        driver.switch_to.window(driver.window_handles[1])
                        handleError()
                        waitForPageLoad()

                        # Edit Variant.
                        # time.sleep(3)

                        weightField = driver.find_element('id', "variant_weight")
                        saveButton = driver.find_element('id', "var-form-save-btn")
                        driver.execute_script("arguments[0].scrollIntoView(true);", weightField)
                        currentWeight = weightField.get_attribute('value')

                        # Operations
                        newWeight = operations(currentWeight)
                        #time.sleep(4)

                        weightField.clear()
                        #time.sleep(2)
                        weightField.send_keys(newWeight)
                        #time.sleep(2)
                        if Operations.save == True:
                            saveButton.click()
                        setCurrentProduct(ids[index])
                        #time.sleep(3)
                        handleError()
                        waitForPageLoad()
                        time.sleep(3)

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
    except exceptions.TimeoutException:
        driver.quit()
        main()
    except Exception:
        print("Stoped")









main()