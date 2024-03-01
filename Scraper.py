import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from queue import Queue
from datetime import datetime, timedelta
from time import sleep

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

def Search_Element_WithInDays(elements, target_class, tag_with_date, reference_date):
    Result_Queue = Queue()

    for element in elements : 
        element_prettify = element.prettify()
        date_check = element.find(class_=target_class).find_all(tag_with_date)
        date_check = [tag.get_text() for tag in date_check]
        time_string = date_check[2]
        IsWithIn= Is_within_days(time_string, reference_date)
        if IsWithIn :
            Result_Queue.put(element_prettify)
        else :
            return Result_Queue
    
    return Result_Queue

# Problem with rotating URL
def Search_Element_WithInDays_UsingInnerForLoop(target_class, target_class_In, target_attr, reference_date):

    Result_Queue = Queue()

    for page in range(1,100):
        url = f'https://www.inflearn.com/community/studies?page={page}&order=recent'
        response = requests.get(url)
        soup = BeautifulSoup(response.text,"html.parser")
        elements= soup.find_all(class_ = target_class)
    
        for element in elements : 
            element_prettify = element.prettify()
            date_check = element.find(class_=target_class_In).find_all(target_attr)
            date_check = [tag.get_text() for tag in date_check]
            time_string = date_check[2]
            IsWithIn= Is_within_days(time_string, reference_date)
            if IsWithIn :
                Result_Queue.put(element_prettify)
            else :
                return Result_Queue
    
    return Result_Queue
    
######################################### Main_Code ################################################

InflearnSiteURL = "https://www.inflearn.com"

Inflearn_studies = Queue()
Inflearn_PostLinkURL = Queue()
Inflearn_PostBodys = Queue()
Inflearn_study_Writedays = Queue()

#Needed to extract it after for-loop(rotating pages), it contains <scrpit>in it
Inflearn_studylist_css = 0
Inflearn_study_post_css = 0

## Get elements from target site(inflearn) according to reference_date
class_name = 'question-container'
target_class = "question__info-detail"
# tag_with_date, site below(refer to url) is <span> and parents tag is "question__info-detail"
tag_with_date = "span"
reference_date = 7


for page in range(1,5) :
    Inflearn_studylist_url = f'https://www.inflearn.com/community/studies?page={page}&order=recent'
    StudylistResponse = requests.get(Inflearn_studylist_url)
    Studylist = BeautifulSoup(StudylistResponse.text,"html.parser")
    # GetElements from target class name('question-container' in inflearn)
    elements= Studylist.find_all(class_ = class_name)
    # GetElementsQuque Within reference_date
    TargetPageElements = Search_Element_WithInDays(elements, target_class, tag_with_date, reference_date)
    # Get studylist css, for one time (comparing type of var)
    if type(Inflearn_studylist_css) == int:
        Inflearn_studylist_css = Studylist.find_all('link', rel='stylesheet')

    # TargetPageElements only contains within days(7days) ele
    if TargetPageElements.qsize() == 20:
        while not TargetPageElements.empty():

            TargetPageEle = TargetPageElements.get()
            Inflearn_studies.put(TargetPageEle)
            
            # Get Detail Post Link from TargetPageEle(question-container)
            TargetPageEle = BeautifulSoup(TargetPageEle,'html.parser')
            DetailPostLink = TargetPageEle.find(class_='e-click-post').get('href')
            ## Branch => If wanna extract Link from this code, : using for-loop, 
            DetailPostLink = InflearnSiteURL+DetailPostLink

            Inflearn_PostLinkURL.put(DetailPostLink)
            # Get Detail Post
            DetailStudyPageResponse = requests.get(DetailPostLink)
            DetailStudyPage = BeautifulSoup(DetailStudyPageResponse.text,'html.parser')
            DetailStudyPageBody = DetailStudyPage.find(class_='content__body markdown-body')
            DetailStudyPageBody = DetailStudyPageBody.prettify()

            Inflearn_PostBodys.put(DetailStudyPageBody)

            StudyWriteDate = DetailStudyPage.find_all('span', class_='sub-title sub-title__created-at')
            # Get post write date from Body
            for element in StudyWriteDate:
                WriteDate = element.find('span',class_='sub-title__value').text.strip()
                StudyWriteDate = WriteDate
                StudyWriteDate = '20'+StudyWriteDate
                Inflearn_study_Writedays.put(StudyWriteDate)

            # Avoding requests limits(It request 20times posts per each loop upon )
            sleep(1)
            
            print(TargetPageEle)
            print(DetailPostLink)
            print(DetailStudyPageBody)
            print(StudyWriteDate)

        

    # elif TargetPageQueue size smaller than 20, the page has element older than reference_date
    elif TargetPageElements.qsize() < 20 :
        while not TargetPageElements.empty():

            TargetPageEle = TargetPageElements.get()
            Inflearn_studies.put(TargetPageEle)
            
            # Get Detail Post Link from TargetPageEle(question-container)
            TargetPageEle = BeautifulSoup(TargetPageEle,'html.parser')
            DetailPostLink = TargetPageEle.find(class_='e-click-post').get('href')
            DetailPostLink = InflearnSiteURL+DetailPostLink

            Inflearn_PostLinkURL.put(DetailPostLink)
            # Get Detail Post
            DetailStudyPageResponse = requests.get(DetailPostLink)
            DetailStudyPage = BeautifulSoup(DetailStudyPageResponse.text,'html.parser')
            DetailStudyPageBody = DetailStudyPage.find(class_='content__body markdown-body')
            DetailStudyPageBody = DetailStudyPageBody.prettify()

            Inflearn_PostBodys.put(DetailStudyPageBody)

            StudyWriteDate = DetailStudyPage.find_all('span', class_='sub-title sub-title__created-at')

            # Get post write date from Body
            for element in StudyWriteDate:
                WriteDate = element.find('span',class_='sub-title__value').text.strip()
                StudyWriteDate = WriteDate
                StudyWriteDate = '20'+StudyWriteDate
                Inflearn_study_Writedays.put(StudyWriteDate)

            # Get post css, for one time (comparing type of var)
            if type(Inflearn_study_post_css) == int:
                Inflearn_study_post_css = DetailStudyPage.find_all('link', rel='stylesheet')

            print(TargetPageEle)
            print(DetailPostLink)
            print(DetailStudyPageBody)
            print(StudyWriteDate)

            # Avoding requests limits(It request 20times posts per each loop upon )
            sleep(1)


        break

# ##Get CSS From target site
# # element_css = soup.find_all('link', rel='stylesheet')
# # print(element_css)

####################################################################################################

# with open('ResultOfSearch_Element_WithInDays(forTest).html','r', encoding='utf-8') as file:
#     html_content = file.read()

# InflearnSiteURL = "https://www.inflearn.com"

# soup = BeautifulSoup(html_content,'html.parser')
# # Get Detail Post link from 'class = question-container'
# DetailLink = soup.find(class_='e-click-post').get('href')
# DetailLink = InflearnSiteURL+DetailLink

# response = requests.get(DetailLink)
# DetailStudyPage = BeautifulSoup(response.text,'html.parser')

# # Get Detail Post Body From URL
# DetailStudyPageBody = DetailStudyPage.find(class_='content__body markdown-body')
# StudyWriteDate = DetailStudyPage.find_all('span', class_='sub-title sub-title__created-at')

# # Get post write date from Body
# for element in StudyWriteDate:
#     WriteDate = element.find('span',class_='sub-title__value').text.strip()
#     StudyWriteDate = WriteDate
#     StudyWriteDate = '20'+StudyWriteDate

# print(DetailStudyPageBody)
# print("---------------StudyWriteDate------------------")
# print(StudyWriteDate)


# Write detail Study Page
# output_file = 'DetailStudyPage'

# with open(output_file, "w", encoding='utf-8') as file:
#     file.write(DetailStudyPage.prettify())

# print(f"HTML 파일이 {output_file}에 저장되었습니다.")