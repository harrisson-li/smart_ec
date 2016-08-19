import sys
import os

test_env = sys.argv[1]
student_name = sys.argv[2]
student_pass = 1
etown_url = 'http://{}.englishtown.com/partner/englishcenters'.format(test_env)

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

d = webdriver.Chrome()
d.get(etown_url)
d.maximize_window()
wait = WebDriverWait(d, 10)

user_name = d.find_element_by_id('username')
user_name.clear()
user_name.send_keys(student_name)
user_pass = d.find_element_by_id('password')
user_pass.clear()
user_pass.send_keys(student_pass)

sign_in = d.find_element_by_class_name('etc-login-btn')
sign_in.click()


start_learning = wait.until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[1]/div/button'))
)
start_learning.click()

dismiss_reminder = wait.until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/a'))
)
dismiss_reminder.click()

# kill chromedriver.exe to avoid memory leak
os.system('taskkill /f /im chromedriver.exe')
