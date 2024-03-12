from urllib.parse import urlparse
from queue import Queue

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

def extract_elements_within_days(elements, target_class, tag_with_date, reference_date):
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
