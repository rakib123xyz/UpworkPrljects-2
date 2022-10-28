from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

driverPath = "C:\webdriver\chromedriver_win32\chromedriver.exe"
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
chrome_options = webdriver.ChromeOptions()
chrome_options.headless = False
chrome_options.add_argument(f'user-agent={user_agent}')
prefs ={"download.default_directory":r"C:\Users\Rakib\PycharmProjects\UpworkProjectHelper\test_instagram\Hashtag-to-user\Output"}
chrome_options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=driverPath)
def login():
    username= "princemostakim1"
    password ="1234islam"
    userxpath ='''//input[@name="username"]'''
    passXpath = '''//input[@name="password"]'''
    submitXpath ='''//button[@type="submit"]'''
    time.sleep(30)
    driver.get("https://www.instagram.com/")
    time.sleep(20)
    driver.find_element('xpath',userxpath).send_keys(username)
    driver.find_element('xpath',passXpath).send_keys(password)
    driver.find_element('xpath',submitXpath).click()
    time.sleep(10)
    print("Loged In")
    return 0

def end():

    isDisplayed =EC.presence_of_element_located(('xpath','//div[@class=" _aaqg _aaqh"]'))
    if isDisplayed:
        return False
    else:
        time.sleep(60)
        if isDisplayed:
            return False
        else:
            return True

def getNext():
    link = driver.current_url
    nextButton = WebDriverWait(driver, 20).until(EC.visibility_of_element_located(('xpath', '//div[@class=" _aaqg _aaqh"]')))
    nextButton.click()
    return link

def save(link):
    newItem = link + "\n"
    with open("post link.txt",mode="a") as file:
        file.writelines(newItem)
        file.close()

def browse():
    LinkList = []
    waitPoint = 100
    driver.get("https://www.instagram.com/explore/tags/coachingdecarreira/")
    postLink = WebDriverWait(driver, 20).until(EC.visibility_of_element_located(('xpath', '//div[@class="_ac7v _aang"]/div/a')))
    postLink.click()
    while not(end()):
        try:
            link = getNext()
            LinkList.append(link)
            save(link)
            print("Totall: " +str(len(LinkList)) )
            if len(LinkList) == waitPoint:
                print("waiting 1 minutes.")
                time.sleep(60)
                waitPoint += 100
        except:
            print("Somthing is Wrong!")
            print("Trying Againg....")







login()

browse()
