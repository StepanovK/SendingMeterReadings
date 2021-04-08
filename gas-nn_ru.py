import os
import time
from selenium import webdriver


def send_reading(auth_settings, readings, test_mode=False):
    mainpage_url = get_mainpage_url(test_mode)
    wd = get_webdriver(test_mode)
    driver = wd.get(mainpage_url)
    log_in_mainpage(driver, auth_settings)


def get_mainpage_url(test_mode=False):
    if test_mode:
        current_dir = os.getcwd()
        current_dir = current_dir.replace('\\', '/')
        url = 'file://' + current_dir + '/TestPages/gas-nn_ru.html'
    else:
        url = 'https://www.gas-nn.ru/form.php'
    return url


def get_webdriver(test_mode=False):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    # if not test_mode:
    #     options.add_argument('--headless')
    current_dir = os.getcwd()
    path = r"{}\chromedriver.exe".format(current_dir)
    return webdriver.Chrome(options=options, executable_path=path)


def log_in_mainpage(driver, auth_settings):
    input_fam = driver.find_element_by_xpath("//td/input[@type='text'][@name='fam']")
    print("Окно ввода фамилии: {}".format(input_fam))

    input_account = driver.find_element_by_xpath("//td/input[@type='text'][@name='lschet'][@id='lschet']")
    print("Окно ввода счета: {}".format(input_account))

    select_fam = driver.find_element_by_xpath("//td/select[@name='c_id']")
    print("Окно ввода города: {}".format(select_fam))

