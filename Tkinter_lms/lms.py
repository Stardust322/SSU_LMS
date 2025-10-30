import os
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from PIL import Image, ImageTk
from module import SSU_login, get_weather, check_status, open_url

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("SoongSil University lms")
        self.root.geometry("800x400")
        self.current_frame, self.current_subframe = None, None
        self.font_size = 16
        self.recent_path = "SSU_LMS/app_data/recent_login.txt"
        self.dark_path = "SSU_LMS/app_data/status.txt"
        self.logo_path = "SSU_LMS/app_data/header_logo.png"
        isDark_mode = int(open(self.dark_path,"r").read())
        self.isLoginPage = False
        self.announcements, self.tasks, self.student_profile, self.subjects, self.links = None, None, None, None, None
        self.mainFont = tkFont.Font(family="Lucida Grande",size=18)
        if isDark_mode == 1:
            self.bg, self.fg, self.fg_gray = "black", "white", "white"
        else:
            self.bg, self.fg, self.fg_gray= "white", "black", "gray"
        self.version = "2.0.0"
        #if os.path.isfile("app_info.txt") == False:
            #f = open(self.path, "w")
            #f.write("{}")
            #f.close()
        if os.path.isfile(self.recent_path):
            try:
                self.id, self.pw = open(self.recent_path,"r").read().split("\n")
                self.announcements, self.tasks, self.student_profile, self.subjects, self.links = SSU_login(self.id, self.pw)
                self.main_page()
            except:
                messagebox.showerror("Error", "자동 로그인중 오류가 발생했습니다.\n로그인 화면으로 이동합니다.")
                os.remove(self.recent_path)
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
        self.img = tk.PhotoImage(file=self.logo_path, master = self.current_frame)
        logo_img.config(image=self.img)
        logo_img.place(relx=0.1,rely=0.34)
        
        ID_label = tk.Label(self.current_frame, font=self.mainFont, text="ID")
        ID_label.place(relx=0.55,rely=0.23)

        ID_entry = tk.Entry(self.current_frame, font=self.mainFont)
        ID_entry.insert(0,"학번(작번)")

        def clear(event):
            if ID_entry.get() == "학번(작번)":
                ID_entry.delete(0,len(ID_entry.get()))

        ID_entry.bind("<Button-1>",clear)
        ID_entry.place(relx=0.55,rely=0.3)

        PW_label = tk.Label(self.current_frame, font=self.mainFont, text="Password")
        PW_label.place(relx=0.55,rely=0.42)

        PW_entry = tk.Entry(self.current_frame, font=self.mainFont, show="*")
        PW_entry.place(relx=0.55,rely=0.5)

        LOGIN_btn = tk.Button(self.current_frame, font=self.mainFont, width=20,bg="deep sky blue")
        def login():
            try:
                self.id = ID_entry.get()
                self.pw = PW_entry.get()
                self.announcements, self.tasks, self.student_profile, self.subjects, self.links = SSU_login(self.id, self.pw)
                f = open(self.recent_path, "w")
                f.write(f"{self.id}\n{self.pw}")
                f.close()
                # print(self.name_list)
                self.main_page()
            except Exception as e:
                messagebox.showerror("LOGIN Fail", f"학번 또는 비밀번호가 잘못되었습니다.{e}")
                self.id, self.pw = None, None
        LOGIN_btn.config(text="LOGIN", command=login)
        LOGIN_btn.place(relx=0.548, rely=0.591)

    def main_page(self):
        self.clear_frame()
        self.clear_subframe()
        self.current_subframe = tk.Frame(self.root, width=270, height=400,bg="pale turquoise")
        self.current_frame = tk.Frame(self.root, width=530, height=400, bg=self.bg)
        self.current_subframe.pack(side="left")
        self.current_frame.pack(side="right")

        logo_img = tk.Label(self.current_subframe)
        self.img= tk.PhotoImage(file=self.logo_path, master = self.current_subframe)
        logo_img.config(image=self.img, bg="pale turquoise")
        logo_img.place(relx=0.05,rely=0.34)

        Name_label = tk.Label(self.current_subframe, font=self.mainFont, text=f"{self.student_profile["name"]} 학생\n학번 : {self.id}")
        Name_label.place(relx=0.16, rely=0.63)
        
        Task_label = tk.Label(self.current_frame, font=self.mainFont, text="Tasks List", fg=self.fg, bg=self.bg)
        Task_label.place(relx=0.04, rely=0.08)

        n = len(self.tasks) if len(self.tasks) < 8 else 8
    
        Task_fontStyle = tkFont.Font(family="Lucida Grande", size=10)
        danger_num, attent_num, safety_num, finish_num = 0, 0, 0, 0
        for i in range(n):
            bg_c = ""
            ft_c = ""
            Task_btn = tk.Button(self.current_frame, font=Task_fontStyle)
            rest_time = self.tasks[i][3]
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
            elif rest_time_rep.endswith("시간 전") or rest_time_rep.endswith("분 전"):
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
            
            Task_btn.config(text=f"{self.tasks[i][0]}\n{self.tasks[i][1]} ({self.tasks[i][3]})", width=60, bg=bg_c, fg=ft_c)
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

        btn_fontStyle = tkFont.Font(family="Lucida Grande",size=10)
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

    def load_settings(self):
        try:
            with open(self.dark_path, 'r') as file:
                dark_mode_status = int(file.read().strip())
                if dark_mode_status == 1:
                    self.bg, self.fg, self.fg_gray = "black", "white", "white"
                else:
                    self.bg, self.fg, self.fg_gray = "white", "black", "gray"
        except FileNotFoundError:
            pass

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
                os.remove(self.recent_path)
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

        Darkmode_subtitle = tk.Label(self.current_frame, font=Subtitle_fontStyle, text="어두운 화면으로 시력을 보호합니다.", 
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
        
        temperture_label = tk.Label(self.current_frame, font=tkFont.Font(size=20), text=weather_data[1], fg=self.fg, bg=self.bg)
        temperture_label.place(relx=0.45, rely=0.4)

        original_image = Image.open(weather_data[7])
        resized_image = original_image.resize((68, 68), Image.LANCZOS)  
        self.img1 = ImageTk.PhotoImage(resized_image)
        logo_img = tk.Label(self.current_frame)
        logo_img.config(image=self.img1 , bg=self.bg)
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
            stat_btn = tk.Button(self.current_frame, font=tkFont.Font(size=9), 
                                 text=f"{title[i]}\n{weather_data[8+i]}", bg=check_status(weather_data[8+i])[0], 
                                 fg=check_status(weather_data[8+i])[1])
            stat_btn.place(relx=0.3 + dist[i], rely=0.58)

    def info_page(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, width=530, height=400, bg=self.bg)
        self.current_frame.pack(side="right")

        info_label = tk.Label(self.current_frame, font=self.mainFont)
        sub_label = tk.Label(self.current_frame, font=tkFont.Font(family="Lucida Grande",size=10))
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

            info_btn = tk.Button(self.current_frame, font=info_fontStyle,command=show_detail)
            anno_title = self.announcements[i][1]
            bg, fg = "white", "black"
            important_words = ["고사", "시험", "테스트", "퀴즈", "test","exam","quiz"]
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
        text_label = tk.Label(self.current_frame, font=tkFont.Font(family="Lucida Grande",size=10))
        text_label.config(text=f"{text}", fg=self.fg, bg=self.bg, wraplength=480, justify="left")
        text_label.place(relx=0.04, rely=0.178)


    def subj_page(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, width=530, height=400, bg=self.bg)
        self.current_frame.pack(side="right")
        subjectFont = tkFont.Font(family="Lucida Grande",size=10)
        
        subj_label = tk.Label(self.current_frame, font=self.mainFont)
        subj_label.config(text="과목", fg=self.fg, bg=self.bg)
        subj_label.place(relx=0.04, rely=0.08)
        for i in range(len(self.subjects)):
            subject_btn = tk.Button(self.current_frame, font=subjectFont)
            subject_btn.config(text=self.subjects[i], width=60, bg="deep sky blue", fg="black", command=lambda url=self.links[i]: open_url(url))
            subject_btn.place(relx=0.04, rely=0.2+(0.08*i))
            sub_label = tk.Label(self.current_frame, font=tkFont.Font(family="Lucida Grande",size=10))
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