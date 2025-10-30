# SoongSil Univ. lms
 v2.0.0 (2024.04.18 released, 2025.10.30 updated.)
> v2.0.0 변경점.
>> + 공지사항, 과목 탭 추가
>> + 학식, GPT 탭 삭제
>> + 코드 가독성 부분 최적화 (일부 변수명 수정) 
>> + lms 자동 로그인 방식 request로 구현
>>> + (selenium 대비 6.3배 성능 향상)

Python request를 이용해 lms 자동로그인 + 공지사항, 과제, 영상 마감정보 가져오는 프로그램.

LearningX에서 영상 마감일은 나오지 않는 단점을 보완한 프로그램입니다.


[SSU_lms 사용법] 
  1. SSU_lms 폴더를 설치 합니다.
  2. 아래의 필수 의존성을 설치합니다.
      pip install pillow beautifulsoup4 requests cryptography
  3. 의존성이 설치된 Python 커널 환경에서 구동시킵니다.
<hr/>

__Copyrights 2024. Lee SangHwa All rights reserved.__
