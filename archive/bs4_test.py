from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent

ua = UserAgent(path="UserAgent_data.json")

soup = BeautifulSoup(requests.get("https://comic.naver.com/webtoon/detail?titleId=183559&no=1&weekday=sun").text, "html.parser")

image_list = []
counter = 0
while True:
	element = soup.find(id=f"content_image_{counter}")
	if not element:
		break
	image_list.append(element["src"])

	counter += 1
print(image_list)

image = image_list[0]
headers = {
	"User-Agent": ua.chrome
}
r = requests.get(image, headers=headers)
with open("image.jpg", "wb") as f:
	if r.status_code == 200:
		for chunk in r.iter_content(256):
			f.write(chunk)
	else:
		print(r.status_code)