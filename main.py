import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from queue import Queue
from sqlalchemy import String
from DBsaver import create_table, save_data
from utils import extract_title_from_url, extract_elements_within_days

INFLEARN_SITE_URL = "https://www.inflearn.com"
CLASS_NAME = 'question-container'
TARGET_CLASS = "question__info-detail"
TAG_WITH_DATE = "span"
REFERENCE_DATE = 7
MAX_PAGES = 1
WAIT_TIME = 20

def scrape_inflearn(last_title=None):
    inflearn_studies = Queue()
    inflearn_post_link_url = Queue()
    inflearn_post_bodies = Queue()
    inflearn_study_write_days = Queue()
    stopped_due_to_duplicate = False

    for page in range(1, MAX_PAGES + 1):
        inflearn_studylist_url = f'https://www.inflearn.com/community/studies?page={page}&order=recent'
        studylist_response = requests.get(inflearn_studylist_url)
        studylist = BeautifulSoup(studylist_response.text, "html.parser")
        elements = studylist.find_all(class_=CLASS_NAME)
        target_page_elements = extract_elements_within_days(elements, TARGET_CLASS, TAG_WITH_DATE, REFERENCE_DATE)

        while not target_page_elements.empty():
            # Extract data from element
            element = target_page_elements.get()
            detail_post_link = extract_detail_post_link(element)
            if detail_post_link:
                current_title = extract_title_from_url(detail_post_link)
                if current_title == last_title:
                    stopped_due_to_duplicate = True
                    return (inflearn_studies, inflearn_post_link_url, inflearn_post_bodies, inflearn_study_write_days), stopped_due_to_duplicate
                post_body, write_date = extract_detail_post_data(detail_post_link)
                if post_body and write_date:
                    inflearn_studies.put(element)
                    inflearn_post_link_url.put(detail_post_link)
                    inflearn_post_bodies.put(post_body)
                    inflearn_study_write_days.put(write_date)

        #TargetPageQueue size smaller than 20, the page has element older than reference_date
        if target_page_elements.qsize() < 20:
            break

        time.sleep(WAIT_TIME)

    return (inflearn_studies, inflearn_post_link_url, inflearn_post_bodies, inflearn_study_write_days), stopped_due_to_duplicate

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
    last_title = None

    while True:
        collected_data, stopped_due_to_duplicate = scrape_inflearn(last_title)

        inflearn_studies, inflearn_post_link_url, inflearn_post_bodies, inflearn_study_write_days = collected_data

        table_name = "inflearn_study"
        columns = {
            'Inflearn_studies': String,
            'Inflearn_PostLinkURL': String,
            'Inflearn_PostBodys': String,
            'Inflearn_study_Writedays': String
        }

        data = {
            'Inflearn_studies': inflearn_studies,
            'Inflearn_PostLinkURL': inflearn_post_link_url,
            'Inflearn_PostBodys': inflearn_post_bodies,
            'Inflearn_study_Writedays': inflearn_study_write_days
        }

        dynamic_table = create_table(table_name, columns)
        last_row = save_data(data, dynamic_table, database_URL='sqlite:///my_database.db')
        if last_row:
            url_contain_title = last_row['Inflearn_PostLinkURL']
            last_title = extract_title_from_url(url_contain_title)

        if stopped_due_to_duplicate:
            print("Scraping stopped due to encountering a duplicate title.")
            break

        time.sleep(60)  # Sleep for 60 seconds before scraping again

if __name__ == "__main__":
    main()