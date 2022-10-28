from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys




driverPath = "C:\webdriver\chromedriver_win32\chromedriver.exe"
user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36'
chrome_options = webdriver.ChromeOptions()
chrome_options.headless = False
chrome_options.add_argument(f'user-agent={user_agent}')
prefs ={"download.default_directory":r"C:\Users\Rakib\PycharmProjects\UpworkProjectHelper\test_instagram\Hashtag-to-user\Output"}
chrome_options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=driverPath)
time.sleep(0)

def login():
    username= "rakib123xyz"
    password ="islam123"
    logButton ='''//*[@id="react-root"]/section/main/article/div/div/div[2]/div[3]/button[1]'''
    userxpath ='''//input[@name="username"]'''
    passXpath = '''//input[@name="password"]'''
    submitXpath ='''//button[@type="submit"]'''
    driver.get("https://www.instagram.com/")
    time.sleep(5)
    driver.implicitly_wait(10)
    driver.find_element('xpath', logButton).click()
    driver.implicitly_wait(5)

    driver.find_element('xpath',userxpath).send_keys(username)
    driver.find_element('xpath',passXpath).send_keys(password)
    driver.find_element('xpath',submitXpath).click()
    driver.implicitly_wait(5)
    time.sleep(10)
    print("Loged In")
    return 0








with open(file="Input/Profiles.text",mode="r",encoding="utf-8") as userProfile:
    _list = list(userProfile)


def gotoDistinition():
    time.sleep(10)
    login()
    driver.get(_list[0])

    driver.find_element('xpath','''//ul[@class="_aa_7" or @class=" _aa_8"]/li[2]''').click()
    driver.implicitly_wait(20)
    driver.find_element('xpath','''//div[@class="_aano"]/div[1]/div[1]/div[1]''').click()

def scroll(x):
    for i in range(x):
        driver.find_element('tag name',"body").send_keys(Keys.SPACE)
        driver.find_element('tag name', "body").send_keys(Keys.SPACE)
        driver.find_element('tag name', "body").send_keys(Keys.SPACE)
        time.sleep(3)

def ScrapLast(x):

    elNames = driver.find_elements('xpath','''//div[@class=" _ab8y  _ab94 _ab97 _ab9f _ab9k _ab9p _abcm"]''')
    last100 = []
    for item in range(x):
        try:
            username = elNames[-item].text
            last100.append(username)

        except:
            pass
    return last100


def saveIntofile(filename,previouslist,newlist):
    newData = len(newlist)- len(previouslist)
    if newData == 0 :
        return False
    with open(r'Output/'+filename, 'a') as fp:
        for x in range(1,newData):
            if x > 0:

                fp.write("\n" + newlist[-x])

    fp.close()
    return True





def output(strtTime,list):
    timeTaken = (time.time() - strtTime) / 60
    userSize = len(list)
    print("Time took : " + str(timeTaken) + "  User Scraped : " + str(userSize))


def main():
    startTime = time.time()
    gotoDistinition()
    previousList = []
    newList = []
    while True:


        scroll(10)
        scrapData = ScrapLast(200)
        for item in scrapData:
            newList.append(item)

        newList = list(set(newList))

        stutas = saveIntofile("username.txt",previousList,newList)
        previousList = newList[:]
        output(startTime,previousList)
        if stutas == False:
            break





main()







