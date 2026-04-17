# 계좌 관련 기능 (생성 / 조회 / 잔액확인)

from db import get_connection

def create_account(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    # accounts 테이블에 새 통장 만들기 (초기 잔액은 0원)
    # account_seq.NEXTVAL 은 DB가 알아서 '다음 계좌번호'를 1씩 올려서 만들어줌
    cursor.execute(
        "INSERT INTO accounts (account_id, user_id, balance) VALUES (account_seq.NEXTVAL, :1, 0)",
        (user_id,)
    )
    conn.commit()   # 확정

    # 방금 만들어진 내 계좌번호가 뭔지 DB한테 다시 물어보는 명령
    cursor.execute("SELECT account_seq.CURRVAL FROM dual")
    account_id = cursor.fetchone()[0]   # 결과에서 첫 번째 값을 뽑아냄

    cursor.close()
    conn.close()

    print(f"\n[안내] 신규 계좌가 개설되었습니다. (계좌번호: {account_id})")
    return account_id   # 만들어진 계좌번호를 메인에 알려줌

def select_account(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    # 지금 로그인한 사람(user_id)의 계좌만 전부 다(fetchall) 가져오라는 명령
    # 로그인한 사람의 이름으로만 조회 (타인 계좌 접근 차단)
    cursor.execute(
        "SELECT account_id, balance FROM accounts WHERE user_id=:1",
        (user_id,)
    )
    accounts = cursor.fetchall()    # fetchone()은 1개만, fetchall()은 전부 다 가져옴

    if not accounts:    # 통장이 하나도 없으면
        print("\n[안내] 등록된 계좌가 없습니다. 계좌를 먼저 개설해주세요.")
        cursor.close()
        conn.close()
        return None

    print(f"\n[{user_id}님의 보유 계좌 목록]")
    # enumerate는 목록을 1번, 2번, 3번... 순서대로 번호를 매겨서 보여주는 파이썬 기능
    for i, acc in enumerate(accounts, start=1):
        print(f" {i}. 계좌번호: {acc[0]} | 잔액: {acc[1]:,}원")

    choice_str = input("원하시는 계좌의 번호를 선택해주세요 (취소: 0): ")

    # 문자를 입력해서 튕기는 현상 방지
    if not choice_str.isdigit():    # 사용자가 실수로 문자(a, b, ㅋㅋ 등)를 쳤는지 확인
        print("\n[안내] 숫자만 입력해주세요.") 
        cursor.close()
        conn.close()
        return None

    choice = int(choice_str)    # 문자를 진짜 숫자로 변환

    if choice == 0:
        print("\n[안내] 계좌 선택을 취소했습니다.")
        cursor.close()
        conn.close()
        return None

    if choice < 1 or choice > len(accounts):
        print("\n[안내] 목록에 없는 번호입니다. 올바른 번호를 선택해주세요.")
        cursor.close()
        conn.close()
        return None

    # 사용자가 화면에 보이는 1번, 2번 중 하나를 고르면, 
    # 컴퓨터는 0번째, 1번째로 인식하므로 choice - 1 을 해서 진짜 계좌번호를 찾아냅니다.
    selected_account_id = accounts[choice - 1][0]
    print(f"\n[안내] [{selected_account_id}] 계좌가 선택되었습니다.")

    cursor.close()
    conn.close()

    return selected_account_id

def check_balance(account_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT balance FROM accounts WHERE account_id=:1",
        (account_id,)
    )
    result = cursor.fetchone()

    if result:
        print(f"\n[안내] 현재 남은 잔액은 {result[0]:,}원 입니다.")
    else:
        print("\n[안내] 계좌 정보를 찾을 수 없습니다.")

    cursor.close()
    conn.close()