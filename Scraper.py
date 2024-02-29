import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from queue import Queue
from datetime import datetime, timedelta



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

# # 태그를 ClassName으로 하는 DF 반환하는 코드
# url = "https://www.inflearn.com/community/studies?page=1&order=recent"
# tag_names = ['li', 'div','a']
# class_names = ['question-container', 'another-class','e-click-post']
# target_tags = [{'name': 'h3', 'class': 'title__text'}, {'name': 'p', 'class': 'question__body'},{'name': 'href', 'tag': 'a', 'class': 'e-click-post'}]
# questions_df = TagsScraper(url, tag_names, class_names, target_tags)
# questions_df.to_csv('question_df_StripText.csv',encoding='utf-8-sig')

def Is_within_days(time_string,reference_date):
    """
   주어진 기준일(reference_date)로부터 몇 일 이내인지를 확인하는 함수입니다.

    Parameters:
    - time_string (str): 시간을 나타내는 문자열입니다. 예를 들어 "5일 전"과 같은 형식입니다.
    - reference_date (int): 기준일로부터의 일 수를 나타내는 정수입니다.

    Returns:
    - bool: 기준일로부터 몇 일 이내이면 True, 그렇지 않으면 False를 반환합니다.    """

    if "방금" in time_string:
        return True
    elif "분 전" in time_string:
        return True
    elif "시간 전" in time_string:
        return True
    elif "일 전" in time_string:
        time_ago = int(time_string.split("일")[0])
        if time_ago <= reference_date :
            return True
    elif "달 전" in time_string:
        return False
    else :
        return False

def Search_Element(elements, target_class, target_tag, reference_date):
    Result_Queue = Queue()

    for element in elements : 
     element_prettify = element.prettify()
     date_check = element.find(class_=target_class).find_all(target_tag)
     date_check = [tag.get_text() for tag in date_check]
     time_string = date_check[2]
     IsWithIn= Is_within_days(time_string, reference_date)
     if IsWithIn :
         Result_Queue.put(element_prettify)
     else :
         return Result_Queue
    
    return Result_Queue

def Search_Element_WithInDays(target_class, target_class_In, target_tag, reference_date):

    Result_Queue = Queue()

    for page in range(1,100):
        url = f'https://www.inflearn.com/community/studies?page={page}&order=recent'
        response = requests.get(url)
        soup = BeautifulSoup(response.text,"html.parser")
        elements= soup.find_all(class_ = target_class)
    
        for element in elements : 
            element_prettify = element.prettify()
            date_check = element.find(class_=target_class_In).find_all(target_tag)
            date_check = [tag.get_text() for tag in date_check]
            time_string = date_check[2]
            IsWithIn= Is_within_days(time_string, reference_date)
            if IsWithIn :
                Result_Queue.put(element_prettify)
            else :
                return Result_Queue
    
    return Result_Queue
    
class_name = 'question-container'
target_class = "question__info-detail"
target_tag = "span"
reference_date = 7

Result_Ele = Queue()

for page in range(1,100) :
    url = f'https://www.inflearn.com/community/studies?page={page}&order=recent'
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    # GetElement from target class name
    elements= soup.find_all(class_ = "question-container")
    PageTargetElements = Search_Element(elements, target_class, target_tag, reference_date)
    while not PageTargetElements.empty():
        print(PageTargetElements.get())

    if PageTargetElements.qsize() < 20:
        while not PageTargetElements.empty():
            PageTargetEle = PageTargetElements.get()
            Result_Ele.put(PageTargetEle)
            print(PageTargetEle)
        break

    else :
        while not PageTargetElements.empty():
            PageTargetEle = PageTargetElements.get()
            print(PageTargetEle)
            Result_Ele.put(PageTargetEle)
            

#with open('Result_Ele.txt', 'w') as file:
#    while not Result_Ele.empty():
#        element = Result_Ele.get()  # 큐에서 요소를 가져옴
#        file.write(str(element) + '\n')  # 요소를 파일에 씁니다.
    

## Get prettified HTML element from target class and tag

## Return element_preetify as File
#for i, element_prettify in enumerate(elements_prettify, start=1):
#    with open(f"element_{i}.html", "w", encoding="utf-8") as file:
#        file.write(element_prettify)

#Get CSS From target site
##element_css = soup.find_all('link', rel='stylesheet')
##print(element_css)