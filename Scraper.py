import requests
from bs4 import BeautifulSoup
import pandas as pd
import markdown
import os
from datetime import datetime

def TagsScraper(url, tag_names, class_names, target_tags):
    """
    웹페이지에서 요소를 스크랩하고 DataFrame으로 반환합니다.

    Parameters:
    url (str): 스크랩할 웹페이지의 URL입니다.
    tag_names (list of str): 스크랩할 요소의 태그 이름들을 포함한 리스트입니다.
    class_names (list of str): 스크랩할 요소의 클래스 이름들을 포함한 리스트입니다.
    target_tags (list of dict): 각 요소에서 추출할 데이터의 정보를 포함한 딕셔너리들을 포함한 리스트입니다.
                                각 딕셔너리는 'name', 'tag', 'class' 키를 가져야 합니다.
                                'name': 추출된 데이터의 이름,
                                'tag': 해당 데이터가 포함된 태그 이름,
                                'class': 해당 데이터가 포함된 클래스 이름
    Returns:
    pandas.DataFrame: 추출된 데이터를 포함하는 DataFrame 객체입니다.
    """
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        data = []
        for tag_name, class_name in zip(tag_names, class_names):
            questions = soup.find_all(tag_name, class_=class_name)
            for question in questions:
                question_data = {}
                for target_tag in target_tags:
                    target_element = question.find(target_tag['name'], class_=target_tag['class'])
                    if target_element:
                        question_data[target_tag['name']] = target_element.get_text(strip=True)
                data.append(question_data)

        df = pd.DataFrame(data)
        df.to_csv('question.csv', index=False, encoding="utf-8-sig")
        return df
    else:
        print('Error:', response.status_code)
        return None

# 태그를 ClassName으로 하는 DF 반환하는 코드
     
url = "https://www.inflearn.com/community/studies?page=1&order=recent"
tag_names = ['li', 'div']
class_names = ['question-container', 'another-class']
target_tags = [{'name': 'h3', 'class': 'title__text'}, {'name': 'p', 'class': 'question__body'}]
questions_df = TagsScraper(url, tag_names, class_names, target_tags)
print(questions_df)

def GetElement(url, class_name):
    # 해당 URL에 GET 요청을 보내고 응답을 받음
    response = requests.get(url)

    # 응답의 상태코드가 200인지 확인
    if response.status_code == 200:
        # HTML을 BeautifulSoup으로 파싱
        soup = BeautifulSoup(response.text, 'html.parser')

        # 클래스가 주어진 class_name인 요소를 찾음
        elements = soup.find_all(class_=class_name)

        return elements
    else:
        print('Error:', response.status_code)
        return None

url = 'https://www.inflearn.com/community/studies?page=1&order=recent'
class_name = 'question-container'

elements = GetElement(url, class_name)
if elements:
    # 파일명 생성
    now = datetime.now()
    file_name = now.strftime("%Y-%m-%d-%H-%M") + ".txt"

    # 파일에 요소(element) 내용 쓰기
    with open(file_name, "w", encoding="utf-8") as file:
        for idx, element in enumerate(elements, start=1):
            file.write(f"Element {idx}:\n{element}\n\n")

    print(f"Elements saved to '{file_name}' successfully.")