import time
from tkinter import *
import tkinter.font
from bs4 import BeautifulSoup
import requests
import re
import webbrowser
import requests
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timezone

# import selenium
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

# v2.0.0 부터 request session 유지 사용

def open_url(url):
    webbrowser.open(url)
    
def clean_html(text):
    text = re.sub(r"<.*?>", "", text)
    text = text.replace("\xa0", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def time_until_deadline(deadline_str):
    if deadline_str == None:
        return "기간 X"
    
    deadline = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    delta = deadline - now

    if delta.total_seconds() <= 0:
        return "마감됨"
    
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    

    if days >= 1:
        return f"D-{days}"
    elif hours >= 1:
        return f"{hours}시간 전"
    else:
        return f"{minutes}분 전"
    
def SSU_login(id, pw):

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    login_url = "https://smartid.ssu.ac.kr/Symtra_sso/smln_pcs.asp?apiReturnUrl=https%3A%2F%2Flms.ssu.ac.kr%2Fxn-sso%2Fgw-cb.php"
    data = {"userid": id, "pwd": pw, "in_tp_bit" : "0", "rqst_caus_cd" : "03"}

    response = session.post(login_url, data=data)
    token = response.text.split("Token=")[1].split("&sIdno=")[0]
    # print(f"Token : {token}")

    result_response = session.get(f"https://lms.ssu.ac.kr/xn-sso/gw-cb.php?sToken={token}&sIdno={id}")
    # print(f"result : {result}")


    get_rsa_url = result_response.text.split("iframe.src=\"")[1].split("\"")[0]
    iframe_response = session.get(get_rsa_url)

    rsa_key_str = iframe_response.text.split("-----BEGIN RSA PRIVATE KEY-----")[1].split("-----END RSA PRIVATE KEY-----")[0]
    rsa_key_str = rsa_key_str.strip().replace(" ", "\n")
    rsa_key_pem = f"-----BEGIN RSA PRIVATE KEY-----\n{rsa_key_str}\n-----END RSA PRIVATE KEY-----"

    pattern = r'loginCryption\("([^"]+)"'
    matches = re.findall(pattern, iframe_response.text)
    actual_encrypted = matches[0]

    private_key = serialization.load_pem_private_key(
        rsa_key_pem.encode(),
        password=None,
        backend=default_backend()
    )
    
    encrypted_data = base64.b64decode(actual_encrypted)
    decrypted_pwd = private_key.decrypt(encrypted_data, padding.PKCS1v15()).decode('utf-8')

    login_data = {
        "utf8": "✓",
        "redirect_to_ssl": "1",
        "after_login_url": "",
        "pseudonym_session[unique_id]": id,
        "pseudonym_session[password]": decrypted_pwd,
        "pseudonym_session[remember_me]": "0"
    }

    login_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': get_rsa_url,
        'Origin': 'https://canvas.ssu.ac.kr'
    }

    session.post(
        "https://canvas.ssu.ac.kr/login/canvas",
        data=login_data,
        headers=login_headers,
        allow_redirects=True
    )



    tokens = {}
    for cookie in session.cookies:
        if cookie.name.lower() or "auth" in cookie.name.lower():
            tokens[cookie.name] = cookie.value


    student_infos = {}
    student_profile = {}
    base_headers = {
            'Accept': 'application/json',
            'X-CSRF-Token': tokens["sToken"]
        }
    student_info = session.get("https://canvas.ssu.ac.kr/api/v1/users/self/profile", headers=base_headers).json()

    student_profile["id"] = student_info["id"]
    student_profile["student_code"] = id
    student_profile["short_student_code"] = str(student_info["name"]).split("(")[1].split(")")[0]
    student_profile["name"] = str(student_info["name"]).replace(f"({student_profile["short_student_code"]})", "")

    get_courses = session.get("https://canvas.ssu.ac.kr/api/v1/dashboard/dashboard_cards", headers=base_headers).json()

    courses = []
    subject_links = {}
    for course in get_courses:
        temp = {}
        temp["name"] = course["shortName"]
        temp["course_code"] = course["id"]
        subject_links[course["id"]] = course["shortName"]
        get_announcements = session.get(f"https://canvas.ssu.ac.kr/api/v1/courses/{course["id"]}/discussion_topics?only_announcements=true", headers=base_headers)
        temp["announcement"] = get_announcements.json()
        courses.append(temp)

    student_infos["course"] = courses

    announcements = []
    for announcement in student_infos["course"]:
        if len(announcement["announcement"])!=0:
            anno_subject = re.sub(r"\(\d+\)","", announcement["name"])
            for announce in announcement["announcement"]:
                anno_title = announce["title"]
                anno_message = announce["message"]
                anno_created = announce["created_at"]
            announcements.append([anno_subject, anno_title, clean_html(anno_message), anno_created])
    announcements = sorted(announcements, key = lambda item: str(item[3]), reverse=True)

    dashboard_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
        'Authorization': f'Bearer {tokens["xn_api_token"]}',
        "Content-Type": "application/json" 
    }

    todo_list = session.get("https://canvas.ssu.ac.kr/learningx/api/v1/learn_activities/to_dos?term_ids[]=43&term_ids[]=40", headers=dashboard_headers).json()

    tasks = []

    for todo in todo_list["to_dos"]:
        if len(todo["todo_list"]) != 0:
            subject_name = re.sub(r"\(\d+\)","", subject_links[todo["course_id"]]).strip()
            for task in todo["todo_list"]:
                task_title = task["title"]
                task_component = task["component_type"]
                if task_component == "commons":
                    task_type = task["commons_type"]
                else :
                    task_type = "assignment"
                dead_line = task["due_date"]
                tasks.append([subject_name, task_title, task_type, time_until_deadline(dead_line), dead_line])

    tasks = sorted(tasks, key = lambda item: str(item[4]))

    subject_list = []
    subject_links = []
    for subject in student_infos["course"]:
        name = str(subject["name"]).strip()
        name_pre = re.sub(r"\(\d+\)","", name).strip()
        if name_pre != name:
            subject_list.append(name_pre)
            subject_links.append(f"https://canvas.ssu.ac.kr/courses/{subject["course_code"]}")
    
    return announcements, tasks, student_profile, subject_list, subject_links

def get_weather():
    url = "https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&ssc=tab.nx.all&query=%EB%8F%99%EC%9E%91%EA%B5%AC+%EB%82%A0%EC%94%A8&oquery=%EC%83%81%EB%8F%84%EB%8F%99+%EB%82%A0%EC%94%A8&tqi=iwAkOwqptbNssKwtbMCssssstjd-300018"    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    today = soup.select_one("div._today")
    chart = soup.select_one("ul.today_chart_list")
    
    weather = today.select_one("span.blind").text
    curr_temp = today.select_one("strong").text.replace("현재 온도", "")
    prev_temp = today.select_one("div.temperature_info span").text.strip().replace("높아요", "↑").replace("낮아요", "↓")
    feels, humid, wind_spd = [x.text for x in today.select("dd")]
    wind_dir = today.select("dt")[2].text
    dust, fine_dust, uv, sunrise_time = [x.text for x in chart.select("span.txt")]
    time_type = chart.select("strong.title")[3].text
    
    is_night = time_type == "일출"
    night_sfx = "_night" if is_night else ""
    
    if "맑음" in weather:
        img = f"SSU_LMS/app_data/weather/sunny{night_sfx}.png"
    elif "구름" in weather:
        img = f"SSU_LMS/app_data/weather/so_cloud{night_sfx}.png"
    elif "흐림" in weather:
        img = "SSU_LMS/app_data/weather/cloud.png"
    elif "비" in weather:
        img = "SSU_LMS/app_data/weather/rain.png"
    
    return weather, curr_temp, prev_temp, feels, humid, wind_spd, wind_dir, img, dust, fine_dust, uv, time_type, uv

def check_status(status):
    status_map = {
        "좋음": ("dodger blue", "black"),
        "보통": ("yellow", "black"),
        "나쁨": ("red", "black")
    }
    
    for key, colors in status_map.items():
        if key in status:
            return colors
    
    return "white", "black"

# selenium 로그인 구현 코드 (사용 안함)
# def SSU_login(id, pw):
#     start = time.time()
#     assign_num_text = "\n"
#     assign_name_list = []
#     assign_time_list = []
#     stu_name = ""
#     URL = "https://smartid.ssu.ac.kr/Symtra_sso/smln.asp?apiReturnUrl=https%3A%2F%2Flms.ssu.ac.kr%2Fxn-sso%2Fgw-cb.php"
    
#     chrome_options = Options()
#     chrome_options.add_argument("--disable-gpu") 
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument('--window-size=1500,1500')
#     driver = webdriver.Chrome(options=chrome_options)
#     driver.get(URL)
#     user_id = driver.find_element(By.ID,'userid')
#     user_id.send_keys(id)

#     user_pw = driver.find_element(By.ID, 'pwd')
#     user_pw.send_keys(pw)
#     user_pw.send_keys(Keys.RETURN)
#     driver.implicitly_wait(1)
#     name = driver.find_element(By.XPATH,'//*[@id="header"]/nav/div/div[1]/div[3]/div[2]/div/button/span')
    
#     stu_name = str(name.text).split("(")[0]
#     time.sleep(0.5)
#     driver.get("https://canvas.ssu.ac.kr/learningx/dashboard?user_login="+str(id)+"&locale=ko")
#     driver.implicitly_wait(3)

#     sub_name = driver.find_elements(By.CLASS_NAME,"xnscc-header-title")
#     for i in range(len(sub_name)):

#         driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[2]/div[2]/div/div['+ str(i+1) +']/div/div[1]/button').click()

#     assign = driver.find_elements(By.CLASS_NAME,"xn-student-todo-item-container")
#     menu_info = ["동영상","화상강의","대면수업출결","과제","퀴즈","토론"]
#     menu_num = driver.find_elements(By.CLASS_NAME, "xnhti-count")

#     for i in range(len(menu_num)):
#         assign_num_text += str(menu_info[i]) + " : "+str(menu_num[i].text)+"\n"

#     day_info = []
#     day_import = [] 
#     sub_info = {}

#     for i in range(len(assign)):
#         data = str(assign[i].text).split("\n")
#         if len(data) > 1:
#             day_info.append(str(assign[i].text).split("\n")[1])
#         else:
#             day_info.append("999999")
#         day_import.append(day_check(day_info[i]))
#         sub_info[data[0]] = day_check(day_info[i])
        
#     sub_info = sorted(sub_info.items(), key = lambda item: item[1])

#     for i in range(len(sub_info)):
#         day = day_info[day_import.index(sub_info[i][1])]
#         assign_name_list.append(sub_info[i][0])
#         assign_time_list.append(f"({str(day).replace("999999","기한 X")})")
#     end = time.time()
#     return assign_name_list, assign_time_list, stu_name, 