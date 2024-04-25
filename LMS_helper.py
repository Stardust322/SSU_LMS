import selenium
import time
from tkinter import *
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 중요도 판별 함수 - 오름차순 정렬
def day_check(time):
    if time.startswith("D-"):
        return 24 * int(time.split("D-")[1])
    elif time == "마감됨":
        return 1000000
    elif time.endswith("시간 전"):
        return int(time.split("시간 전")[0])
    else:
        return 999999

# 자동로그인 함수
def SSU_login(id, pw):
    URL = "https://smartid.ssu.ac.kr/Symtra_sso/smln.asp?apiReturnUrl=https%3A%2F%2Flms.ssu.ac.kr%2Fxn-sso%2Fgw-cb.php"

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    #options=chrome_options
    driver = webdriver.Chrome()
    driver.get(URL)
    
    user_id = driver.find_element(By.ID,'userid')
    user_id.send_keys(id)

    user_pw = driver.find_element(By.ID, 'pwd')
    user_pw.send_keys(pw)
    user_pw.send_keys(Keys.RETURN)

    driver.implicitly_wait(5)

    my_page = driver.find_element(By.XPATH, '//*[@id="xnm2_content"]/div[1]/div[1]/div[1]/div/a')
    my_page.click()

    driver.implicitly_wait(5)
    driver.get("https://canvas.ssu.ac.kr/learningx/dashboard?user_login="+str(id)+"&locale=ko")

    time.sleep(3)
    driver.implicitly_wait(10)

    sub_name = driver.find_elements(By.CLASS_NAME,"xnscc-header-title")

    for i in range(len(sub_name)):

        driver.find_element(By.XPATH,'//*[@id="root"]/div/div/div[2]/div[2]/div/div['+ str(i+1) +']/div/div[1]/button').click()


    assign = driver.find_elements(By.CLASS_NAME,"xn-student-todo-item-container")

    menu_info = ["동영상","화상강의","대면수업출결","과제","퀴즈","토론"]
    menu_num = driver.find_elements(By.CLASS_NAME, "xnhti-count")

    for i in range(len(menu_num)):
        print(menu_info[i],":",menu_num[i].text, "\n")

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
        print(sub_info[i][0],"\n남은기한 :",str(day).replace("999999","기한 제한없음"),"\n\n")
    

# GUI 구현 - Tkinter
win = Tk()
win.title("SSU lms Log-In")
win.geometry("400x300")
win.option_add("*Font","궁서 20")

lab_d = Label(win)
img = PhotoImage(file="header_logo.png", master = win)

lab_d.config(image=img)
lab_d.pack()

lab1 = Label(win)
lab1.config(text="ID")
lab1.pack()

ent1 = Entry(win)
ent1.insert(0,"학번(작번)")
def clear(event):
    if ent1.get() == "학번(작번)":
        ent1.delete(0,len(ent1.get()))

ent1.bind("<Button-1>",clear)
ent1.pack()

lab2 = Label(win)
lab2.config(text="Password")
lab2.pack()

ent2 = Entry(win)
ent2.config(show="*")
ent2.pack()

btn = Button(win)
btn.config(text="LOG-IN")
def login():
    SSU_login(ent1.get(), ent2.get())
    lab3.config(text="Success.")

btn.config(command=login)
btn.pack()

lab3 = Label(win)
lab3.pack()


win.mainloop()
