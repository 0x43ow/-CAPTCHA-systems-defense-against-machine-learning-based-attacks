from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import io
from PIL import Image
from poisoned_model_run import predict
"""
attempts to solve the captchas on the defended server on  http://127.0.0.1:50000
note that the server needs to be running in order for the bot to function
"""




def download_image(url):
    """
    search a page for a specific element and download it on disc
    """
    img = browser.find_element(By.ID, 'captcha')
    img = img.screenshot_as_png
    img_file = io.BytesIO(img)
    #Stores the file in memory and convert to image file using Pillow
    im = Image.open(img_file)

    with open('Captcha.png', 'wb') as file:
      im.save(file, 'png')


    

def solve_Captcha():
    """
    calls download_image to download the captcha image, calls predict to get the model's solution to the captcha and writes it on the page's input field 
    """
    searchBar = browser.find_element(By.ID, "text bar")
    cap = browser.find_element(By.ID, 'captcha')
    src = cap.get_attribute('src')
    download_image(src)
    answer = predict('Captcha.png')
    searchBar.send_keys(answer)
    time.sleep(0.1)
    searchBar.send_keys(Keys.ENTER)


#running on chrome
browser = webdriver.Chrome('chromedriver.exe')


while True:
  browser.get('http://127.0.0.1:50000')
  solve_Captcha()
  time.sleep(1)

