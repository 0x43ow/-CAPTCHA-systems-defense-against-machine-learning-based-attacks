from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import signal
import time
import io
from PIL import Image
from JUST_model_run import predict

"""
uses selenium to automate captcha solving on https://services.just.edu.jo/courseschedule/
"""

#to log accuracy
total_attempts = 0
successful_accesses = 0

def handler(signum, frame):
  #handle INT signals and logs the run's results 
  f = open('UNI_LOG.txt','w')
  total_time = time.time() - run_time
  f.write(f"""
  accuracy = {round(successful_accesses / total_attempts * 100,2)}%
  attempts per second = {round(total_attempts /  total_time,2)}
  accesses per second = {round(successful_accesses / total_time,2)}
  """)
  f.close()
  exit(1)



def download_image(cap):
    """
    search a page for a specific element and download it on disk
    """
    img = cap.screenshot_as_png
    img_file = io.BytesIO(img)
    im = Image.open(img_file)
    with open('Captcha.png', 'wb') as file:
      im.save(file, 'png')


    

def solve_Captcha(): 
    """
    calls download_image to download the captcha image, calls predict to get the model's solution to the captcha and writes it on the page's input field 
    """
    searchBar = browser.find_element(By.ID, "ctl00_contentPH_txtCaptchaText")
    cap = browser.find_element(By.ID, 'ctl00_contentPH_captcha_imgCaptcha')
    download_image(cap)
    answer = predict("Captcha.png")
    searchBar.clear()
    searchBar.send_keys(answer)
    searchBar.send_keys(Keys.ENTER)
    #finding the prediction's result, if it was correct increment successful_accesses
    try:
      element = browser.find_element(By.ID, 'ctl00_contentPH_lblResult')
    except NoSuchElementException:
      global successful_accesses
      successful_accesses+=1



signal.signal(signal.SIGINT, handler)


#opening the course schedule's page through chrome
browser = webdriver.Chrome('chromedriver.exe')
browser.get('https://services.just.edu.jo/courseschedule/')
selBar = browser.find_element(By.ID, "ctl00_contentPH_ddlFaculty")
select = Select(selBar)
select.select_by_index(9)
selBar2 = browser.find_element(By.ID, "ctl00_contentPH_ddlDept")
select2 = Select(selBar2)
select2.select_by_index(4)

run_time = time.time()
while True:
  solve_Captcha()
  total_attempts += 1
