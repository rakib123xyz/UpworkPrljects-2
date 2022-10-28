
# This sample code uses the Appium python client v2
# pip install Appium-Python-Client
# Then you can paste this into a file and simply run with Python
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# now, to clear the screen

# For W3C actions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

caps = {}
caps["platformName"] = "android"
caps["appium:platformVersion"] = "5.1.1"
caps["appium:deviceName"] = "127.0.0.1:21503"
caps["appium:automationName"] = "uiautomator2"
caps["appium:appPackage"] = "com.instagram.android"
caps["appium:appActivity"] = "com.instagram.mainactivity.MainActivity"
caps["appium:ensureWebviewsHavePages"] = True
caps["appium:nativeWebScreenshot"] = True
caps["appium:newCommandTimeout"] = 3600
caps["appium:connectHardwareKeyboard"] = True
caps["appium:noReset"] = False
caps["appium:udid"] = "127.0.0.1:21503"
caps["appium:systemPort"] = "8290"


driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)




def login():

    loginButton = WebDriverWait(driver,60).until(EC.presence_of_element_located((AppiumBy.ID,"com.instagram.android:id/log_in_button")))
    loginButton.click()
    time.sleep(10)

    logingUsername = driver.find_element(AppiumBy.ID, value="com.instagram.android:id/login_username")
    logingUsername.send_keys("rakib123xyz")
    password = driver.find_element(AppiumBy.ID, value="com.instagram.android:id/password")
    password.send_keys("islam123")
    submitButton = driver.find_element(AppiumBy.ID, value="com.instagram.android:id/button_text")
    submitButton.click()

    searchButton = WebDriverWait(driver,20).until(EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID,"Search and explore")))
    searchButton.click()
    searchBox = driver.find_element(AppiumBy.ID, value="com.instagram.android:id/action_bar_search_edit_text")
    searchBox.click()

login()


file = open("Input/usernames.txt", "r")

currentText = file.read()
usernames = currentText.split(",")
file.close()

emails = []
scrapedData = []
startTime = time.time()
remainingUser = len(usernames)
i = 0

loopCount = 0



for name in usernames:


    if loopCount > 49:
        retry = True
        while retry:
            try:
                driver.quit()
                time.sleep(5)
                driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)
                time.sleep(20)
                login()
                loopCount = 0
                retry = False
            except:
                pass



    try:
        dataRow = {
            "username": "",
            "email": "",
            "phone": "",
            "followerCount": "",
            "followingsCount": "",
            "postCount": "",
            "fullName": "",
            "category": "",
            "bio": "",
            "website": "",
            "address": ""
        }

        time.sleep(2)
        searchbox = driver.find_element(by=AppiumBy.ID, value="com.instagram.android:id/action_bar_search_edit_text")
        searchbox.click()

        if i > 0 :
            searchbox.clear()

            time.sleep(1)
        i += 1

        searchbox.send_keys(name)
        time.sleep(1)
        driver.press_keycode(66)

        time.sleep(1)




        accountTab =WebDriverWait(driver,10).until(EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Accounts")))
        accountTab.click()

        userLink = WebDriverWait(driver,20).until(EC.visibility_of_element_located((AppiumBy.ID, "com.instagram.android:id/row_search_user_username")))
        userLink.click()

        #this part need to be perfect

        try:
            dataRow["username"]= WebDriverWait(driver,20).until(EC.visibility_of_element_located((AppiumBy.ID,"com.instagram.android:id/action_bar_title"))).text

        except:
            pass


        try:
            dataRow["postCount"]=WebDriverWait(driver,2).until(EC.visibility_of_element_located((AppiumBy.ID,"com.instagram.android:id/row_profile_header_textview_post_count"))).text


        except:
            pass

        try:
            dataRow["followerCount"] = WebDriverWait(driver,2).until(EC.visibility_of_element_located((AppiumBy.ID,"com.instagram.android:id/row_profile_header_textview_followers_count" ))).text

        except:
            pass
        try:
            dataRow["followingsCount"] =WebDriverWait(driver,2).until(EC.visibility_of_element_located((AppiumBy.ID,"com.instagram.android:id/row_profile_header_textview_following_count"))).text



        except:
            pass
        try:
            dataRow["fullName"] = WebDriverWait(driver,2).until(EC.visibility_of_element_located((AppiumBy.ID,"com.instagram.android:id/profile_header_full_name"))).text



        except:
            pass
        try:
            dataRow["category"] = WebDriverWait(driver,2).until(EC.visibility_of_element_located((AppiumBy.ID,"com.instagram.android:id/profile_header_business_category"))).text



        except:
            pass
        try:
            dataRow["bio"] =WebDriverWait(driver,2).until(EC.visibility_of_element_located((AppiumBy.ID,"com.instagram.android:id/profile_header_bio_text"))).text



        except:
            pass
        try:
            dataRow["website"] = WebDriverWait(driver,2).until(EC.visibility_of_element_located((AppiumBy.ID,"com.instagram.android:id/profile_header_website"))).text



        except:
            pass
        try:
            dataRow["address"] = WebDriverWait(driver,2).until(EC.visibility_of_element_located((AppiumBy.ID,"com.instagram.android:id/profile_header_business_address"))).text



        except:
            pass



        try:

            contactButton =WebDriverWait(driver,3).until(EC.visibility_of_element_located((AppiumBy.XPATH,"//android.widget.TextView[@text='Contact']")))

            contactButton.click()

            contactInformation = driver.find_elements(by=AppiumBy.ID, value="com.instagram.android:id/contact_option_sub_text")

            for item in contactInformation:
                text = item.text

                if text.find("@") != -1:
                    dataRow["email"] =text
                    emails.append(text)

                elif text.find("+") != -1:
                    dataRow["phone"] = text

            backButton = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="Back")
            backButton.click()
            time.sleep(1)
            backButton.click()

        except:

            backButton = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="Back")
            backButton.click()

            pass


        df = pd.DataFrame.from_dict([dataRow])
        csv = df.to_csv("Output/result1.csv",mode= "a", sep=",", index=False, header=False, encoding='utf-8')


        name = name + ","
        with open("Input/usernames.txt", 'w') as update:
            # Delete
            update.truncate(0)
            currentText = currentText.replace(name,"")
            remainingUser = len(currentText.split(","))

            # Write

            update.write(currentText)


            file.close()



            timeTaken = (time.time() - startTime) / 60
            scrapedItem = len(usernames) - remainingUser
            emailfound = len(list(set(emails)))

            print("Loop : " + str(loopCount) + ' Time took: ' + str(int(timeTaken)) + " minutes " + " Remaining usernames: " + str(remainingUser) + " Scraped: " + str(scrapedItem) + " Email found: " + str(emailfound) + " Current User: " + name + " User mail: " + dataRow["email"])

    except:
        pass

    loopCount += 1





