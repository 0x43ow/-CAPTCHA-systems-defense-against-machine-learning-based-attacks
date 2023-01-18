from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import time
import io
from PIL import Image
from JUST_model_run import predict

total_attempts = 0
successful_accesses = 0
browser = webdriver.Chrome('chromedriver.exe')


"""
these are testing functions to evaluate the default and the 3 image polled browser bots
they will access JUST's course schedule's page on https://services.just.edu.jo/courseschedule/ using selenium webdriver
log messages will be found on log_default.txt and log_3IP.txt
"""

def download_image_default(cap):
    """
    search a page for a specific element and download it on disk
    """
    img = cap.screenshot_as_png
    img_file = io.BytesIO(img)
    im = Image.open(img_file)
    with open('Captcha.png', 'wb') as file:
      im.save(file, 'png')

def solve_Captcha_default(): 
    """
    calls download_image to download the captcha image, calls predict to get the model's solution to the captcha and writes it on the page's input field 
    """
    global total_attempts
    total_attempts += 1


    searchBar = browser.find_element(By.ID, "ctl00_contentPH_txtCaptchaText")
    cap = browser.find_element(By.ID, 'ctl00_contentPH_captcha_imgCaptcha')
    download_image_default(cap)
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


def run_default(test_samples=100):
  global total_attempts
  global successful_accesses
  total_attempts = 0
  successful_accesses = 0
  #opening the course schedule's page through chrome
  run_time = time.time()
  
  for _ in range(test_samples):
    solve_Captcha_default()
    #time.sleep(0.1)
  total_time = time.time() - run_time


  f = open('log_default.txt','a')
  f.write(
  f"""
  accuracy = {round(successful_accesses / total_attempts * 100,2)}%
  attempts per second = {round(total_attempts /  total_time,2)}
  accesses per second = {round(successful_accesses / total_time,2)}
  """)
  f.close()


def download_image_3IP(cap,index):
    """
    search a page for a specific element and download it on disk
    """
    img = cap.screenshot_as_png
    img_file = io.BytesIO(img)
    im = Image.open(img_file)
    with open(f'Captcha{index}.png', 'wb') as file:
      im.save(file, 'png')

def most_frequent(List):
    return max(set(List), key = List.count)



def choose_best(answers):
    #if at least two predictions are identical, return one of them
    if answers[0] == answers[1] or answers[0] == answers[2]:
        return answers[0]
    if answers[1] == answers[2]:
        return answers[1]
    chars = ['0','0','0','0']
    sol = ""
    for j in range(4):
        """
        find the most repeated character in each position
        e.g 1111,1234,2234 returns 1234
        """
        chars[j] = list(answers[i][j] for i in range(3))
        sol+=(most_frequent(chars[j]))    
    return sol



def solve_Captcha_3IP(): 
    """
    calls download_image to download the captcha image, calls predict to get the model's solution to the captcha and writes it on the page's input field 
    """
    global total_attempts
    total_attempts += 1
    answers = []
    for i in range(3):
        searchBar = browser.find_element(By.ID, "ctl00_contentPH_txtCaptchaText")
        cap = browser.find_element(By.ID, 'ctl00_contentPH_captcha_imgCaptcha')
        download_image_3IP(cap,i)
        answers.append(predict(f"Captcha{i}.png"))
        if i != 2 :
            searchBar.send_keys(Keys.ENTER)
    answer = choose_best(answers)
    searchBar.send_keys(answer)
    searchBar.send_keys(Keys.ENTER)
    searchBar = browser.find_element(By.ID, "ctl00_contentPH_txtCaptchaText")
    searchBar.clear()
    #finding the prediction's result, if it was correct increment successful_accesses
    try:
      element = browser.find_element(By.ID, 'ctl00_contentPH_lblResult')
    except NoSuchElementException:
      global successful_accesses
      successful_accesses+=1

def run_3IP(test_samples=100):
  global total_attempts
  global successful_accesses
  total_attempts = 0
  successful_accesses = 0
  #opening the course schedule's page through chrome
  run_time = time.time()
  
  for _ in range(test_samples):
    solve_Captcha_3IP()
  total_time = time.time() - run_time


  f = open('log_3IP.txt','a')
  f.write(
  f"""
  accuracy = {round(successful_accesses / total_attempts * 100,2)}%
  attempts per second = {round(total_attempts /  total_time,2)}
  accesses per second = {round(successful_accesses / total_time,2)}
  """)
  f.close()




def main():
  browser.get('https://services.just.edu.jo/courseschedule/')
  selBar = browser.find_element(By.ID, "ctl00_contentPH_ddlFaculty")
  select = Select(selBar)
  select.select_by_index(9)
  selBar2 = browser.find_element(By.ID, "ctl00_contentPH_ddlDept")
  select2 = Select(selBar2)
  select2.select_by_index(4)
  """
  testing functions, call main()
  then call 
  run_3IP(sample size)
  or
  run_default(sample size)
  """
  
