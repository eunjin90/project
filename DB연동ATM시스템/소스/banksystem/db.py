# DB 연결

import oracledb     # 파이썬과 오라클 DB를 연결해주는 통역사 같은 모듈입니다.

def get_connection():   # 은행 금고의 문을 여는 작업입니다. (아이디, 비밀번호, 주소 입력)
    conn = oracledb.connect(
        user="hr",                      # DB 아이디
        password="hr",                  # DB 비밀번호
        dsn="localhost:1521/free"       # DB가 있는 컴퓨터 주소
    )
    return conn         # 열린 금고문(연결 상태)을 다른 파일에서 쓸 수 있게 반환해줍니다.