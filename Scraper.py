import requests
from bs4 import BeautifulSoup
import pandas as pd
import markdown

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
     
# url = "https://www.inflearn.com/community/studies?page=1&order=recent"
# tag_names = ['li', 'div']
# class_names = ['question-container', 'another-class']
# target_tags = [{'name': 'h3', 'class': 'title__text'}, {'name': 'p', 'class': 'question__body'}]
# questions_df = scrape_questions(url, tag_names, class_names, target_tags)
# print(questions_df)
    
