import selenium
import time
from tkinter import *
import tkinter.font
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests

assign_num_text = "\n"
assign_name_list = []
assign_time_list = []
stu_name = ""

def day_check(time):
    if time.startswith("D-"):
        return 24 * int(time.split("D-")[1])
    elif time == "마감됨":
        return 1000000
    elif time.endswith("분 전"):
        return int(time.split("분 전")[0]) / 60
    elif time.endswith("시간 전"):
        return int(time.split("시간 전")[0])
    else:
        return 999999
    
def SSU_login(id, pw):
    start = time.time()
    global assign_num_text
    global assign_name_list
    global assign_time_list
    global stu_name
    URL = "https://smartid.ssu.ac.kr/Symtra_sso/smln.asp?apiReturnUrl=https%3A%2F%2Flms.ssu.ac.kr%2Fxn-sso%2Fgw-cb.php"
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu") 
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--window-size=1500,1500')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    user_id = driver.find_element(By.ID,'userid')
    user_id.send_keys(id)

    user_pw = driver.find_element(By.ID, 'pwd')
    user_pw.send_keys(pw)
    user_pw.send_keys(Keys.RETURN)
    driver.implicitly_wait(1)
    name = driver.find_element(By.XPATH,'//*[@id="header"]/nav/div/div[1]/div[3]/div[2]/div/button/span')
    
    stu_name = str(name.text).split("(")[0]
    time.sleep(0.5)
    driver.get("https://canvas.ssu.ac.kr/learningx/dashboard?user_login="+str(id)+"&locale=ko")
    driver.implicitly_wait(3)

    sub_name = driver.find_elements(By.CLASS_NAME,"xnscc-header-title")
    for i in range(len(sub_name)):

        driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[2]/div[2]/div/div['+ str(i+1) +']/div/div[1]/button').click()

    assign = driver.find_elements(By.CLASS_NAME,"xn-student-todo-item-container")
    menu_info = ["동영상","화상강의","대면수업출결","과제","퀴즈","토론"]
    menu_num = driver.find_elements(By.CLASS_NAME, "xnhti-count")

    for i in range(len(menu_num)):
        assign_num_text += str(menu_info[i]) + " : "+str(menu_num[i].text)+"\n"

    day_info = []
    day_import = [] 
    sub_info = {}

    for i in range(len(assign)):
        data = str(assign[i].text).split("\n")
        if len(data) > 1:
            day_info.append(str(assign[i].text).split("\n")[1])
        else:
            day_info.append("999999")
        day_import.append(day_check(day_info[i]))
        sub_info[data[0]] = day_check(day_info[i])
        
    sub_info = sorted(sub_info.items(), key = lambda item: item[1])

    for i in range(len(sub_info)):
        day = day_info[day_import.index(sub_info[i][1])]
        assign_name_list.append(sub_info[i][0])
        assign_time_list.append(f"({str(day).replace("999999","기한 X")})")
    end = time.time()
    return assign_name_list, assign_time_list, stu_name, 

def get_weather():
    url = "https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&ssc=tab.nx.all&query=%EB%8F%99%EC%9E%91%EA%B5%AC+%EB%82%A0%EC%94%A8&oquery=%EC%83%81%EB%8F%84%EB%8F%99+%EB%82%A0%EC%94%A8&tqi=iwAkOwqptbNssKwtbMCssssstjd-300018"    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    status = soup.select("div._today")[0].select("span.blind")[0].text
    temp = soup.select("div._today")[0].select("strong")[0].text.replace("현재 온도","")
    yest_temp = soup.select("div._today")[0].select("div.temperature_info")[0].select("span")[0].text.strip()
    sub_info = soup.select("div._today")[0].select("dd")
    feel_tem, mort, wind = [i.text for i in sub_info]
    direction = soup.select("div._today")[0].select("dt")[2].text
    yest_temp = yest_temp.replace("높아요","↑").replace("낮아요","↓")
    chart = soup.select("ul.today_chart_list")[0].select("span.txt")
    dust, small_dust, sun, clock = [i.text for i in chart]
    sunset = soup.select("ul.today_chart_list")[0].select("strong.title")[3].text
    
    if "맑음" in status:
        sub = "_night" if sunset == "일출" else ""
        path = f"Tkinter_lms/app_data/weather/sunny{sub}.png"
    elif "구름" in status:
        sub = "_night" if sunset == "일출" else ""
        path = f"Tkinter_lms/app_data/weather/so_cloud{sub}.png"
    elif "흐림" in status:
        path = f"Tkinter_lms/app_data/weather/cloud.png"
    elif "비" in status:
        path = f"Tkinter_lms/app_data/weather/rain.png"
    return status, temp, yest_temp, feel_tem, mort, wind, direction, path, dust, small_dust, sun, sunset, sun

def check_status(status):
    if "좋음" in status:
        bg, fg = "dodger blue", "black"
    elif status == "보통":
        bg, fg = "yellow", "black"
    elif "나쁨" in status:
        bg, fg = "red", "black"
    else:
        bg, fg = "white", "black"
    return bg, fg