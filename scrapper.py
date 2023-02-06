import requests
from bs4 import BeautifulSoup

nickname = 'rainruma'
url = "https://mydramalist.com/dramalist/%s/completed" % (nickname)

page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="content_2")

print(results.prettify())