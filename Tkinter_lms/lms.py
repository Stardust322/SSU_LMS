import selenium
import time
from tkinter import *
import tkinter.font
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

assign_num_text = "\n"
assign_name_list = []
assign_time_list = []
stu_name = ""

def day_check(time):
    if time.startswith("D-"):
        return 24 * int(time.split("D-")[1])
    elif time == "마감됨":
        return 1000000
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
    #print(round(end - start, 3))
        
#GUI 구현
win = Tk()
win.title("SSU lms Log-In")
win.geometry("400x300")
win.option_add("*Font","궁서 20")

lab_d = Label(win)
img = PhotoImage(file="header_logo.png", master = win)
lab_d.config(image=img)
lab_d.place(relx=0.25,rely=0.01)

lab1 = Label(win)
lab1.config(text="ID")
lab1.place(relx=0.1,rely=0.2)

ent1 = Entry(win)
ent1.insert(0,"학번(작번)")

def clear(event):
    if ent1.get() == "학번(작번)":
        ent1.delete(0,len(ent1.get()))

ent1.bind("<Button-1>",clear)
ent1.place(relx=0.1,rely=0.3)

lab2 = Label(win)
lab2.config(text="Password")
lab2.place(relx=0.1,rely=0.4)

ent2 = Entry(win)
ent2.config(show="*")
ent2.place(relx=0.1,rely=0.5)

btn = Button(win)
btn.config(text="LOGIN")

def login():
    try:
        SSU_login(ent1.get(), ent2.get())
        lab3.config(text="Success.")
        f = open("recent_login.txt","w")
        f.write(ent1.get()+"\n"+ent2.get())
        f.close()
    except:
        lab3.config(text="LOGIN Fail.")

def start_timer():
    timer.config(state="disabled") 
    countdown(1)  

def countdown(seconds):
    global stu_name
    if seconds > 3:
        
        timer.after(1000, countdown, seconds-1)
    elif seconds <= 3 and seconds > 0:
        lab3.destroy()
        timer.config(text=f"Loading... {seconds}s")
        timer.after(1000, countdown, seconds-1)  
    else:
        win2 = Tk()
        win2.title("SSU Dashboard")
        win2.geometry("1200x800")
        win2.option_add("*Font","궁서 20")
        lab_d = Label(win2)
        img = PhotoImage(file="header_logo.png", master = win2)
        lab_d.config(image=img)
        lab_d.place(relx=0.4,rely=0.01)

        r_id = open("recent_login.txt","r").read().split("\n")[0]
        user_info = Button(win2)
        user_info.config(text=f"이름 : {stu_name}\n학번 : {r_id}")
        user_info.place(relx=0.1,rely=0.1)

        assign_list = Button(win2)
        assign_list.config(text=assign_num_text)
        assign_list.place(relx=0.1,rely=0.20)
        
        danger_num = 0
        attent_num = 0
        safety_num = 0 
        finish_num = 0
        
        for i in range(len(assign_name_list)):
            font = tkinter.font.Font(size=12)
            bg_c = ""
            ft_c = ""
            a = Button(win2)
            rest_time = assign_time_list[i]
            rest_time_rep = str(rest_time).replace("(","").replace(")","")

            if rest_time_rep.startswith("D-"):
                if int(rest_time_rep.replace("D-","")) <= 3:
                    bg_c = "yellow"
                    ft_c = "black"
                    attent_num += 1
                else:
                    bg_c = "white"
                    ft_c = "black"

            elif rest_time_rep == "마감됨":
                bg_c = "black"
                ft_c = "white"
                finish_num += 1
            elif rest_time_rep.endswith("시간 전"):
                bg_c = "red"
                ft_c = "black"
                danger_num += 1
            elif rest_time_rep == "기한 X":
                bg_c = "green"
                ft_c = "white"
                safety_num += 1
            else:
                bg_c = "white"
                ft_c = "black"
            
            a.config(text=str(assign_name_list[i])+" "+str(rest_time), font=font, width=58, bg=bg_c, fg=ft_c)
            a.place(relx=0.338, rely=0.1+(0.045*i))

        danger_btn = Button(win2)
        danger_btn.config(text=f"위험 : {danger_num}개",bg="red",fg="black",width=13,height=3)
        danger_btn.place(relx=0.1,rely=0.5)

        attent_btn = Button(win2)
        attent_btn.config(text=f"주의 : {attent_num}개",bg="yellow",fg="black",width=13,height=3)
        attent_btn.place(relx=0.1,rely=0.6)

        safety_btn = Button(win2)
        safety_btn.config(text=f"안전 : {safety_num}개",bg="green",fg="black",width=13,height=3)
        safety_btn.place(relx=0.1,rely=0.7)

        finish_btn = Button(win2)
        finish_btn.config(text=f"마감됨 : {finish_num}개",bg="black",fg="white",width=13,height=3)
        finish_btn.place(relx=0.1,rely=0.8)

        win.destroy()
        
        timer.config(state="normal")

timer = Label(win, text="")
timer.place(relx=0.28, rely=0.8)

def ult_login():
    start_timer()
    login()

def ult_recent_login():
    start_timer()
    recent_login()

btn.config(command=ult_login)
btn.place(relx=0.1,rely=0.6)

lab3 = Label(win)
lab3.place(relx=0.37,rely=0.8)

btn2 = Button(win)
btn2.config(text="최근 로그인")

def recent_login():    
    r_id = open("recent_login.txt","r").read().split("\n")[0]
    r_pw = open("recent_login.txt","r").read().split("\n")[1]
    SSU_login(r_id, r_pw)
    lab3.config(text="Success")

btn2.config(command=ult_recent_login)
btn2.place(relx=0.45, rely=0.6)

win.mainloop()
