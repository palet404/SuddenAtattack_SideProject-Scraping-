import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from queue import Queue
from sqlalchemy import String
from DBsaver import create_table, save_data
from utils import extract_title_from_url, Is_element_within_days

INFLEARN_SITE_URL = "https://www.inflearn.com"
CLASS_NAME = 'question-container'
#CLASS_NAME is tag class name contains study list
TARGET_CLASS = "question__info-detail"
#TARGET_CLASS is tag class name contains time string 
TAG_WITH_DATE = "span"
#TAG_WITH_DATE is tag contains time string
REFERENCE_DATE = 7
MAX_PAGES = 2
WAIT_TIME = 0

inflearn_studies = Queue()
inflearn_post_link_url = Queue()
inflearn_post_bodies = Queue()
inflearn_study_write_days = Queue()

def scrape_inflearn(page):

    inflearn_studylist_url = f'https://www.inflearn.com/community/studies?page={page}&order=recent'
    studylist_response = requests.get(inflearn_studylist_url)
    studylist = BeautifulSoup(studylist_response.text, "html.parser")
    elements = studylist.find_all(class_=CLASS_NAME)

    return elements

def extract_detail_post_link(element):
    # Extract detail post link from element
    element = BeautifulSoup(element, 'html.parser')
    detail_post_link = element.find(class_='e-click-post').get('href')
    #It's value is 43. WTF?, the very first code was without 'a', and I don't have idea why it was returns 43
    #It's because it wasn't converted as Beautifulsoup entity. => organize it
    if detail_post_link:
        return INFLEARN_SITE_URL + detail_post_link
    return None

def extract_detail_post_data(detail_post_link):
    # Extract post body and write date from detail post link
    post_body = None
    write_date = None

    # Scraping logic for detail post page
    try:
        response = requests.get(detail_post_link)
        if response.ok:
            detail_page = BeautifulSoup(response.text, 'html.parser')
            post_body_element = detail_page.find(class_='content__body markdown-body')
            if post_body_element:
                post_body = post_body_element.prettify()

            write_date_element = detail_page.find('span', class_='sub-title sub-title__created-at')
            if write_date_element:
                write_date_str = write_date_element.find('span', class_='sub-title__value').text.strip()
                write_date = datetime.strptime('20' + write_date_str, "%Y.%m.%d %H:%M")
    except Exception as e:
        print(f"Error scraping detail post: {e}")

    return post_body, write_date

def main():

    table_name = "inflearn_study"

    columns = {
                'Inflearn_studies': String,
                'Inflearn_PostLinkURL': String,
                'Inflearn_PostBodys': String,
                'Inflearn_study_Writedays': String
                }
    
    dynamic_table = create_table(table_name, columns)

    page = 1

    while True:

        elements = scrape_inflearn(page)
        OutOfDate = False

        for element in elements:

            if Is_element_within_days(element,TARGET_CLASS,TAG_WITH_DATE, REFERENCE_DATE):
                detail_post_link = extract_detail_post_link(element)
                post_body, write_date = extract_detail_post_data(detail_post_link)

                row = [element, detail_post_link, post_body, write_date]
                save_data(row, dynamic_table, database_URL = 'sqlite:///my_database_test.db')

            else:
                OutOfDate = True
                break
        
        if OutOfDate:
            page = 0
            time.sleep(3600)
            
        page = page + 1

        time.sleep(WAIT_TIME)  # Sleep for 60 seconds before scraping again

if __name__ == "__main__":
    main()