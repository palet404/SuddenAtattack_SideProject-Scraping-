from urllib.parse import urlparse
from queue import Queue

def Is_within_days(time_string,reference_date):

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

def Is_element_within_days(element, target_class, tag_with_date, reference_date):
        
    date_check = element.find(class_=target_class).find_all(tag_with_date)
    date_check = [tag.get_text() for tag in date_check]
    time_string = date_check[2]
    IsWithIn= Is_within_days(time_string, reference_date)

    if IsWithIn :
        return True
    else :
        return False
    

def extract_title_from_url(url):
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Get the path of the URL
    path = parsed_url.path
    
    # Split the path by '/'
    path_parts = path.split('/')
    
    # Extract the last part of the path (title)
    title = path_parts[-1]
    
    return title.replace('-', ' ')


def extract_base_url(detail_post_url):
    # 입력된 URL에서 마지막 슬래시('/')의 인덱스를 찾습니다.
    last_slash_index = detail_post_url.rfind('/')
    
    # 마지막 슬래시('/')의 인덱스 이전까지의 부분을 반환합니다.
    base_url = detail_post_url[:last_slash_index + 1]  # 마지막 슬래시('/')도 포함하기 위해 +1을 합니다.
    
    return base_url