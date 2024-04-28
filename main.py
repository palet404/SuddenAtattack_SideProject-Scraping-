import time
import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime
from queue import Queue
from sqlalchemy import String, create_engine
from DBsaver import create_table, save_data, load_db, create_session
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

DB_DIRECTORY = r"c:\RYUCODING\SuddenAtattack_SideProject(Scraping)"
DB_NAME = "Inflearn_DB.db"
TABLENAME = "Inflearn_study"



def scrape_inflearn(page):

    inflearn_studylist_url = f'https://www.inflearn.com/community/studies?page={page}&order=recent'
    studylist_response = requests.get(inflearn_studylist_url)
    studylist = BeautifulSoup(studylist_response.text, "html.parser")
    elements = studylist.find_all(class_=CLASS_NAME)

    return elements

def extract_detail_post_link(element):
    # Extract detail post link from element
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

#postdata = class_ = 'content__body markdown-body'
# editdate_ele = detail_page.find('span', class_ = 'sub-title sub-title__updated-at')

def get_page_elements(detail_page, ele_type) :

    '''
    detail_page is response of each detail study post URL\n
    ele_type = postbody, write_date, edit_date\n
    postbody is prettified in function\n
    '''

    detail_page = BeautifulSoup(detail_page.text, 'html.parser')

    if ele_type == 'postbody' :
        postbody = detail_page.find(class_='content__body markdown-body')
        postbody = postbody.prettify()
        return postbody

    elif ele_type == 'write_date' :
        ele_write_date = detail_page.find('span', class_='sub-title sub-title__created-at')
        write_date_str = ele_write_date.find('span', class_='sub-title__value').text.strip()
        write_date = datetime.strptime('20' + write_date_str, "%Y.%m.%d %H:%M")
        return write_date
    
    elif ele_type == 'edite_date' :

        try :
            ele_edit_date = detail_page.find('span', class_='sub-title sub-title__updated-at')
            edit_date_str = ele_edit_date.find('span', class_='sub-title__value').text.strip()
            edit_date = datetime.strptime('20' + edit_date_str, "%Y.%m.%d %H:%M")
        except :
            print("It post isn't edited !")
            edit_date = False

        return edit_date



def main():
    
    # Is there DB in directory?
    full_db_path = os.path.join(DB_DIRECTORY,DB_NAME)
    loaded_table = load_db(full_db_path,TABLENAME)

    if loaded_table is not None :
        inflearn_table = loaded_table
        
    elif  loaded_table == None : 

        table_name = "inflearn_study"

        columns = {
                'Inflearn_studies': {'type' : String},
                'Inflearn_PostLinkURL': {'type' : String},
                'Inflearn_PostBodys': {'type' : String},
                'Inflearn_study_Writedays': {'type' : String},
                'Inflearn_study_editdays' : {'type' : String, 'nullable' : True}
                }
    
        inflearn_table = create_table(table_name, columns)

    page = 1

    while True:

        elements = scrape_inflearn(page)
        OutOfDate = False

        for element in elements:

            existing_row = False

            if Is_element_within_days(element,TARGET_CLASS,TAG_WITH_DATE, REFERENCE_DATE):
                
                detail_post_link = extract_detail_post_link(element)
                detail_page = requests.get(detail_post_link)
                post_body = get_page_elements(detail_page,ele_type='postbody')
                write_date = get_page_elements(detail_page,ele_type='write_date')
                edit_date = get_page_elements(detail_page, ele_type ='edit_date')

                #string data sholud be prettified for be used as inner HTML(PostBody is already prettified)
                element = element.prettify()

                element = str(element)
                post_body = str(post_body)
                
                row = {'Inflearn_studies':element, 
                       'Inflearn_PostLinkURL':detail_post_link, 
                       'Inflearn_PostBodys': post_body,
                       'Inflearn_study_writedate': write_date,
                       'Inflearn_study_editdate' : edit_date}
                
                last_url = detail_post_link.rfind('/')
                base_url = detail_post_link[:last_url + 1]
                
                full_engine_path = 'sqlite:///' + full_db_path
                engine = create_engine(full_engine_path)
                session = create_session(engine)

                try :
                    # comparing element in db with post link url(base url)
                    # editing post it's base url doesn't change that is why using it for comparing method  
                    existing_row = session.query(inflearn_table).filter(inflearn_table.Inflearn_PostLinkURL.like(f'{base_url}%')).first()
                    session.execute(existing_row)
                    session.commit()
                    session.close()

                    # avoid duplicated ele, and update items
                    if not existing_row or edit_date != existing_row.Inflearn_study_editdate :
                        save_data(row, inflearn_table, full_db_path)
                    else:
                        # Already exists and not edited, skip
                        pass

                except Exception as e :
                    #For passing fist generate of table
                    print(f'error occured {e}')

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