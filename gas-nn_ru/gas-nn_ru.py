import os
import time
from selenium import webdriver


def send_readings(auth_settings, readings, test_mode=False):
    mainpage_url = get_mainpage_url(test_mode)
    wd = get_webdriver(test_mode)
    wd.get(mainpage_url)
    log_in_mainpage(wd, auth_settings)


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
    chromedriver_dir = current_dir.replace('\\gas-nn_ru', '')
    path = r"{}\chromedriver.exe".format(chromedriver_dir)
    return webdriver.Chrome(options=options, executable_path=path)


def log_in_mainpage(driver: webdriver, auth_settings):
    # driver = webdriver.Chrome()
    input_fam = driver.find_element_by_xpath("//td/input[@type='text'][@name='fam']")
    input_fam.clear()
    input_fam.send_keys(auth_settings.get('family_name'))

    input_account = driver.find_element_by_xpath("//td/input[@type='text'][@name='lschet'][@id='lschet']")
    input_account.clear()
    input_account.send_keys(auth_settings.get('account'))

    select_city= driver.find_element_by_xpath("//td/select[@name='c_id']")
    select_city.send_keys(auth_settings.get('city_id'))

    buton_submit= driver.find_element_by_xpath("//td/input[@type='submit'][@name='go']")
    buton_submit.click()


def get_auth_settings(user_id=None):
    auth_settings = {
        'family_name': 'Степанов',
        'account': '051000507028',
        'city_id': 100
    }
    return auth_settings


if __name__ == '__main__':

    send_readings(get_auth_settings(), None)
    time.sleep(10)