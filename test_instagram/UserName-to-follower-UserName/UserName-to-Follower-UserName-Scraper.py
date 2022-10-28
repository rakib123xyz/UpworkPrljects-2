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
time.sleep(30)

def login():
    username= "rakib123xyz"
    password ="pg.ajgtwmdajmt"
    logButton ='''//*[@id="react-root"]/section/main/article/div/div/div[2]/div[3]/button[1]'''
    userxpath ='''//input[@name="username"]'''
    passXpath = '''//input[@name="password"]'''
    submitXpath ='''//button[@type="submit"]'''
    driver.get("https://www.instagram.com/")
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


login()
driver.get(_list[1])

driver.find_element('xpath','''//ul[@class="_aa_7" or @class=" _aa_8"]/li[2]''').click()
driver.implicitly_wait(20)
driver.find_element('xpath','''//div[@class="_aano"]/div[1]/div[1]/div[1]''').click()




startTime = time.time()
UsernameList = []
userSize = len(UsernameList)
go = True
while go:
    for i in range(100):
        time.sleep(2)
        driver.find_element('tag name','body').send_keys(Keys.SPACE)
    userItems = driver.find_elements('xpath','''//div[@class=" _ab8y  _ab94 _ab97 _ab9f _ab9k _ab9p _abcm"]''')

    for user in userItems:
        UsernameList.append(user.text)
    UsernameList= list(set(UsernameList))
    if len(UsernameList) > userSize:
        userSize = len(UsernameList)
        timeTaken = (time.time() - startTime) / 60
        print("User scraped : " + str(userSize)+ "  Time taken : " + str(int(timeTaken)) + " minutes")

        with open(r'Output/username.txt', 'w',) as fp:
            for item in UsernameList:
                # write each item on a new line
                fp.write("%s\n" % item)
        fp.close()
    else:
        go = False









