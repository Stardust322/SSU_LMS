import sys
import os
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from PIL import Image as PILImage, ImageTk
import time
from tkinter import *
import tkinter.font
from bs4 import BeautifulSoup
import requests
import re
import webbrowser
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timezone
import urllib3
import ssl
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

def data_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.join(os.getenv('APPDATA'), 'SSU_LMS')
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    full_path = os.path.join(base_path, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    return full_path

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

def init_user_data():
    status_file = data_path('app_data/status.txt')
    login_file = data_path('app_data/recent_login.txt')
    
    if not os.path.exists(status_file):
        with open(status_file, 'w') as f:
            f.write('0')
    
    if not os.path.exists(login_file):
        open(login_file, 'w').close() 

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

    response = session.post(login_url, data=data, verify=False)
    token = response.text.split("Token=")[1].split("&sIdno=")[0]

    result_response = session.get(f"https://lms.ssu.ac.kr/xn-sso/gw-cb.php?sToken={token}&sIdno={id}", verify=False)

    get_rsa_url = result_response.text.split("iframe.src=\"")[1].split("\"")[0]
    iframe_response = session.get(get_rsa_url, verify=False)

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
        allow_redirects=True,
    verify=False
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
    student_info = session.get("https://canvas.ssu.ac.kr/api/v1/users/self/profile", headers=base_headers, verify=False).json()

    student_profile["id"] = student_info["id"]
    student_profile["student_code"] = id
    student_profile["short_student_code"] = str(student_info["name"]).split("(")[1].split(")")[0]
    student_profile["name"] = str(student_info["name"]).replace(f"({student_profile['short_student_code']})", "")

    get_courses = session.get("https://canvas.ssu.ac.kr/api/v1/dashboard/dashboard_cards", headers=base_headers, verify=False).json()

    courses = []
    subject_links = {}
    for course in get_courses:
        temp = {}
        temp["name"] = course["shortName"]
        temp["course_code"] = course["id"]
        subject_links[course["id"]] = course["shortName"]
        get_announcements = session.get(f"https://canvas.ssu.ac.kr/api/v1/courses/{course['id']}/discussion_topics?only_announcements=true", headers=base_headers, verify=False)
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

    todo_list = session.get("https://canvas.ssu.ac.kr/learningx/api/v1/learn_activities/to_dos?term_ids[]=43&term_ids[]=40", headers=dashboard_headers, verify=False).json()

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
            subject_links.append(f"https://canvas.ssu.ac.kr/courses/{subject['course_code']}")
    
    return announcements, tasks, student_profile, subject_list, subject_links

def get_weather():
    url = "https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&ssc=tab.nx.all&query=%EB%8F%99%EC%9E%91%EA%B5%AC+%EB%82%A0%EC%94%A8&oquery=%EC%83%81%EB%8F%84%EB%8F%99+%EB%82%A0%EC%94%A8&tqi=iwAkOwqptbNssKwtbMCssssstjd-300018"    
    response = requests.get(url, verify=False)
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
        img = f"app_data/weather/sunny{night_sfx}.png"
    elif "구름" in weather:
        img = f"app_data/weather/so_cloud{night_sfx}.png"
    elif "흐림" in weather:
        img = "app_data/weather/cloud.png"
    elif "비" in weather:
        img = "app_data/weather/rain.png"
    
    return weather, curr_temp, prev_temp, feels, humid, wind_spd, wind_dir, resource_path(img), dust, fine_dust, uv, time_type, uv

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

class App:
    def __init__(self, root):
        init_user_data()
        self.root = root
        self.root.title("SoongSil University lms")
        self.root.geometry("800x400")
        self.current_frame, self.current_subframe = None, None
        self.font_size = 16
        
        self.recent_path = data_path("app_data/recent_login.txt")
        self.dark_path = data_path("app_data/status.txt")
        self.logo_path = resource_path("app_data/header_logo.png")
        
        # 다크모드 설정 읽기
        try:
            isDark_mode = int(open(self.dark_path, "r").read().strip())
        except:
            isDark_mode = 0
            
        self.isLoginPage = False
        self.announcements, self.tasks, self.student_profile, self.subjects, self.links = None, None, None, None, None
        self.mainFont = tkFont.Font(family="Lucida Grande", size=18)
        
        if isDark_mode == 1:
            self.bg, self.fg, self.fg_gray = "black", "white", "white"
        else:
            self.bg, self.fg, self.fg_gray = "white", "black", "gray"
            
        self.version = "2.0.0"
        
        # 자동 로그인 체크
        if os.path.exists(self.recent_path) and os.path.getsize(self.recent_path) > 0:
            try:
                with open(self.recent_path, "r") as f:
                    content = f.read().strip()
                    if content and '\n' in content:
                        self.id, self.pw = content.split("\n")
                        self.announcements, self.tasks, self.student_profile, self.subjects, self.links = SSU_login(self.id, self.pw)
                        self.main_page()
                    else:
                        self.login_page()
            except Exception as e:
                print(f"자동 로그인 오류: {e}")
                messagebox.showerror("Error", "자동 로그인중 오류가 발생했습니다.\n로그인 화면으로 이동합니다.")
                try:
                    os.remove(self.recent_path)
                except:
                    pass
                self.login_page()
        else:
            self.login_page()

    def login_page(self):
        self.clear_frame()
        self.clear_subframe()
        self.isLoginPage = True
        self.current_frame = tk.Frame(self.root, width=800, height=400)
        self.current_frame.pack()
        logo_img = tk.Label(self.current_frame)
        self.img = tk.PhotoImage(file=self.logo_path, master=self.current_frame)
        logo_img.config(image=self.img)
        logo_img.place(relx=0.1, rely=0.34)
        
        ID_label = tk.Label(self.current_frame, font=self.mainFont, text="ID")
        ID_label.place(relx=0.55, rely=0.23)

        ID_entry = tk.Entry(self.current_frame, font=self.mainFont)
        ID_entry.insert(0, "학번(작번)")
        ID_entry.bind("<Button-1>", lambda e: ID_entry.delete(0, tk.END) if ID_entry.get() == "학번(작번)" else None)
        ID_entry.place(relx=0.55, rely=0.3)

        PW_label = tk.Label(self.current_frame, font=self.mainFont, text="Password")
        PW_label.place(relx=0.55, rely=0.42)

        PW_entry = tk.Entry(self.current_frame, font=self.mainFont, show="*")
        PW_entry.place(relx=0.55, rely=0.5)

        LOGIN_btn = tk.Button(self.current_frame, font=self.mainFont, width=20, bg="deep sky blue")
        
        def login():
            try:
                self.id = ID_entry.get()
                self.pw = PW_entry.get()
                self.announcements, self.tasks, self.student_profile, self.subjects, self.links = SSU_login(self.id, self.pw)
                self.root.unbind('<Return>')
                with open(self.recent_path, "w") as f:
                    f.write(f"{self.id}\n{self.pw}")
                self.main_page()
            except Exception as e:
                messagebox.showerror("LOGIN Fail", f"학번 또는 비밀번호가 잘못되었습니다.\n{e}")
                self.id, self.pw = None, None
        
        ID_entry.bind('<Return>', lambda e : PW_entry.focus_set())
        PW_entry.bind('<Return>', lambda e : login())

        ID_entry.focus_set()
        LOGIN_btn.config(text="LOGIN", command=login)
        LOGIN_btn.place(relx=0.548, rely=0.591)

    def main_page(self):
        self.clear_frame()
        self.clear_subframe()
        self.current_subframe = tk.Frame(self.root, width=270, height=400, bg="pale turquoise")
        self.current_frame = tk.Frame(self.root, width=530, height=400, bg=self.bg)
        self.current_subframe.pack(side="left")
        self.current_frame.pack(side="right")

        logo_img = tk.Label(self.current_subframe)
        self.img = tk.PhotoImage(file=self.logo_path, master=self.current_subframe)
        logo_img.config(image=self.img, bg="pale turquoise")
        logo_img.place(relx=0.05, rely=0.34)

        Name_label = tk.Label(self.current_subframe, font=self.mainFont, 
                              text=f"{self.student_profile['name']} 학생\n학번 : {self.id}")
        Name_label.place(relx=0.16, rely=0.63)
        
        Task_label = tk.Label(self.current_frame, font=self.mainFont, text="Tasks List", fg=self.fg, bg=self.bg)
        Task_label.place(relx=0.04, rely=0.08)

        n = len(self.tasks) if len(self.tasks) < 8 else 8
    
        Task_fontStyle = tkFont.Font(family="Lucida Grande", size=10)
        
        for i in range(n):
            bg_c = ""
            ft_c = ""
            Task_btn = tk.Button(self.current_frame, font=Task_fontStyle)
            rest_time = self.tasks[i][3]
            rest_time_rep = str(rest_time).replace("(", "").replace(")", "")

            if rest_time_rep.startswith("D-"):
                if int(rest_time_rep.replace("D-", "")) <= 3:
                    bg_c = "yellow"
                    ft_c = "black"
                else:
                    bg_c = "white"
                    ft_c = "black"
            elif rest_time_rep == "마감됨":
                bg_c = "black"
                ft_c = "white"
            elif rest_time_rep.endswith("시간 전") or rest_time_rep.endswith("분 전"):
                bg_c = "red"
                ft_c = "black"
            elif rest_time_rep == "기한 X":
                bg_c = "green"
                ft_c = "white"
            else:
                bg_c = "white"
                ft_c = "black"
            
            Task_btn.config(text=f"{self.tasks[i][0]}\n{self.tasks[i][1]} ({self.tasks[i][3]})", 
                           width=60, bg=bg_c, fg=ft_c)
            Task_btn.place(relx=0.04, rely=0.17+(0.1*i))

        def go_main():
            self.main_page()
        
        def go_setting():
            self.setting_page()

        def go_weather():
            self.weather_page()
        
        def go_info():
            self.info_page()
        
        def go_subj():
            self.subj_page()

        btn_fontStyle = tkFont.Font(family="Lucida Grande", size=10)
        btn_width, btn_height, btn_dist = 6, 4, 0.2
        
        info_btn = tk.Button(self.current_subframe, font=btn_fontStyle, width=btn_width, height=btn_height)
        info_btn.config(text="공지", command=go_info)
        info_btn.place(relx=0.0, rely=0.86)

        Wea_btn = tk.Button(self.current_subframe, font=btn_fontStyle, width=btn_width, height=btn_height)
        Wea_btn.config(text="날씨", command=go_weather)
        Wea_btn.place(relx=btn_dist * 1, rely=0.86)

        Home_btn = tk.Button(self.current_subframe, font=btn_fontStyle, width=btn_width, height=btn_height)
        Home_btn.config(text="홈", command=go_main)
        Home_btn.place(relx=btn_dist * 2, rely=0.86)

        subj_btn = tk.Button(self.current_subframe, font=btn_fontStyle, width=btn_width, height=btn_height)
        subj_btn.config(text="과목", command=go_subj)
        subj_btn.place(relx=btn_dist * 3, rely=0.86)
        
        setting_btn = tk.Button(self.current_subframe, font=btn_fontStyle, width=btn_width, height=btn_height)
        setting_btn.config(text="설정", command=go_setting)
        setting_btn.place(relx=btn_dist * 4, rely=0.86)

    def setting_page(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, width=530, height=400, bg=self.bg)
        self.current_frame.pack(side="right")

        Version_fontStyle = tkFont.Font(family="Lucida Grande", size=9)
        Title_fontStyle = tkFont.Font(family="Lucida Grande", size=12)
        Subtitle_fontStyle = tkFont.Font(family="Lucida Grande", size=10)

        def Logout():
            response = messagebox.askokcancel("LogOut", "로그아웃 하시겠습니까?")
            if response:
                try:
                    os.remove(self.recent_path)
                except:
                    pass
                self.login_page()

        Setting_label = tk.Label(self.current_frame, font=self.mainFont, text="Setting", fg=self.fg, bg=self.bg)
        Setting_label.place(relx=0.04, rely=0.08)

        def save_status():
            with open(self.dark_path, 'w') as file:
                file.write('%s' % CheckVar1.get())
            
            if CheckVar1.get() == 1:
                self.bg, self.fg, self.fg_gray = "black", "white", "white"
            else:
                self.bg, self.fg, self.fg_gray = "white", "black", "gray"
            self.setting_page()

        CheckVar1 = tk.IntVar(value=1 if self.bg == "black" else 0)
        Darkmode_check = tk.Checkbutton(self.current_frame, text="다크 모드", font=Title_fontStyle, 
                                        fg=self.fg, bg=self.bg, variable=CheckVar1, command=save_status)
        Darkmode_check.place(relx=0.04, rely=0.2)

        Darkmode_subtitle = tk.Label(self.current_frame, font=Subtitle_fontStyle, 
                                     text="어두운 화면으로 시력을 보호합니다.", 
                                     fg=self.fg_gray, bg=self.bg)
        Darkmode_subtitle.place(relx=0.25, rely=0.208)

        Logout_btn = tk.Button(self.current_frame, font=Title_fontStyle, text="로그아웃", fg="red", command=Logout)
        Logout_btn.place(relx=0.04, rely=0.80)

        Version_label = tk.Label(self.current_frame, font=Version_fontStyle, 
                                text=f"Version {self.version} / Copyrights 2024. Lee SangHwa All rights reserved.", 
                                fg=self.fg_gray, bg=self.bg)
        Version_label.place(relx=0.15, rely=0.94)

    def weather_page(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, width=530, height=400, bg=self.bg)
        self.current_frame.pack(side="right")

        weather_data = get_weather()

        locate_label = tk.Label(self.current_frame, font=self.mainFont, text="숭실대학교의 날씨", fg=self.fg, bg=self.bg)
        locate_label.place(relx=0.04, rely=0.08)
    
        temperture_label = tk.Label(self.current_frame, font=tkFont.Font(size=20),
                                    text=weather_data[1], fg=self.fg, bg=self.bg)
        temperture_label.place(relx=0.45, rely=0.4)

        try:
            original_image = PILImage.open(weather_data[7])
            resized_image = original_image.resize((68, 68), PILImage.LANCZOS)
            self.img1 = ImageTk.PhotoImage(resized_image)
        except Exception as e:
            print(f"[오류] 이미지 로드 실패: {e}")
            self.img1 = None

        logo_img = tk.Label(self.current_frame, bg=self.bg)
        if self.img1:
            logo_img.config(image=self.img1)
        logo_img.place(relx=0.325, rely=0.3)

        subinfo_label1 = tk.Label(self.current_frame, font=tkFont.Font(size=14), 
                                 text=f"어제보다 {weather_data[2]} / {weather_data[0]}", fg=self.fg, bg=self.bg)
        subinfo_label1.place(relx=0.3, rely=0.48)

        subinfo_label2 = tk.Label(self.current_frame, font=tkFont.Font(size=8), 
                                 text=f"체감기온 {weather_data[3]}ㆍ습도 {weather_data[4]}ㆍ{weather_data[6]} {weather_data[5]}", 
                                 fg=self.fg, bg=self.bg)
        subinfo_label2.place(relx=0.3, rely=0.54)

        title = ["미세 먼지", "초미세먼지", " 자외선 "]
        dist = [0, 0.125, 0.27]
        for i in range(3):
            bg, fg = check_status(weather_data[8+i])
            stat_btn = tk.Button(self.current_frame, font=tkFont.Font(size=9),
                                text=f"{title[i]}\n{weather_data[8+i]}",
                                bg=bg, fg=fg)
            stat_btn.place(relx=0.3 + dist[i], rely=0.58)

    def info_page(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, width=530, height=400, bg=self.bg)
        self.current_frame.pack(side="right")

        info_label = tk.Label(self.current_frame, font=self.mainFont)
        sub_label = tk.Label(self.current_frame, font=tkFont.Font(family="Lucida Grande", size=10))
        sub_label.config(text="*시험 키워드에 강조 표시", fg="gray", bg=self.bg)
        info_label.config(text="공지사항", fg=self.fg, bg=self.bg)
        info_label.place(relx=0.04, rely=0.08)
        sub_label.place(relx=0.69, rely=0.12)
        
        info_fontStyle = tkFont.Font(family="Lucida Grande", size=10)
        for i in range(len(self.announcements)):
            def show_detail(idx=i):
                title = self.announcements[idx][1]
                content = self.announcements[idx][2]
                self.info_message_page(f"{title}", content)

            info_btn = tk.Button(self.current_frame, font=info_fontStyle, command=show_detail)
            anno_title = self.announcements[i][1]
            bg, fg = "white", "black"
            important_words = ["고사", "시험", "테스트", "퀴즈", "test", "exam", "quiz"]
            if any(important_word in str(anno_title).lower() for important_word in important_words):
                bg = "yellow"
            info_btn.config(text=f"{self.announcements[i][0]}\n{anno_title}", width=60, bg=bg, fg=fg)
            info_btn.place(relx=0.04, rely=0.17+(0.1*i))

    def info_message_page(self, title, text):
        self.clear_frame()
        
        def go_info():
            self.info_page()
            
        self.current_frame = tk.Frame(self.root, width=530, height=400, bg=self.bg)
        self.current_frame.pack(side="right")
        
        return_fontStyle = tkFont.Font(family="Lucida Grande", size=10)
        return_btn = tk.Button(self.current_frame, font=return_fontStyle)
        return_btn.config(text="돌아가기", command=go_info, bg="red", fg="white")
        return_btn.place(relx=0.86, rely=0.92)
        
        title_label = tk.Label(self.current_frame, font=self.mainFont)
        title_label.config(text=f"{title}", fg=self.fg, bg=self.bg)
        title_label.place(relx=0.04, rely=0.08)
        
        text_label = tk.Label(self.current_frame, font=tkFont.Font(family="Lucida Grande", size=10))
        text_label.config(text=f"{text}", fg=self.fg, bg=self.bg, wraplength=480, justify="left")
        text_label.place(relx=0.04, rely=0.178)

    def subj_page(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, width=530, height=400, bg=self.bg)
        self.current_frame.pack(side="right")
        subjectFont = tkFont.Font(family="Lucida Grande", size=10)
        
        subj_label = tk.Label(self.current_frame, font=self.mainFont)
        subj_label.config(text="과목", fg=self.fg, bg=self.bg)
        subj_label.place(relx=0.04, rely=0.08)
        
        for i in range(len(self.subjects)):
            subject_btn = tk.Button(self.current_frame, font=subjectFont)
            subject_btn.config(text=self.subjects[i], width=60, bg="deep sky blue", fg="black", 
                             command=lambda url=self.links[i]: open_url(url))
            subject_btn.place(relx=0.04, rely=0.2+(0.08*i))
            
        sub_label = tk.Label(self.current_frame, font=tkFont.Font(family="Lucida Grande", size=10))
        sub_label.config(text="*과목을 클릭하면 lms로 이동합니다.", fg="gray", bg=self.bg)
        sub_label.place(relx=0.56, rely=0.145)

    def clear_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
    
    def clear_subframe(self):
        if self.current_subframe is not None:
            self.current_subframe.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()