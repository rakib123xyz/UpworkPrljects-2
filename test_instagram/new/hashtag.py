
# This sample code uses the Appium python client v2
# pip install Appium-Python-Client
# Then you can paste this into a file and simply run with Python
import time
from bisect import bisect_left
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
    time.sleep(2)
    searchBox = driver.find_element(AppiumBy.ID, value="com.instagram.android:id/action_bar_search_edit_text")
    searchBox.click()

login()



# search hashtags
hashtag = "#coachingdecarreira"
scraped_Username = []
scraped_Username.sort()
def searchHashTag(hashtag):
    time.sleep(2)
    searchbox = driver.find_element(by=AppiumBy.ID, value="com.instagram.android:id/action_bar_search_edit_text")
    searchbox.click()


    searchbox.send_keys(hashtag)
    time.sleep(1)
    driver.press_keycode(66)

    time.sleep(1)
    tagTab =WebDriverWait(driver,10).until(EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Tags")))
    tagTab.click()

    tagLink = WebDriverWait(driver,20).until(EC.visibility_of_element_located((AppiumBy.ID, "com.instagram.android:id/row_hashtag_textview_tag_name")))
    tagLink.click()

def scrollDown():
    actions = ActionChains(driver)
    actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
    actions.w3c_actions.pointer_action.move_to_location(350, 1191)
    actions.w3c_actions.pointer_action.pointer_down()

    actions.w3c_actions.pointer_action.move_to_location(350, 633)
    time.sleep(.1)
    actions.w3c_actions.pointer_action.release()
    actions.perform()



def search(alist, item):
    'Locate the leftmost value exactly equal to item'
    i = bisect_left(alist, item)
    if i != len(alist) and alist[i] == item:
        return False
    else:
        return True

def capture(userElm):
    userElm.click()
    time.sleep(2)

    backButton = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="Back")

    backButton.click()
    time.sleep(1)


def check(username):
    oldUser = scraped_Username
    is_new = search(oldUser,username)
    if is_new:
        scraped_Username.append(username)
        scraped_Username.sort()
        capture(userElm)
        return len(oldUser)
    else:
        pass










searchHashTag(hashtag)

postLink = WebDriverWait(driver,20).until(EC.visibility_of_element_located((AppiumBy.ID, "com.instagram.android:id/image_button")))
postLink.click()




while True:
    userName = ""
    try:
        userElm = WebDriverWait(driver,5).until(EC.visibility_of_element_located((AppiumBy.ID, "com.instagram.android:id/row_feed_photo_profile_name")))
        userName = userElm.text
        time.sleep(1)
        count = check(userName)
        if count:
            print(count)



        scrollDown()
    except:
        pass


