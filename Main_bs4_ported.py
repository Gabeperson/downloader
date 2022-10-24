from bs4 import BeautifulSoup
import requests
import re
import os
import threading
import time

# set max threads
max_threads = 4
# set url (TODO: Get user input)
url = "https://comic.naver.com/webtoon/detail?titleId=183559&no=1&weekday=sun"


# strip url of weekday and number using regex :)
url = re.sub(r"&weekday=\w{1,10}", "", url)  # &weekday= + any word from 1-10
chapter_number = int(re.search(r"\d{1,4}(?![a-zA-Z0-9&])", url).group())  # get number from chapter number
url = re.sub(r"\d{1,4}(?![a-zA-Z0-9&])", "", url)  # 1-4 digits + negative lookahead for any character, number, or & sign

chapters_list = [url + str(numb + 1) for numb in range(chapter_number)]  # create list of all chapters til max chap numb
print(f"Chapters List: {chapters_list}")

# open selenium (user must have firefox installed)
service = Service("dependencies\\geckodriver.exe", log_path="nul")  # set webdriver binary location, disable log files
options = Options()  # create options
options.headless = False  # change headless mode
driver = selenium.webdriver.Firefox(service=service,options=options)
driver.get(chapters_list[0])

# get series name
series_title = driver.find_element(By.CLASS_NAME, "title").text

# make dir
files_dir = os.path.join(os.getcwd(), "files", series_title)
if not os.path.exists(files_dir): os.mkdir(files_dir)

for chapter in chapters_list:
	images_list = []
	counter = 0
	while True:
		try:
			element = driver.find_element(By.ID, f"content_image_{counter}")
			images_list.append([element.get_attribute("src"), counter])
			counter += 1
		except NoSuchElementException:
			break



driver.quit()
