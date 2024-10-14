import selenium
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from flask import Flask
from flask import request, redirect, url_for
# Flask version 지원종료.

assign_num_text = "\n"
assign_name_list = []
assign_time_list = []
result_text = ""
text = ""

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
    global text
    URL = "https://smartid.ssu.ac.kr/Symtra_sso/smln.asp?apiReturnUrl=https%3A%2F%2Flms.ssu.ac.kr%2Fxn-sso%2Fgw-cb.php"
    text = ""
    menu_info = ["동영상","화상강의","대면수업출결","과제","퀴즈","토론"]
    day_info = []
    day_import = [] 
    sub_info = {}
    task = []
    task_day = []
  
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
    menu_num = driver.find_elements(By.CLASS_NAME, "xnhti-count")

    for i in range(len(menu_num)):
        assign_num_text += str(menu_info[i]) + " : "+str(menu_num[i].text)+"\n"

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
        
        day_data = int(day_check(day))
        if day_data < 24:
            color = "red"
        elif day_data >= 24 and day_data <= 72:
            color = "yellow"
        elif day_data == 999999:
            color = "green"
        elif day_data == 1000000:
            color = "black completed"
            
        else:
            color = "none"

        task.append(f"{str(sub_info[i][0])} ({str(day).replace("999999","기한 X")})")
        task_day.append(color)
        
    tasks = [task, task_day]
    return tasks

#flask 시작
app = Flask(__name__)

@app.route('/', methods = ["GET","POST"])
def index():
    
    if request.method == "GET":
        with open("main.html", "r",encoding="utf-8") as file:
            strings = file.read()
            
        return strings
    else:
            
        id = request.form["username"]
        pw = request.form["password"]
        data = SSU_login(id, pw)

        return  #동적 html로 인해 파일저장X
      '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>과제 목록</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .loading span {
            display: inline-block;
            width: 10px;
            height: 10px;
            background-color: gray;
            border-radius: 50%;
            animation: loading 1s 0s linear infinite;
        }

        .loading span:nth-child(1) {
            animation-delay: 0s;
            background-color: red;
        }

        .loading span:nth-child(2) {
            animation-delay: 0.2s;
            background-color: orange;
        }

        .loading span:nth-child(3) {
            animation-delay: 0.4s;
            background-color: yellowgreen;
        }

        @keyframes loading {
            0%, 100% {
                opacity: 0;
                transform: scale(0.5);
            }
            50% {
                opacity: 1;
                transform: scale(1.2);
            }
        }

        .task-container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 400px;
            text-align: center;
        }

        .task-container h2 {
            margin-bottom: 20px;
            background-color: #003366;
            color: white;
        }

        .completed {
            text-decoration: line-through;
            color: grey;
        }

        #taskList {
            list-style-type: none;
            padding: 0;
        }

        #taskList li {
            margin: 10px 0;
            display: flex;
            align-items: center;
        }

        .task-checkbox {
            margin-right: 10px;
        }

        .pagination {
            margin-top: 20px;
        }

        .pagination button {
            padding: 5px 10px;
            margin: 0 5px;
        }

        .pagination span {
            font-size: 1em;
        }

        footer {
            position: absolute;
            bottom: 10px;
            text-align: center;
            width: 100%;
        }

        .loader {
            border: 16px solid #f3f3f3;
            border-radius: 50%;
            border-top: 16px solid #3498db;
            width: 120px;
            height: 120px;
            animation: spin 2s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .content {
            display: none;
        }

        center {
            color: #666;
            margin-bottom: 10px;
        }

        .red {
            margin-right: 10px;
            color: red;
            text-shadow: 1px 1px 1px #000;
        }

        .yellow {
            margin-right: 10px;
            color: yellow;
            text-shadow: 1px 1px 1px #000;
        }

        .green {
            margin-right: 10px;
            color: green;
            text-shadow: 1px 1px 1px #000;
        }

        .black {
            margin-right: 10px;
            color: white;
            background-color: black;
        }

        .fireworks {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 9999;
            justify-content: center;
            align-items: center;
        }

        .fireworks canvas {
            position: absolute;
            width: 100%;
            height: 100%;
        }

        

        .congrats-message {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 2em;
            color: white;
            z-index: 10000;
            text-align: center;
        }

        .congrats-message{
            background-color: #003366;
            color: white;
        }
    </style>
</head>
<body>
    <div class="loading">
        <span></span>
        <span></span>
        <span></span>
    </div>

    <div class="content">
        <div class="task-container">
            <h2>과제 목록</h2>
            <ul id="taskList">
                
            </ul>
            <div class="pagination">
                <button id="prevPage" disabled>이전</button>
                <span id="pageInfo"></span>
                <button id="nextPage">다음</button>
            </div>
        </div>
    </div>
    <div class="fireworks" id="fireworks">
        <canvas></canvas>
        <div class="congrats-message" id="congratsMessage">과제 완료!</div>
    </div>
    <footer>
        <center>Copyrights 2024. Lee SangHwa All rights reserved.</center>
    </footer>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const tasks = '''+str(data[0])+''';
            const tasks_day = '''+str(data[1])+''';
            const tasksPerPage = 5;
            let currentPage = 1;
            const totalPages = Math.ceil(tasks.length / tasksPerPage);
            let fireworksLaunched = false; // 추가된 플래그
        
            const taskList = document.getElementById('taskList');
            const prevPageBtn = document.getElementById('prevPage');
            const nextPageBtn = document.getElementById('nextPage');
            const pageInfo = document.getElementById('pageInfo');
            const fireworksContainer = document.getElementById('fireworks');
            const congratsMessage = document.getElementById('congratsMessage');
        
            function renderTasks() {
                taskList.innerHTML = '';
                const start = (currentPage - 1) * tasksPerPage;
                const end = start + tasksPerPage;
                const paginatedTasks = tasks.slice(start, end);
        
                paginatedTasks.forEach((task, index) => {
                    const taskId = `task${start + index + 1}`;
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <input type="checkbox" id="${taskId}" class="task-checkbox">
                        <label for="${taskId}" class="${tasks_day[start + index]}">${task}</label>
                    `;
                    taskList.appendChild(li);

                    // Load the checkbox state from local storage
                    const checkbox = document.getElementById(taskId);
                    if (localStorage.getItem(taskId) === 'checked') {
                        checkbox.checked = true;
                        checkbox.nextElementSibling.classList.add('completed');
                    }
                });
        
                pageInfo.textContent = `페이지 ${currentPage} / ${totalPages}`;
                prevPageBtn.disabled = currentPage === 1;
                nextPageBtn.disabled = currentPage === totalPages;

                checking();
            }
        
            prevPageBtn.addEventListener('click', function() {
                if (currentPage > 1) {
                    currentPage--;
                    renderTasks();
                }
            });
        
            nextPageBtn.addEventListener('click', function() {
                if (currentPage < totalPages) {
                    currentPage++;
                    renderTasks();
                }
            });
        
            function checking() {
                const checkboxes = document.querySelectorAll('.task-checkbox');
                checkboxes.forEach(function(checkbox) {
                    checkbox.addEventListener('change', function() {
                        if (checkbox.checked) {
                            checkbox.nextElementSibling.classList.add('completed');
                            localStorage.setItem(checkbox.id, 'checked');
                        } else {
                            checkbox.nextElementSibling.classList.remove('completed');
                            localStorage.removeItem(checkbox.id);
                        }
                        checkCompletion();
                    });
                });
            }
        
            function checkCompletion() {
                const yellowLabels = document.querySelectorAll('label.yellow');
                const redLabels = document.querySelectorAll('label.red');
                const allChecked = [...yellowLabels, ...redLabels].every(label => {
                    const checkbox = document.getElementById(label.getAttribute('for'));
                    return checkbox.checked;
                });

                if (allChecked && !fireworksLaunched) {
                    showCongrats();
                    launchFireworks();
                    fireworksLaunched = true; // 플래그 설정
                }
            }
        
            function showCongrats() {
                congratsMessage.style.display = 'block';
                setTimeout(() => congratsMessage.style.display = 'none', 5000);
            }

            function launchFireworks() {
                fireworksContainer.style.display = 'block';
                const canvas = fireworksContainer.querySelector('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
        
                function Particle(x, y, color) {
                    this.x = x;
                    this.y = y;
                    this.color = color;
                    this.speed = Math.random() * 2 + 1;
                    this.angle = Math.random() * Math.PI * 2;
                    this.radius = Math.random() * 2 + 1;
                    this.life = 50;
                    this.opacity = 1;
        
                    this.update = function() {
                        const dx = Math.cos(this.angle) * this.speed;
                        const dy = Math.sin(this.angle) * this.speed;
                        this.x += dx;
                        this.y += dy;
                        this.life--;
                        this.opacity = this.life / 50;
                    };
        
                    this.draw = function() {
                        ctx.beginPath();
                        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                        ctx.fillStyle = `rgba(${this.color}, ${this.opacity})`;
                        ctx.fill();
                    };
                }
        
                const particles = [];
        
                for (let i = 0; i < 100; i++) {
                    particles.push(new Particle(canvas.width / 2, canvas.height / 2, '255, 255, 0'));
                    particles.push(new Particle(canvas.width / 2, canvas.height / 2, '255, 255, 0'));
                }
        
                function pang() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
        
                    particles.forEach((particle, index) => {
                        particle.update();
                        particle.draw();
                        if (particle.life <= 0) {
                            particles.splice(index, 1);
                        }
                    });
        
                    if (particles.length > 0) {
                        requestAnimationFrame(animate);
                    } else {
                        fireworksContainer.style.display = 'none';
                    }
                }
        
                pang();
            }
        
            // 로딩 화면 처리 (출처 : https://mong-blog.tistory.com/entry/%EB%A1%9C%EB%94%A9-%ED%99%94%EB%A9%B4-%EB%A7%8C%EB%93%A4%EA%B8%B0-with-css)
            setTimeout(function() {
                document.querySelector('.loading').style.display = 'none';
                document.querySelector('.content').style.display = 'block';
                renderTasks();
            }, 2000); // 2초 후에 로딩 화면을 숨기고 실제 콘텐츠를 보여줌
        });
    </script>
</body>
</html>'''

app.run(debug=True)
