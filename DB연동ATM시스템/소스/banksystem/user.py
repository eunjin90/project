# 회원가입, 로그인

from db import get_connection   # db.py에서 금고 연결 함수를 가져옵니다.

# 이름이 규칙(한글 2~5자)에 맞는지 검사하는 함수
def is_valid_name(name):
    if not name: return False   # 아무것도 안 적었으면 통과 안 됨
    if len(name) < 2 or len(name) > 5: return False # 길이가 안 맞으면 통과 안 됨 2~5글자까지
    for char in name:
        if not ('가' <= char <= '힣'):  # 한글이 아니면 통과 안 됨
            return False
    return True     # 모든 조건을 통과하면 진짜 이름으로 인정!

def register():
    conn = get_connection() # 금고 문 열기
    cursor = conn.cursor()  # 결재 서류 준비 (DB에 명령을 내릴 준비)

    while True: # 올바른 이름을 입력할 때까지 계속 반복(무한 루프)
        user_id = input("가입자 성함 (실명 입력, 예: 이은진): ")

        # 이름 검증 통과 못 하면 안내 후 다시 입력
        if not is_valid_name(user_id):
            print("\n[안내] 이름은 2~5자의 한글로만 입력해주세요.")
            continue    # 아래 코드를 무시하고 다시 처음(input)으로 돌아감

        # DB에서 이 이름이 이미 있는지 찾아보라는 명령
        cursor.execute(
            "SELECT user_id FROM users WHERE user_id = :1",
            (user_id,)
        )
        result = cursor.fetchone()  # 검색 결과 딱 1개만 가져오기

        if result:  # 결과가 있다는 건 이미 가입된 사람이라는 뜻
            print("\n[안내] 이미 가입된 이름입니다. 다른 이름을 입력해주세요.")
            continue    # 다시 처음으로 돌아감
        break   # 중복이 아니면 무한 루프 탈출

    password = input("사용할 비밀번호: ")

    # DB의 users 테이블에 새 회원 정보를 저장하라는 명령 (INSERT)
    cursor.execute(
        "INSERT INTO users (user_id, password) VALUES (:1, :2)",
        (user_id, password)
    )
    conn.commit()   # 진짜 DB에 저장됨

    print(f"\n[안내] {user_id}님, 성공적으로 회원가입이 완료되었습니다.")

    # 작업이 끝났으니 서류철 닫고, 금고 문도 닫음 (메모리 절약)
    cursor.close()
    conn.close()

def login():
    conn = get_connection()
    cursor = conn.cursor()

    user_id = input("이름: ")
    password = input("비밀번호: ")

    # DB에서 이름과 비밀번호가 모두 일치하는 사람이 있는지 검색 (SELECT)
    cursor.execute(
        "SELECT * FROM users WHERE user_id=:1 AND password=:2",
        (user_id, password)
    )

    result = cursor.fetchone()  # 결과 가져오기

    cursor.close()
    conn.close()

    if result:  # 결과가 있으면 (정보가 일치하면)
        print(f"\n[안내] {user_id}님, 환영합니다.")
        return user_id
    else:   # 결과가 없으면 (틀렸으면)
        print("\n[안내] 이름 또는 비밀번호가 일치하지 않습니다.")
        return None # 로그인 실패