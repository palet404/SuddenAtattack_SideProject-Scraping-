from bs4 import BeautifulSoup

html_content = ""
with open('TargetHTMLFIle.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')
tags = soup.find_all(class_='style')
for tag in soup.find_all():
    # 태그에서 텍스트를 제외하고 태그 자체만을 출력
    print(tag)