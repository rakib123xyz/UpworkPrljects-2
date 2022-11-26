#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
__author__ = ["Sun (Phu Quy)"]
__copyright__ = "Copyright 2020, Sun (Phu Quy)"
__credits__ = ["Sun (Phu Quy)"]
__license__ = "GPL"
__version__ = "1.0"
__status__ = "Production"
__author__ = "Sun (Phu Quy)"
__email__ = "dangphuquybkhn@gmail.com"

import socket

hostname = socket.gethostname()
if 'MD104' in hostname or 'MB2018' in hostname:
    ISLOCAL = True
else:
    ISLOCAL = False

from discord import Webhook, RequestsWebhookAdapter, Embed, Colour
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, UnexpectedTagNameException
import pickle
import logging
import sys
import time
import os
import zipfile
import random
# from PIL import Image
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config

logger = logging.getLogger(__name__)


# ======================================= BEGIN WEB BROWSER ================================================
def read_text_file_to_list(filePath):
    ''' Read text file line by line to list '''
    if not os.path.isfile(filePath):
        logger.debug('File %s not found', filePath)
        return []

    with open(filePath, encoding="utf-8-sig") as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content


def notifyEmail(subject, message, toaddr):
    fromaddr = config.user_gmail
    password = config.pass_gmail
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddr)
    msg['Subject'] = subject
    body = message
    msg.attach(MIMEText(body, 'plain'))
    try:
        print('sending mail to {} on {}'.format(toaddr, subject))
        mailServer = smtplib.SMTP('smtp.gmail.com', 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(fromaddr, password)
        mailServer.sendmail(fromaddr, toaddr, msg.as_string())
        mailServer.close()
    except Exception as e:
        print(str(e))


def send_discord_embed(title, url, price, thumbnail, site, disc_hook):
    embed = Embed(title=title, colour=Colour(0x4ba4b),
                  url=site, description="NEW LEAD! " + '\n' + url,
                  timestamp=Embed.Empty)

    embed.set_footer(text="moon • " + str(datetime.now()),
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/FullMoon2010.jpg/253px-FullMoon2010.jpg")

    # embed.add_field(name="PRIS", value=price)

    webhook = Webhook.from_url(disc_hook, adapter=RequestsWebhookAdapter())
    webhook.send(embed=embed)


class WebBrowser():
    """Class web browser"""

    def __init__(self, currentPath=None, driver=None,
                 timeout=10, isDisableImage=False,
                 isDisableJavascript=False, downloadPath=None,
                 isMaximum=False, isHeadless=False,
                 proxyFilePath=None, changeProxyTotal=None,
                 isMobile=False, mobileUserAgentFilePath=None,
                 userAgentFilePath=None, userDataDir=None
                 ):
        if currentPath:
            self._currentPath = currentPath
        else:
            self._currentPath = os.path.dirname(os.path.realpath(sys.argv[0]))
        self._driver = driver
        self._timeout = timeout
        self._isDisableImage = isDisableImage
        self._isDisableJavascript = isDisableJavascript
        if downloadPath:
            self._downloadPath = downloadPath
        else:
            self._downloadPath = self._currentPath
        self._isHeadLess = isHeadless
        self._isMaximum = isMaximum
        self._proxyFilePath = proxyFilePath
        self._changeProxyTotal = changeProxyTotal
        self._changeProxyCounter = 0
        self._currentProxyIp = 0
        self._isMobile = isMobile
        self._mobileUserAgentFilePath = mobileUserAgentFilePath
        self._restartBrowserCounter = 0
        self._userAgentFilePath = userAgentFilePath
        self._userDataDir = userDataDir
        self.start()

    def get_downloaded_file_list(self):
        """get completed download list
        Returns:
            list: list of downloaded file
        """
        if not self._driver.current_url.startswith("chrome://downloads"):
            self._driver.get("chrome://downloads/")

        return self._driver.execute_script("""
            var items = document.querySelector('downloads-manager')
                .shadowRoot.getElementById('downloadsList').items;
            if (items.every(e => e.state === "COMPLETE"))
                return items.map(e => e.fileUrl || e.file_url);
            """)

    def get_current_window(self):
        return self._driver.current_window_handle

    def enable_headless_download(self):
        self._driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior',
                  'params': {'behavior': 'allow', 'downloadPath': self._downloadPath}}
        self._driver.execute("send_command", params)

    def switch_2_window(self, window):
        self._driver.switch_to_window(window)

    def is_page_loaded(self, windows=None):
        # logger.info("Checking if {} page is loaded.".format(self._driver.current_url))
        try:
            page_state = self._driver.execute_script('return document.readyState;')
            return page_state == 'complete'
        except:
            return False

    def close_other_loaded_windows(self, window):
        for w in self._driver.window_handles:
            if w not in window:
                self._driver.switch_to.window(w)
                time.sleep(2)
                while not self.is_page_loaded(w):
                    time.sleep(2)
                self._driver.close()
        # switch to main window
        self._driver.switch_to.window(window)

    def close_other_windows(self, window):
        for w in self._driver.window_handles:
            if w not in window:
                self._driver.switch_to.window(w)
                time.sleep(2)
                # while not self.isPageLoaded(w):
                #     time.sleep(2)
                self._driver.close()
        # switch to main window
        self._driver.switch_to.window(window)

    def get_cookie(self):
        cookies_list = self._driver.get_cookies()
        cookies_dict = {}
        for cookie in cookies_list:
            cookies_dict[cookie['name']] = cookie['value']

        return cookies_dict

    def clear_cookie(self):
        return self._driver.delete_all_cookies()

    def save_cookie(self, filePath):
        pickle.dump(self._driver.get_cookies(), open(filePath, "wb"))

    def load_cookie(self, filePath):
        if os.path.isfile(filePath):
            cookies = pickle.load(open(filePath, "rb"))
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                self._driver.add_cookie(cookie)

    def add_cookie(self, name, value):
        cookie = {
            'name': name,
            'value': value
        }
        self._driver.add_cookie(cookie)

    def get_currentURL(self):
        return self._driver.current_url

    def get_page_source(self):
        return self._driver.page_source

    # By Index
    # By Name or Id
    # By Web Element
    def switch_to_frame_by_name(self, name, timeout=None):
        ''' Get one item by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((By.NAME, name))
            )
            self._driver.switch_to_frame(name)
            return element
        except TimeoutException:
            logger.info(' Not found : %s', name)
            logger.debug('%s', TimeoutException)
            return None

    def switch_to_frame_by_id(self, name, timeout=None):
        ''' Get one item by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((By.ID, name))
            )
            self._driver.switch_to.frame(element)
            # return element
        except TimeoutException:
            logger.info(' Not found : %s', name)
            logger.debug('%s', TimeoutException)
            # return None

    def switch_to_lastest_window(self):
        # wait to make sure there are two windows open
        WebDriverWait(self._driver, 10).until(lambda d: len(d.window_handles) > 1)
        self._driver.switch_to_window(self._driver.window_handles[-1])
        # wait to make sure the new window is loaded
        WebDriverWait(self._driver, 10).until(lambda d: d.title != "")

    def close_current_windows(self):
        self._driver.close()
        self._driver.switch_to_window(self._driver.window_handles[-1])

    def find_visible_by_xpath(self, locator, timeout=None):
        ''' Get one item by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, locator))
            )
            return element
        except TimeoutException:
            # logger.info(' Find by xpath not found : %s', locator)
            # logger.debug('%s', TimeoutException)
            return None

    def find_elements_by_name(self, locator, timeout=None):
        ''' Get one item by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            a_elements = self._driver.find_elements(By.TAG_NAME, locator)
            return a_elements
        except TimeoutException:
            # logger.info(' Find by xpath not found : %s', locator)
            # logger.debug('%s', TimeoutException)
            return None

    def find_by_xpath(self, locator, timeout=None):
        ''' Get one item by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, locator))
            )
            return element
        except TimeoutException:
            # logger.info(' Find by xpath not found : %s', locator)
            # logger.debug('%s', TimeoutException)
            return None

    def find_by_xpath_from_element(self, sel, locator, timeout=None):
        ''' Get one item by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(sel, timeout).until(
                EC.presence_of_element_located((By.XPATH, locator))
            )
            return element
        except TimeoutException:
            logger.info(' Find by xpath not found : %s', locator)
            logger.debug('%s', TimeoutException)
            return None

    def find_by_id(self, locator, timeout=None):
        ''' Get one item by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, timeout).until(
                EC.presence_of_element_located((By.ID, locator))
            )
            return element
        except TimeoutException:
            logger.info(' Find by ID not found : %s', locator)
            logger.debug('%s', TimeoutException)
            return None

    def find_all_by_css_from_element(self, sel, locator, timeout=None):
        ''' Get one item by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(sel, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, locator))
            )
            return element
        except TimeoutException:
            logger.info(' Find by css not found : %s', locator)
            logger.debug('%s', TimeoutException)
            return None

    def find_by_css_from_element(self, sel, locator, timeout=None):
        ''' Get one item by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(sel, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, locator))
            )
            return element
        except TimeoutException:
            logger.info(' Find by css not found : %s', locator)
            logger.debug('%s', TimeoutException)
            return None

    def find_all_by_xpath(self, locator, timeout=None):
        ''' Get all items by xpath'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, locator)))
            return element
        except TimeoutException:
            logger.info(' Find by xpath not found : %s', locator)
            logger.debug('%s', TimeoutException)
            return []

    def find_elements_by_xpath(self,locator):
        elements = self._driver.find_elements("xpath",locator)
        return elements

    def find_by_class(self, classname, timeout=None):
        ''' Get one item by class'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, classname)))
            return element
        except TimeoutException:
            logger.info(' Find by class not found : %s', classname)
            logger.debug('%s', TimeoutException)
            return None

    def find_all_by_class(self, classname, timeout=None):
        ''' Get all item by class'''
        if not timeout:
            timeout = self._timeout
        try:
            element = WebDriverWait(self._driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, classname)))
            return element
        except TimeoutException:
            logger.info(' Find by class not found : %s', classname)
            logger.debug('%s', TimeoutException)
            return []

    def select_dropdown_by_text(self, locator, text_value, timeout=None):
        tag = self.find_by_xpath(locator)
        if tag:
            select = Select(tag)
            try:
                select.select_by_visible_text(text_value)
            except NoSuchElementException:
                logger.info("Not found variant {}".format(text_value))

        else:
            logger.info('Not found dropdown at xpath {}'.format(locator))
            return False

    def select_dropdown_by_value(self, locator, value, timeout=None):
        tag = self.find_by_xpath(locator)
        if tag:
            select = Select(tag)
            try:
                select.select_by_value(value)
            except NoSuchElementException:
                logger.info("Not found variant {}".format(value))

        else:
            logger.info('Not found dropdown at xpath {}'.format(locator))

    def is_exist_by_xpath(self, locator, timeout=None):
        ''' Check if xpath is exists'''
        if not timeout:
            timeout = self._timeout
        try:
            WebDriverWait(self._driver, timeout).until(EC.presence_of_element_located((By.XPATH, locator)))
            return True
        except TimeoutException:
            return False
        return True

    def is_exist_by_css(self, locator, timeout=None):
        ''' Check if xpath is exists'''
        if not timeout:
            timeout = self._timeout
        try:
            WebDriverWait(self._driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, locator)))
            return True
        except TimeoutException:
            return False
        return True

    def wait_for_hide(self, locator, by='css', max_wait_time=20, timeout=0.1):
        ''' Check if xpath is exists'''
        counter = max_wait_time / timeout
        while counter > 0:
            try:
                WebDriverWait(self._driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, locator)))
                logger.info('Waiting for element to hide: {}'.format(locator))
            except TimeoutException:
                return True

            counter -= 1

    def restart(self):
        ''' Restart the browser'''
        logger.info("Restart browser")
        if self._driver:
            self._driver.close()
        time.sleep(1)
        self.start()

    def close_this_tab(self):
        ''' Exit the browser'''
        logger.info("Close current browser")
        if self._driver:
            self._driver.close()

    def exit(self):
        ''' Exit the browser'''
        logger.info("Exit browser")
        if self._driver:
            self._driver.quit()

    def try_get_url(self, url, retry=5):
        get_result = False
        while retry > 0:
            retry -= 1
            get_result = self.get_url(url)
            if get_result and 'This site can’t be reached' not in self.get_page_source():
                return True

            logger.info('Retry get url: {}'.format(url))
            time.sleep(2)
            self.restart()

        return False

    def refresh(self):
        self._driver.refresh()

    def get_url(self, url):
        if self._changeProxyTotal:
            self._changeProxyCounter += 1
            if self._changeProxyCounter > self._changeProxyTotal:
                self.restart()
                self._changeProxyCounter = 0
        ''' Get an url '''
        try:
            self._driver.get(url)
            if self.has_captcha():
                logger.info("Page not loaded or has a captcha. Restart browser")
                self.restart()
                self._restartBrowserCounter += 1
                if self._restartBrowserCounter > 5:
                    self._restartBrowserCounter = 0
                    # Skip this url
                    return False
                self.get_url(url)

            return True
        except:
            logger.info("Fail to get %s", url)
            print("Unexpected error:", sys.exc_info()[0])
            return False

    def has_captcha(self):
        time.sleep(1)
        pagesource = self.get_page_source()

        if 'Blocked IP Address' in pagesource \
                or 'recaptcha-token' in pagesource \
                or 'I am not a robot' in pagesource \
                or 'not a robot' in pagesource \
                or 'Enter the characters you see below' in pagesource \
                or 'One more step' in pagesource \
                or 'Sorry! Something went wrong on our end' in pagesource:
            logger.info("Has captcha")
            return True
        else:
            return False

    def executeJS(self, jsString, param=None):
        logger.info("Execute script {}".format(jsString))
        self._driver.execute_script(jsString, param)
        time.sleep(1)

    def scroll_bottom(self, wait_scroll=1, loading_xpath=None):
        logger.info("Scrolling down ... ")
        self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait_scroll)
        counter = 5
        while counter > 0:
            counter -= 1
            if not self.is_exist_by_xpath(loading_xpath, 1):
                break

    def scroll_down(self, number=10):
        for i in range(0, number):
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

    def scroll_top(self):
        self._driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

    # def scroll_top(self, width, height):
    #     self._driver.execute_script(f"window.scrollTo({width}, {height});")
    #     time.sleep(1)

    def scroll_by(self, width, height):
        self._driver.execute_script(f"window.window.scrollBy({width}, {height});")

        time.sleep(0.5)

    def scroll_infinity(self, loading_xpath=None, iretry=15, waiting_load=2):
        # scroll infinity
        # define initial page height for 'while' loop
        last_height = self._driver.execute_script("return document.body.scrollHeight")
        logger.info("Scrolling down ... ")
        retry = iretry
        page = 0
        while True:
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(waiting_load)

            new_height = self._driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                retry -= 1
                if retry < 0:
                    if loading_xpath:
                        # Wait for loading new data
                        if self.is_exist_by_xpath(loading_xpath, 5):
                            retry = iretry
                            continue

                    break
            else:
                last_height = new_height
                page += 1
                logger.info("Scroll down page: %d", page)
                retry = iretry

    def click_on_fly(self, element, x_offset=10, y_offset=10, moveTimeout=1):
        ''' Click coordiate'''
        try:
            hover = ActionChains(self._driver).move_to_element(element).move_by_offset(x_offset, y_offset).click()
            hover.perform()
        except:
            logger.info('Fail to click on an element')

    def move_slider(self, element, x_offset=10, y_offset=0, moveTimeout=1):
        ''' Click coordiate'''
        hover = ActionChains(self._driver).move_to_element(element).move_by_offset(x_offset, y_offset).click()
        hover.perform()

    def dismiss_alert(self):
        try:
            WebDriverWait(self._driver, 2).until(EC.alert_is_present())
            self._driver.switch_to_alert().accept()
            return True
        except TimeoutException:
            return False

    # def get_screenshot_by_xpath(self, xpath, result_path):
    #     element = self.find_by_xpath(xpath)
    #     if not element:
    #         logger.info("Not found element at xpath: %d", xpath)

    #     location = element.location
    #     size = element.size

    #     self._driver.save_screenshot("temp.png")

    #     x = location['x']
    #     y = location['y']
    #     width = location['x']+size['width']
    #     height = location['y']+size['height']

    #     im = Image.open('temp.png')
    #     im = im.crop((int(x), int(y), int(width), int(height)))
    #     im.save(result_path)
    #     # Delete temp image
    #     if os.path.isfile('temp.png'):
    #         os.remove('temp.png')

    #     return result_path
    def scroll_into_view(self, element):
        self._driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(1)

    def hover_element(self, element, moveTimeout=1):
        ''' Hover an element'''
        hover = ActionChains(self._driver).move_to_element(element)
        hover.perform()

    def click_element(self, element, moveTimeout=1):
        try:
            ''' Click an element'''
            actions = ActionChains(self._driver)
            actions.move_to_element(element)
            actions.perform()
            time.sleep(moveTimeout)
            actions.click(element)
            actions.perform()
            return True
        except Exception as ex:
            logger.info("Can't click element")
            return False

    def click_element_to_new_tab(self, element, moveTimeout=3):
        try:
            ''' Click an element'''
            actions = ActionChains(self._driver)
            actions.move_to_element(element)
            actions.perform()
            time.sleep(moveTimeout)

            if os.name == 'posix':
                actions.key_down(Keys.COMMAND, element).click(element).key_up(Keys.COMMAND, element)
            else:
                actions.key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL)
            actions.perform()
            return True
        except:
            logger.info("Can't click element")
            return False

    def send_keys(self, key):
        ''' Send key to brower'''
        actions = ActionChains(self._driver)
        actions.send_keys(key)
        actions.perform()

    def get_plugin(self, proxy_host, proxy_port, proxy_user, proxy_pass):
        logger.info('set proxy {}:{} with username {}'.format(proxy_host, proxy_port, proxy_user))

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (proxy_host, proxy_port, proxy_user, proxy_pass)
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        return pluginfile

    def start(self):
        ''' Start the browser'''
        logger.info("Start browser")

        chromeOptions = webdriver.ChromeOptions()

        # If have proxy path then config proxy
        if self._proxyFilePath:
            proxies = read_text_file_to_list(self._proxyFilePath)

            proxy_with_password = []
            # READ PROXY
            for proxy in proxies:
                if '@' in proxy:
                    part = proxy.split('@')
                    username, password = part[0].split(':')
                    host, port = part[1].split(':')
                    proxy_with_password.append({
                        'proxy_host': '{}'.format(host),
                        'proxy_port': port,
                        'proxy_user': username,
                        'proxy_pass': password,
                    })

            # if proxy with password
            if proxy_with_password:
                randomIp = random.choice(proxy_with_password)
                self._currentProxyIp = randomIp['proxy_host']
                chromeOptions.add_extension(self.get_plugin(**randomIp))
            else:
                proxyip = random.choice(proxies)
                logger.info("proxy ip: {}".format(proxyip))
                self._currentProxyIp = proxyip.split(':')[0]
                chromeOptions.add_argument('--proxy-server={}'.format(proxyip))

        if self._isHeadLess:
            logger.info('Start browser in headless mode')
            chromeOptions.add_argument("--headless")
            chromeOptions.add_argument("--disable-gpu")

        if ISLOCAL:
            chromeOptions.add_extension("chropath.zip")
            chromeOptions.add_extension("edit_this_cookie.zip")

        # chromeOptions.add_argument('--disable-extensions')
        # chromeOptions.add_argument('--profile-directory=Default'
        # chromeOptions.add_argument("--incognito")
        # chromeOptions.add_argument("--disable-plugins-discovery");
        # chromeOptions.add_argument("--start-maximized")
        # chromeOptions.add_argument("--no-experiments")
        chromeOptions.add_argument("--disable-translate")
        chromeOptions.add_argument("disable-infobars")
        # chromeOptions.add_argument("--disable-plugins")
        # chromeOptions.add_argument("--disable-extensions");
        chromeOptions.add_argument("--no-sandbox")
        chromeOptions.add_argument("--disable-dev-shm-usage")
        chromeOptions.add_argument("--no-default-browser-check")
        # chromeOptions.add_argument("--clear-token-service")
        chromeOptions.add_argument("--disable-default-apps")
        if self._userAgentFilePath:
            # READ USER AGENTS
            ua_list = read_text_file_to_list(self._userAgentFilePath)
            user_agent = random.choice(ua_list)
        else:
            user_agent = random.choice(USER_AGENT_LIST)

        logger.info('User-agent: {}'.format(user_agent))
        chromeOptions.add_argument('user-agent={}'.format(user_agent))

        chromeOptions.add_argument("test-type")
        chromeOptions.add_argument('--log-level=3')

        if self._userDataDir:
            chromeOptions.add_argument("user-data-dir=" + self._userDataDir)

        if (self._isMaximum):
            chromeOptions.add_argument("start-maximized")

        prefs = {"profile.default_content_setting_values.notifications": 2}
        prefs = {"credentials_enable_service", False}
        prefs = {"profile.password_manager_enabled": False}

        if self._isDisableImage:
            prefs["profile.managed_default_content_settings.images"] = 2

        if self._isDisableJavascript:
            prefs["profile.managed_default_content_settings.javascript"] = 2

        prefs['plugins'] = {'plugins_disabled': ['Chrome PDF Viewer']}

        # prefs['download'] = {'default_directory': self._downloadPath, "directory_upgrade": True}
        prefs["download.default_directory"] = self._downloadPath
        prefs["download.prompt_for_download"] = False
        prefs["download.directory_upgrade"] = True
        prefs["safebrowsing_for_trusted_sources_enabled"] = False
        prefs["safebrowsing.enabled"] = False

        chromeOptions.add_experimental_option("prefs", prefs)
        # chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"])
        chromeOptions.add_experimental_option('useAutomationExtension', False)
        # chromeOptions.add_experimental_option("excludeSwitches", ["ignore-certificate-errors", "safebrowsing-disable-download-protection", "safebrowsing-disable-auto-update", "disable-client-side-phishing-detection"])

        chromedriver = ''
        if os.name == 'posix':
            if self._currentPath:
                chromedriver = os.path.join(self._currentPath, "chromedriver")

            if not os.path.isfile(chromedriver):
                chromedriver = 'chromedriver'
        else:
            if self._currentPath:
                chromedriver = os.path.join(self._currentPath, "chromedriver.exe")

            if not os.path.isfile(chromedriver):
                chromedriver = 'chromedriver.exe'

        if self._isMobile:
            if self._mobileUserAgentFilePath:
                mobile_agents = read_text_file_to_list(self._mobileUserAgentFilePath)
                random_agent = random.choice(mobile_agents)
            else:
                random_agent = random.choice(MOBILE_USER_AGENT_LIST)

            logger.info('Mobile User-agent: {}'.format(random_agent))
            mobile_emulation = {
                "deviceMetrics":
                    {
                        "width": 414,
                        "height": 816,
                        "pixelRatio": 3.0
                    },
                "userAgent": random_agent
            }

            chromeOptions.add_experimental_option("mobileEmulation", mobile_emulation)

        # self._driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions,desired_capabilities=desired_cap)
        self._driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)

        # self._driver.delete_all_cookies()

        if self._isMobile:
            self._driver.set_window_size(414, 816)

        # self._driver.set_page_load_timeout(60)

        # window_size = self._driver.execute_script("""
        # return [window.outerWidth - window.innerWidth + arguments[0],
        #   window.outerHeight - window.innerHeight + arguments[1]];
        # """, 1024, 600)
        # self._driver.set_window_size(*window_size)

        # driver.set_window_position(-10000,0)
        # self._driver.switch_to_window(self._driver.current_window_handle)

    def try_click(self, element, num=10):
        ''' Try to click an element'''
        is_clicked = False
        step = 0
        while not is_clicked and step < num:
            try:
                is_clicked = self.click_element(element, 5)
                is_clicked = True
            except:
                time.sleep(1)
                logger.info("try click %s", element)
                is_clicked = False
            step += 1

        return is_clicked

    def try_click_by_xpath(self, locator, num=10):
        ''' Try to click an element'''
        is_clicked = False
        retry = num
        while not is_clicked and num > 0:
            num -= 1
            element = self.find_by_xpath(locator)
            if element:
                is_clicked = self.click_element(element, moveTimeout=retry - num)
                if is_clicked:
                    return True
            # Else try click again
            time.sleep(1)
            logger.info("try click {} x {}".format(num, locator))

        return is_clicked

    def try_click_by_css(self, locator, num=10):
        ''' Try to click an element'''
        is_clicked = False
        retry = num
        while not is_clicked and num > 0:
            num -= 1
            element = self.find_by_class(locator)
            if element:
                is_clicked = self.click_element(element, moveTimeout=retry - num)
                if is_clicked:
                    return True
            # Else try click again
            time.sleep(1)
            logger.info("try click {} x {}".format(num, locator))

        return is_clicked


# ======================================= END WEB BROWSER ================================================


MOBILE_USER_AGENT_LIST = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1',
    'Outlook-iOS/709.2189947.prod.iphone (3.24.0)',
    'Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko; googleweblight) Chrome/38.0.1025.166 Mobile Safari/535.19',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57',
    'MauiBot (crawler.feedback+wc@gmail.com)',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.0 Mobile/14G60 Safari/602.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_2_1 like Mac OS X) AppleWebKit/602.4.6 (KHTML, like Gecko) Version/10.0 Mobile/14D27 Safari/602.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0 Mobile/15D100 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.0 Mobile/14F89 Safari/602.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A404',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15G77',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13F69 Safari/601.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0 Mobile/15C153 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_2 like Mac OS X) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0 Mobile/14C92 Safari/602.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13D15 Safari/601.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_2 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/14A456 Safari/602.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13G36 Safari/601.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_5 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0 Mobile/15D60 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_1_1 like Mac OS X) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0 Mobile/14B100 Safari/602.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B411 Safari/600.1.4 (compatible; YandexMobileBot/3.0; +http://yandex.com/bots)',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_2 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0 Mobile/15C202 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 6.0.1; SM-G532G Build/MMB29T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.83 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13E238 Safari/601.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_2 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0 Mobile/15B202 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13C75 Safari/601.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0_3 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A432 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 7.0; SM-G610M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13E188a Safari/601.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4',
    'Mozilla/5.0 (Linux; Android 7.0; SM-G570M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16B92',
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_1_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B440 Safari/600.1.4',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16C101',
    'Mozilla/5.0 (Linux; U; Android 4.3; de-de; GT-I9300 Build/JSS15J) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'Outlook-iOS/709.2144270.prod.iphone (3.23.0)',
    'Mozilla/5.0 (Linux; Android 6.0.1; SM-G532M Build/MMB29T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36',
    'Mozilla/5.0 (Mobile; Windows Phone 8.1; Android 4.0; ARM; Trident/7.0; Touch; rv:11.0; IEMobile/11.0; NOKIA; Lumia 635) like iPhone OS 7_0_3 Mac OS X AppleWebKit/537 (KHTML, like Gecko) Mobile Safari/537',
    'Mozilla/5.0 (Linux; Android 6.0.1; SM-J700M Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; U; Android 2.2.1; en-us; Nexus One Build/FRG83) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
    'Mozilla/5.0 (Linux; Android 7.0; SM-G570M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12D508 Safari/600.1.4',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_4 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13G35 Safari/601.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13G34 Safari/601.1',
    'Mozilla/5.0 (Linux; Android 7.0; SAMSUNG SM-G610M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/7.4 Chrome/59.0.3071.125 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; U; Android 4.1.2; de-de; GT-I8190 Build/JZO54K) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'Mozilla/5.0 (Linux; Android 4.4.2; de-de; SAMSUNG GT-I9195 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/1.5 Chrome/28.0.1500.94 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0.1; SM-J500M Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.0; SAMSUNG SM-G900F Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/2.1 Chrome/34.0.1847.76 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 4.4.2; SM-G7102 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/70.0.3538.75 Mobile/15E148 Safari/605.1',
    'Mozilla/5.0 (Linux; Android 7.0; SM-G610F Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.111 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; SM-J730GM Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.111 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 6.0.1; SM-G532M Build/MMB29T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; SAMSUNG SM-N920C Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/6.2 Chrome/56.0.2924.87 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; SM-J710F Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0.1; SM-J700M Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.0.0; SAMSUNG SM-G950F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/7.4 Chrome/59.0.3071.125 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0.1; SM-J500M Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.83 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; SAMSUNG SM-G570M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/7.4 Chrome/59.0.3071.125 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60',
    'Mozilla/5.0 (Linux; Android 7.0; SM-G610M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.80 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0.1; SM-J500M Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.111 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D201 Safari/9537.53',
    'Mozilla/5.0 (Linux; Android 6.0.1; SM-J500M Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; U; Android 4.3; en-us; SM-N900T Build/JSS15J) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_0_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13A452 Safari/601.1',
    'Mozilla/5.0 (Linux; Android 7.0; SM-G610M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_1 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0 Mobile/15B150 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/14A403 Safari/602.1',
    'Mozilla/5.0 (Linux; Android 7.0; SM-G610M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.91 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.0.1; SAMSUNG GT-I9505 Build/LRX22C) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/2.1 Chrome/34.0.1847.76 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0 Mobile/15C114 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 7.0; SM-G570M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.91 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B411 Safari/600.1.4',
    'Mozilla/5.0 (Linux; Android 6.0.1; SAMSUNG SM-G532M Build/MMB29T) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/7.4 Chrome/59.0.3071.125 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; SM-G570M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.80 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.53',
]

USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
    'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
    'Mozilla/5.0 (X11; U; Linux Core i7-4980HQ; de; rv:32.0; compatible; JobboerseBot; http://www.jobboerse.com/bot.htm) Gecko/20100101 Firefox/38.0',
    'Mozilla/5.0 (Windows NT 5.1; rv:36.0) Gecko/20100101 Firefox/36.0',
    'Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:17.0) Gecko/20100101 Firefox/17.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Windows NT 6.0; rv:34.0) Gecko/20100101 Firefox/34.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
    'Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.5) Gecko/20041107 Firefox/1.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/20.6.14',
    'Mozilla/5.0 (Windows NT 5.1; rv:30.0) Gecko/20100101 Firefox/30.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0',
    'Mozilla/5.0 (X11; U; Linux Core i7-4980HQ; de; rv:32.0; compatible; JobboerseBot; https://www.jobboerse.com/bot.htm) Gecko/20100101 Firefox/38.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.10) Gecko/20050716 Firefox/1.0.6',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
    'Mozilla/5.0 (Windows NT 5.1; rv:6.0.2) Gecko/20100101 Firefox/6.0.2',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:63.0) Gecko/20100101 Firefox/63.0',
    'Mozilla/5.0 (Windows NT 5.1; rv:29.0) Gecko/20100101 Firefox/29.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.0.7) Gecko/20060909 Firefox/1.5.0.7',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; it-IT) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.34 (KHTML, like Gecko) Qt/4.8.3 Safari/534.34',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Version/3.1.2 Safari/525.21',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.51.22 (KHTML, like Gecko) Version/5.1.1 Safari/534.51.22',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; fr-FR) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.27+ (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.2 Safari/602.3.12',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0.1 Safari/604.3.5',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0.1 Safari/604.3.5',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10',
    'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/125.2 (KHTML, like Gecko) Safari/125.8',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; en-us) AppleWebKit/533.17.8 (KHTML, like Gecko) Version/5.0.1 Safari/533.17.8',
    'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-us) AppleWebKit/125.5 (KHTML, like Gecko) Safari/125.9',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/7.1.7 Safari/537.85.16',
    'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-us) AppleWebKit/85.8.5 (KHTML, like Gecko) Safari/85.8.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12',
    'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-us) AppleWebKit/85.8.2 (KHTML, like Gecko) Safari/85.8',
]