from bs4 import BeautifulSoup
import requests
import re
import os
import queue
import threading
import time
from fake_useragent import UserAgent



ua = UserAgent(path="UserAgent_data.json")

# set max threads
max_threads = 4
# set url (TODO: Get user input)
url = "https://comic.naver.com/webtoon/detail?titleId=183559&no=5&weekday=sun"


# strip url of weekday and number using regex :)
url = re.sub(r"&weekday=\w{1,10}", "", url)  # &weekday= + any word from 1-10
chapter_number = int(re.search(r"\d{1,4}(?![a-zA-Z0-9&])", url).group())  # get number from chapter number
url = re.sub(r"\d{1,4}(?![a-zA-Z0-9&])", "", url)  # 1-4 digits + negative lookahead for any character, number, or & sign

chapters_list = [(url + str(numb + 1), str(numb + 1)) for numb in range(chapter_number)]  # create list of all chapters til max chap numb
print(f"Chapters List: {chapters_list}")

# load
soup = BeautifulSoup(requests.get(chapters_list[0][0]).text, "html.parser")

# get series name
series_title = soup.find(class_="title").decode_contents()
print(series_title)

# make dirs
files_dir = os.path.join(os.getcwd(), "files", series_title)
if not os.path.exists(files_dir):
	os.mkdir(files_dir)
images_dir = os.path.join(files_dir, "images")
if not os.path.exists(images_dir):
	os.mkdir(images_dir)

# make main queue for threads
image_queue = queue.Queue()
headers = {
	"User-Agent": ua.chrome
}

def thread_function():
	while True:
		try:
			image = image_queue.get(timeout=10)  # [Image url, chapter dir, image number]
		except queue.Empty:
			break
		r = requests.get(image[0], stream=True, headers=headers)
		with open(os.path.join(image[1], f"{image[2]}.jpg"), "wb") as f:
			if r.status_code == 200:
				for chunk in r.iter_content(256):
					f.write(chunk)

threads = [threading.Thread(target=thread_function, daemon=True) for _ in range(max_threads)]
for thread in threads:
	thread.start()

for chapter in chapters_list:  # [Chapter url, chapter #]
	chapter_dir = os.path.join(images_dir, chapter[1])  # get the directory where the chapter is going to be
	if not os.path.exists(chapter_dir): # make the chapter directory if it doesn't exist to avoid errors
		os.mkdir(chapter_dir)
	soup = BeautifulSoup(requests.get(chapter[0]).text, "html.parser")  # parse the chapter html
	counter = 0
	while True:
		element = soup.find(id=f"content_image_{counter}")  # find the image panels
		if not element:  # once there are no more image panels to get, stop.
			break
		image_queue.put([element["src"], chapter_dir, counter])  # [0] is image url,
		counter += 1

if sum([bool(thread.is_alive()) for thread in threads]) != 0:
	time.sleep(5)


# create html that includes all the image files
directories = [path for path in os.listdir(images_dir) if os.path.isdir(os.path.join(images_dir, path))]
print(os.listdir(images_dir))
print(directories)


def get_files(lookup_path):
	return [path for path in os.listdir(lookup_path) if os.path.isfile(os.path.join(lookup_path, path))]

for directory in directories:
	with open(os.path.join(files_dir, f"c{directory}.html"), "wb") as f:
		html_string = f"<title>{series_title} c{directory}</title><center><h1>{series_title} c{directory}</h1>"
		for image in get_files(os.path.join(images_dir, directory)):
			html_string += f"<img style='width: 60vw;' src={os.path.join('images', directory, image)}>"
		html_string += "</center>"
		f.write(html_string.encode())
