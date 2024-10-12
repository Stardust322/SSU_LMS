document.addEventListener('DOMContentLoaded', function() {
  // tasks배열을 server.py에서 동적으로 변경          
  const tasks = [
        "과제 1", "과제 2", "과제 3", "과제 4", "과제 5",
        "과제 6", "과제 7", "과제 8", "과제 9", "과제 10",
        "과제 11", "과제 12", "과제 13", "과제 14"];
            
  // tasks_day배열을 server.py에서 동적으로 변경 
  const tasks_day = [
                'red', 'yellow', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 
                'none', 'none', 'green', 'black completed'
            ];
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

                    // 체크박스 내용을 저장장
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

            // 중요한 과제 체크 여부
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
                    fireworksLaunched = true; // 최초 성공에만 축하 설정
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
        
                function animate() {
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
        
                animate();
            }
        
            // 로딩 화면 처리 (출처 : https://mong-blog.tistory.com/entry/%EB%A1%9C%EB%94%A9-%ED%99%94%EB%A9%B4-%EB%A7%8C%EB%93%A4%EA%B8%B0-with-css)
            setTimeout(function() {
                document.querySelector('.loading').style.display = 'none';
                document.querySelector('.content').style.display = 'block';
                renderTasks();
            }, 2000); // 2초 후에 로딩 화면을 숨기고 실제 콘텐츠를 보여줌
        });
      window.addEventListener('load', function() {
        localStorage.clear();
        renderTasks();
        });
