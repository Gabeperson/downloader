from bs4 import BeautifulSoup
import requests

soup = BeautifulSoup(requests.get("https://comic.naver.com/webtoon/detail?titleId=183559&no=1&weekday=sun").text, "html.parser")

links_list = []
counter = 0
while True:
	element = soup.find(id="content_image_1")
	if element:
		print(element["src"])
	counter += 1

