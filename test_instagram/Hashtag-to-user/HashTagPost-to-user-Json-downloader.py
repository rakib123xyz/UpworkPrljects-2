from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys

driverPath = "C:\webdriver\chromedriver_win32\chromedriver.exe"
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
chrome_options = webdriver.ChromeOptions()
chrome_options.headless = False
chrome_options.add_argument(f'user-agent={user_agent}')
prefs ={"download.default_directory":r"C:\Users\Rakib\PycharmProjects\UpworkProjectHelper\test_instagram\Hashtag-to-user\Output"}
chrome_options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=driverPath)
def login():
    username= "mosaddekislam1"
    password ="1234islam"
    userxpath ='''//input[@name="username"]'''
    passXpath = '''//input[@name="password"]'''
    submitXpath ='''//button[@class="sqdOP  L3NKy   y3zKF     "]'''
    time.sleep(30)
    driver.get("https://www.instagram.com/")
    time.sleep(8)
    driver.find_element('xpath',userxpath).send_keys(username)
    driver.find_element('xpath',passXpath).send_keys(password)
    driver.find_element('xpath',submitXpath).click()
    time.sleep(10)
    print("Loged In")
    return 0

def scrollDown(speed=10,step=5):
    i = 0

    while i <= step:

        driver.execute_script('''window.scrollTo({
          top: window.pageYOffset +''' + str(speed)+''',
          left: 0,
          behavior: 'smooth'
        });''')
        time.sleep(.021)

        i +=1


def scrollUp(speed=10,step=5):
    i = 0
    height = speed
    while i <= step:

        driver.execute_script('''window.scrollTo({
          top:  window.pageYOffset -''' + str(speed)+''',
          left: 0,
          behavior: 'smooth'
        });''')
        time.sleep(.021)

        i +=1

def browse():
    pageCount = 1
    hashTagUrl = "https://www.instagram.com/explore/tags/reginaweddingphotographer/"
    driver.get(hashTagUrl)
    time.sleep(10)
    instaTab = driver.window_handles[0]
    driver.execute_script("window.open('http://127.0.0.1:8081/#/flows/138a940d-0ffe-4fd8-88af-f4d664a5a681/response?s=https%3A%2F%2Fi.instagram.com%2Fapi%2Fv1%2Ftags%2Freginaweddingphotographer%2Fsections%2F');")
    driver.implicitly_wait(10)
    mitmTab = driver.window_handles[1]

    def scroll():

        driver.switch_to.window(instaTab)

        i =0
        while i <=10:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            for x in range(2):
                scrollUp(100,52)
                scrollDown(100,50)

            time.sleep(2)

            i +=1
            print(i)



    def saveRespons():
        driver.switch_to.window(mitmTab)
        time.sleep(1)
        responsXpaths = '''//tr[@class="has-request has-response"]'''
        flows = driver.find_elements('xpath',responsXpaths)
        print(flows)
        for flow in flows:
            try:

                flow.click()
                downloadButton = driver.find_element('xpath', '''//button/i[@class="fa fa-download"]''')
                downloadButton.click()
                downloadResponse = driver.find_element('xpath', '''//ul[@class="dropdown-menu show"]/li[2]''')
                downloadResponse.click()
            except:
                continue
        fileButton = driver.find_element('xpath', '''//a[@class="pull-left special"]''')
        fileButton.click()
        deleteButton = driver.find_element('xpath', '''//ul/li/a/i[@class="fa fa-fw fa-trash"]''')
        deleteButton.click()
        driver.switch_to.alert.accept()

    load = 0
    while True:

        scroll()
        saveRespons()
        load +=1
        print("load: " + str(load))


login()
browse()