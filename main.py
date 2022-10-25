from bs4 import BeautifulSoup
import requests
import re
import os
import queue
import threading
import time

with open("config.txt", "r") as f:
	config = f.read().strip(" \n").split("\n")


threads = int(re.sub("threads=", "", config[0]))
config_url = re.sub("webtoon_end_link=", "", config[1])
width_percentage = re.sub("image_width_percent", "", config[2])



# set max threads
max_threads = threads
# set url (TODO: Get user input)
url = config_url


# strip url of weekday and number using regex :)
url = re.sub(r"&weekday=\w{1,10}", "", url)  # &weekday= + any word from 1-10
chapter_number = int(re.search(r"\d{1,4}(?![a-zA-Z0-9&])", url).group())  # get number from chapter number
url = re.sub(r"\d{1,4}(?![a-zA-Z0-9&])", "", url)  # 1-4 digits + negative lookahead for any character, number, or & sign

chapters_list = [(url + str(numb + 1), str(numb + 1)) for numb in range(chapter_number)]  # create list of all chapters til max chap numb

# load
soup = BeautifulSoup(requests.get(chapters_list[0][0]).text, "html.parser")

# get series name
series_title = soup.find(class_="title").decode_contents()

# make dirs
if not os.path.exists("files"):
	os.mkdir("files")
files_dir = os.path.join(os.getcwd(), "files", series_title)
if not os.path.exists(files_dir):
	os.mkdir(files_dir)
images_dir = os.path.join(files_dir, "images")
if not os.path.exists(images_dir):
	os.mkdir(images_dir)

# make main queue for threads
image_queue = queue.Queue()

def thread_function():
	while True:
		try:
			image = image_queue.get(timeout=10)  # [Image url, chapter dir, image number]
		except queue.Empty:
			break
		r = requests.get(image[0], stream=True, headers={"User-Agent": 'Mozilla/5.0'})
		with open(os.path.join(image[1], f"{image[2]}.jpg"), "wb") as f:
			if r.status_code == 200:
				for chunk in r.iter_content(256):
					f.write(chunk)
		print("Finished chapter " + image[1].split('images\\')[1] + f", image {image[2]}")

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

# wait for all the threads to finish
while sum([bool(thread.is_alive()) for thread in threads]) != 0:
	time.sleep(5)


# create html that includes all the image files
directories = [path for path in os.listdir(images_dir) if os.path.isdir(os.path.join(images_dir, path))]



def get_files(lookup_path):
	return [path for path in os.listdir(lookup_path) if os.path.isfile(os.path.join(lookup_path, path))]

for directory in directories:
	with open(os.path.join(files_dir, f"c{directory}.html"), "wb") as f:
		html_string = f"<title>{series_title} c{directory}</title><center><h1>{series_title} c{directory}</h1>"
		for image in get_files(os.path.join(images_dir, directory)):
			html_string += f"<img style='width: {width_percentage}vw; display: block;' src={os.path.join('images', directory, image)}>"
		html_string += "</center>"
		f.write(html_string.encode())
