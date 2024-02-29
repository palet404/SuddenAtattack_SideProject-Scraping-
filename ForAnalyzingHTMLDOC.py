import requests as re
from bs4 import BeautifulSoup

url = 'https://www.inflearn.com/community/studies?page=1&order=recent'
response = re.get(url)
soup = BeautifulSoup(response.text,"html.parser")

GetEle = soup.find_all(class_ = "question-container")
print(GetEle)