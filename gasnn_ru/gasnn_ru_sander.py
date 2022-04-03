import os
import time
from selenium import webdriver

login_page_url = 'https://www.gas-nn.ru/login'
meter_reading_page_url = 'https://www.gas-nn.ru/lk/indication'


def send_readings(auth_settings, readings, test_mode=False):
    wd = get_webdriver(test_mode)
    wd.get(login_page_url)
    log_in(wd, auth_settings)
    wd.close()


def get_webdriver(test_mode=False):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    if not test_mode:
        options.add_argument('--headless')
    current_dir = os.getcwd()
    chromedriver_dir = current_dir.replace('\\gas-nn_ru', '')
    path = r"{}\chromedriver.exe".format(chromedriver_dir)
    return webdriver.Chrome(options=options, executable_path=path)


def log_in(driver: webdriver, auth_settings):

    xpath = "//div/input[@id='formControlEmail'][@type='text'][@autocomplete='email']"
    input_login = driver.find_element_by_xpath(xpath)
    input_login.clear()
    input_login.send_keys(auth_settings.get('email'))

    xpath = "//div/input[@name='ischet'][@type='password'][@autocomplete='password']"
    input_pass = driver.find_element_by_xpath(xpath)
    input_pass.clear()
    input_pass.send_keys(auth_settings.get('pass'))

    button_submit = driver.find_element_by_class_name('btn-primary')
    button_submit.click()


def get_auth_settings(user_id=None):
    auth_settings = {
        'email': '',
        'pass': '',
    }
    return auth_settings


if __name__ == '__main__':

    send_readings(get_auth_settings(), None, False)
    time.sleep(20)
