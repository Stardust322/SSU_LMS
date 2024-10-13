import os
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from PIL import Image, ImageTk
import PIL.Image
from module import SSU_login, get_weather, check_status

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("SSU lms")
        self.root.geometry("800x400")
        self.current_frame = None
        self.current_subframe = None
        self.font_size = 16
        self.path = "Tkinter_lms/app_data/recent_login.txt"
        self.dark_path = "Tkinter_lms/app_data/status.txt"
        self.logo_path = "Tkinter_lms/app_data/header_logo.png"
        isDark_mode = int(open(self.dark_path,"r").read())
        if isDark_mode == 1:
            self.bg, self.fg, self.fg_gray = "black", "white", "white"
        else:
            self.bg, self.fg, self.fg_gray= "white", "black", "gray"
        self.version = "1.4.1"
        #if os.path.isfile("app_info.txt") == False:
            #f = open(self.path, "w")
            #f.write("{}")
            #f.close()
        if os.path.isfile(self.path):
            self.id, self.pw = open(self.path,"r").read().split("\n")
            name_list, time_list, student_name = SSU_login(self.id, self.pw)
            self.main_page(name_list, time_list, student_name)
        else:
            self.login_page()

    def login_page(self):
        self.clear_frame()
        self.clear_subframe()
        self.current_frame = tk.Frame(self.root, width=800, height=400)
        self.current_frame.pack()
        Login_fontStyle = tkFont.Font(family="Lucida Grande",size=18)
        logo_img = tk.Label(self.current_frame)
        self.img = tk.PhotoImage(file=self.logo_path, master = self.current_frame)
        logo_img.config(image=self.img)
        logo_img.place(relx=0.1,rely=0.34)
        

        ID_label = tk.Label(self.current_frame, font=Login_fontStyle)
        ID_label.config(text="ID")
        ID_label.place(relx=0.55,rely=0.23)

        ID_entry = tk.Entry(self.current_frame, font=Login_fontStyle)
        ID_entry.insert(0,"학번(작번)")

        def clear(event):
            if ID_entry.get() == "학번(작번)":
                ID_entry.delete(0,len(ID_entry.get()))

        ID_entry.bind("<Button-1>",clear)
        ID_entry.place(relx=0.55,rely=0.3)

        PW_label = tk.Label(self.current_frame, font=Login_fontStyle)
        PW_label.config(text="Password")
        PW_label.place(relx=0.55,rely=0.42)

        PW_entry = tk.Entry(self.current_frame, font=Login_fontStyle)
        PW_entry.config(show="*")
        PW_entry.place(relx=0.55,rely=0.5)

        LOGIN_btn = tk.Button(self.current_frame, font=Login_fontStyle, width=20,bg="deep sky blue")
        def login():
            id = ID_entry.get()
            pw = PW_entry.get()
            try:
                name_list, time_list, student_name = SSU_login(id, pw)
                f = open(self.path, "w")
                f.write(f"{id}\n{pw}")
                f.close()
                self.main_page(name_list, time_list, student_name)
            except:
                messagebox.showerror("LOGIN Fail", "학번 또는 비밀번호가 잘못되었습니다.")
        LOGIN_btn.config(text="LOGIN", command=login)
        LOGIN_btn.place(relx=0.548, rely=0.591)

    def main_page(self, name_list, time_list, student_name):
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

        Main_fontStyle = tkFont.Font(family="Lucida Grande",size=18)
        Name_label = tk.Label(self.current_subframe, font=Main_fontStyle, text=f"{student_name} 학생\n학번 : {self.id}")
        Name_label.place(relx=0.16, rely=0.63)
        
        Task_label = tk.Label(self.current_frame, font=Main_fontStyle, text="Tasks List", fg=self.fg, bg=self.bg)
        Task_label.place(relx=0.04, rely=0.08)

        n = len(name_list) if len(name_list) < 8 else 8
    
        Task_fontStyle = tkFont.Font(family="Lucida Grande", size=10)
        danger_num, attent_num, safety_num, finish_num = 0, 0, 0, 0
        for i in range(n):
            bg_c = ""
            ft_c = ""
            Task_btn = tk.Button(self.current_frame, font=Task_fontStyle)
            rest_time = time_list[i]
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
            
            Task_btn.config(text=str(name_list[i])+" "+str(rest_time), width=60, bg=bg_c, fg=ft_c)
            Task_btn.place(relx=0.04, rely=0.2+(0.08*i))

        def go_main():
            self.main_page(name_list, time_list, student_name)
        
        def go_setting():
            self.setting_page()

        def go_weather():
            self.weather_page()
        
        def go_bab():
            self.bab_page()
        
        def go_gpt():
            self.gpt_page()

        btn_fontStyle = tkFont.Font(family="Lucida Grande",size=10)
        btn_width, btn_height, btn_dist = 6, 4, 0.2
        bab_btn = tk.Button(self.current_subframe, font=btn_fontStyle, width=btn_width, height=btn_height)
        bab_btn.config(text="학식", command=go_bab)
        bab_btn.place(relx=0.0, rely=0.86)

        Wea_btn = tk.Button(self.current_subframe, font=btn_fontStyle, width=btn_width, height=btn_height)
        Wea_btn.config(text="날씨", command=go_weather)
        Wea_btn.place(relx=btn_dist * 1, rely=0.86)

        Home_btn = tk.Button(self.current_subframe, font=btn_fontStyle, width=btn_width, height=btn_height)
        Home_btn.config(text="홈", command=go_main)
        Home_btn.place(relx=btn_dist * 2, rely=0.86)

        dday_btn = tk.Button(self.current_subframe, font=btn_fontStyle, width=btn_width, height=btn_height)
        dday_btn.config(text="GPT", command=go_gpt)
        dday_btn.place(relx=btn_dist * 3, rely=0.86)
        
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

        Setting_fontStyle = tkFont.Font(family="Lucida Grande", size=18)
        Version_fontStyle = tkFont.Font(family="Lucida Grande", size=9)
        Title_fontStyle = tkFont.Font(family="Lucida Grande", size=12)
        Subtitle_fontStyle = tkFont.Font(family="Lucida Grande", size=10)

        def Logout():
            response = messagebox.askokcancel("LogOut", "로그아웃 하시겠습니까?")
            if response:
                os.remove(self.path)
                self.login_page()

        Setting_label = tk.Label(self.current_frame, font=Setting_fontStyle, text="Setting", fg=self.fg, bg=self.bg)
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
        Darkmode_check = tk.Checkbutton(self.current_frame, text="다크 모드", font=Title_fontStyle, fg=self.fg, bg=self.bg, variable=CheckVar1, command=save_status)
        Darkmode_check.place(relx=0.04, rely=0.2)

        Darkmode_subtitle = tk.Label(self.current_frame, font=Subtitle_fontStyle, text="어두운 화면으로 시력을 보호합니다.", fg=self.fg_gray, bg=self.bg)
        Darkmode_subtitle.place(relx=0.25, rely=0.208)

        Logout_btn = tk.Button(self.current_frame, font=Title_fontStyle, text="로그아웃", fg="red", command=Logout)
        Logout_btn.place(relx=0.04, rely=0.80)

        Version_label = tk.Label(self.current_frame, font=Version_fontStyle, text=f"Version {self.version} / Copyrights 2024. Lee SangHwa All rights reserved.", fg=self.fg_gray, bg=self.bg)
        Version_label.place(relx=0.15, rely=0.94)

    def weather_page(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, width=530, height=400, bg=self.bg)
        self.current_frame.pack(side="right")
        Weather_fontStyle = tkFont.Font(family="Lucida Grande",size=18)
        weather_data = get_weather()

        locate_label = tk.Label(self.current_frame, font=Weather_fontStyle, text="숭실대학교의 날씨", fg=self.fg, bg=self.bg)
        locate_label.place(relx=0.04, rely=0.08)
        
        temperture_label = tk.Label(self.current_frame, font=tkFont.Font(size=20), text=weather_data[1], fg=self.fg, bg=self.bg)
        temperture_label.place(relx=0.45, rely=0.4)

        original_image = Image.open(weather_data[7])
        resized_image = original_image.resize((68, 68), Image.LANCZOS)  
        self.img1 = ImageTk.PhotoImage(resized_image)
        logo_img = tk.Label(self.current_frame)
        logo_img.config(image=self.img1 , bg=self.bg)
        logo_img.place(relx=0.325, rely=0.3)

        subinfo_label1 = tk.Label(self.current_frame, font=tkFont.Font(size=14), text=f"어제보다 {weather_data[2]} / {weather_data[0]}", fg=self.fg, bg=self.bg)
        subinfo_label1.place(relx=0.3, rely=0.48)

        subinfo_label2 = tk.Label(self.current_frame, font=tkFont.Font(size=8), text=f"체감기온 {weather_data[3]}ㆍ습도 {weather_data[4]}ㆍ{weather_data[6]} {weather_data[5]}", fg=self.fg, bg=self.bg)
        subinfo_label2.place(relx=0.3, rely=0.54)
        title = ["미세 먼지", "초미세먼지", " 자외선 "]
        dist = [0, 0.125, 0.27]
        for i in range(3):
            stat_btn = tk.Button(self.current_frame, font=tkFont.Font(size=9), text=f"{title[i]}\n{weather_data[8+i]}", bg=check_status(weather_data[8+i])[0], fg=check_status(weather_data[8+i])[1])
            stat_btn.place(relx=0.3 + dist[i], rely=0.58)

    def bab_page(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, width=530, height=400, bg=self.bg)
        self.current_frame.pack(side="right")
        Bab_fontStyle = tkFont.Font(family="Lucida Grande",size=18)

        Bab_label = tk.Label(self.current_frame, font=Bab_fontStyle)
        Bab_label.config(text="오늘의 학식", fg=self.fg, bg=self.bg)
        Bab_label.place(relx=0.04, rely=0.08)

    def gpt_page(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, width=530, height=400, bg=self.bg)
        self.current_frame.pack(side="right")
        Dday_fontStyle = tkFont.Font(family="Lucida Grande",size=18)

        Dday_label = tk.Label(self.current_frame, font=Dday_fontStyle)
        Dday_label.config(text="GPT", fg=self.fg, bg=self.bg)
        Dday_label.place(relx=0.04, rely=0.08)

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