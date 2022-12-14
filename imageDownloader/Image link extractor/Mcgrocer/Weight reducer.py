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
    driver.set_page_load_timeout(60)

    userName = "hb.mcgrocer@gmail.com"
    passWord = "rakib123xyz"
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
        driver.find_element('xpath','''//div[@id="seller_side_product_table_length"]''').click()
        driver.find_element('xpath', '''//div[@id="seller_side_product_table_length"]//option[@value='50']''').click()
        waitForPageLoad("select option")



    def waitForPageLoad(text="Loading.."):
        element = driver.find_element("xpath", '//div[@class="loader-div"]')
        isLoading = element.get_attribute("style")
        print(text)

        while isLoading.startswith("display: block;"):
            print("waiting for " + text)
            time.sleep(10)
            try:
                isLoading = element.get_attribute("style")

            except Exception:
                pass

    def operations(currentWeight):
        currentWeight = float(currentWeight)

        if currentWeight <= .99:
            return 1
        elif currentWeight >= 1 and currentWeight < 1.99:
            return currentWeight
        elif currentWeight >= 2 and currentWeight < 3.99:
            return currentWeight - 1
        else:
            return currentWeight - 2

    def getCurrentProduct():
        with open('currentPositionLog.txt', mode='a+') as log:
            log.seek(0)
            target = log.read()
            if target == "":
                print(target)
                target = 0

            return int(target)

    def setCurrentProduct(current):
        with open('currentPositionLog.txt', mode='w') as log:
            log.write(str(current))

    def handleError():
        while True:
            try:
                driver.find_element('id', 'top_menu')
                return None

            except exceptions.NoSuchElementException:
                driver.refresh()
                waitForPageLoad()





    try:

        loginToProductsPanel(userName,passWord,loginPageUrl)

        target = getCurrentProduct()
        position = 0



        #Go to next page. Loop
        while True:

            while True:
                handleError()
                nextPage = driver.find_element('xpath','//a[@class="paginate_button next"]')
                productsAction = driver.find_elements('xpath','''//table/tbody/tr[@role='row']/td/div[@class="dropdown element_action"]''')
                products = driver.find_elements('xpath','''//table/tbody/tr[@role='row']/td/div//ul/li[1]''')
                i=0
                # Products remain in page? loop

                for item in productsAction:

                    if target == position:
                        print(target)
                        # Edit products

                        target += 1
                        position += 1
                        setCurrentProduct(target)

                        handleError()
                        driver.execute_script("arguments[0].scrollIntoView(true);", item)
                        item.click()

                        product = products[i]
                        i +=1
                        ActionChains(driver).key_down(Keys.CONTROL).click(product).key_up(Keys.CONTROL).perform()
                        driver.switch_to.window(driver.window_handles[1])
                        handleError()
                        waitForPageLoad()

                        #Has variant? Loop
                        variantsAction = driver.find_elements('xpath','''//div[@id="variant_table"]/table/tbody/tr/td[last()]/div''')
                        variants = driver.find_elements('xpath','''//div[@id="variant_table"]/table/tbody/tr/td[last()]/div/ul/li[1]/a''')
                        j = 0
                        for variantItem in variantsAction:
                            handleError()

                            driver.execute_script("arguments[0].scrollIntoView(true);", variantItem)
                            variantItem.click()
                            variant = variants[j]
                            j += 1
                            ActionChains(driver).key_down(Keys.CONTROL).click(variant).key_up(Keys.CONTROL).perform()
                            driver.switch_to.window(driver.window_handles[2])
                            handleError()
                            waitForPageLoad()

                            #Edit Variant.
                            #time.sleep(3)

                            weightField = driver.find_element('id',"variant_weight")
                            saveButton = driver.find_element('id', "var-form-save-btn")
                            driver.execute_script("arguments[0].scrollIntoView(true);", weightField)
                            currentWeight = weightField.get_attribute('value')

                            #Operations
                            newWeight = operations(currentWeight)
                            time.sleep(1)

                            weightField.clear()
                           # time.sleep(2)
                            weightField.send_keys(newWeight)
                            #time.sleep(2)
                            saveButton.click()
                            time.sleep(3)
                            handleError()
                            waitForPageLoad()
                            #time.sleep(3)



                            driver.close()
                            driver.switch_to.window(driver.window_handles[1])



                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    else:
                        position += 1
                        i += 1


                nextPage.click()
                handleError()
                waitForPageLoad()
    except exceptions.TimeoutException:
        print("Browser Timeout again starting")
        driver.quit()
        time.sleep(10)
        main()
    except Exception:
        driver.quit()
        print("un wanted stop")





main()
