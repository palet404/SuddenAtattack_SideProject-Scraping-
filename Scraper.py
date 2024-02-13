import requests
from bs4 import BeautifulSoup
import markdown
import pandas as pd

url = "https://www.inflearn.com/community/studies?page=1&order=recent"
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, 'html.parser')

questions = soup.find_all('li', class_='question-container')

data = []
for question in questions:
    title = question.find('h3', class_='title__text').get_text(strip=True)
    contents = question.find('p', class_='question__body').get_text(strip=True)
    
    # Convert HTML to Markdown
    title_markdown = markdown.markdown(title)
    contents_markdown = markdown.markdown(contents)
    
    data.append({'Title': title_markdown, 'Contents': contents_markdown})

df = pd.DataFrame(data)
df.to_csv('question.csv',index=False, encoding="utf-8-sig")