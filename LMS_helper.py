import selenium
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://smartid.ssu.ac.kr/Symtra_sso/smln.asp?apiReturnUrl=https%3A%2F%2Flms.ssu.ac.kr%2Fxn-sso%2Fgw-cb.php"

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
#options=chrome_options

driver = webdriver.Chrome()
driver.get(URL)
user_id = driver.find_element(By.ID,'userid')
user_id.send_keys("id") #id(학번) 입력

user_pw = driver.find_element(By.ID, 'pwd')
user_pw.send_keys("pw") #비밀번호 입력
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
    print(menu_info[i],":",menu_num[i].text)

print("\n")

for i in range(len(assign)):
    print(assign[i].text,"\n")
