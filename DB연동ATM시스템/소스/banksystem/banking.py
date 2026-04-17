# 입금, 출금, 이체, 거래내역

# [데이터베이스 연결] 공통 통로인 db.py에서 연결 함수를 가져옵니다.
from db import get_connection

# [변환 함수] DB에 영어로 저장된 거래 타입을 사용자가 보기 편하게 한글로 바꿔줍니다.
def convert_tx_type(tx_type):
    mapping = {
        "DEPOSIT": "입금",
        "WITHDRAW": "출금",
        "TRANSFER": "이체"
    }
    return mapping.get(tx_type, tx_type)

# [입금 함수] 선택된 계좌에 돈을 넣습니다.
def deposit(account_id):
    if account_id is None:      # 계좌 선택 안 하고 들어오면 입구 컷
        print("\n[안내] 선택된 계좌가 없습니다. 계좌를 먼저 선택해주세요.")
        return

    amount_str = input("입금하실 금액을 입력해주세요: ")

    if not amount_str.isdigit():        # 숫자가 아니면 튕겨냄 (try-except 없이 if문으로 처리)
        print("\n[안내] 금액은 숫자로만 입력해주세요.")
        return

    amount = int(amount_str)    # 숫자로 변환
    if amount <= 0:
        print("\n[안내] 1원 이상부터 입금 가능합니다.")
        return

    conn = get_connection()     # 금고 문 열기
    cursor = conn.cursor()

    # 1. 내 계좌 잔액 늘리기 (UPDATE)
    cursor.execute(
        "UPDATE accounts SET balance = balance + :1 WHERE account_id=:2",
        (amount, account_id)
    )

    # 2. 거래 내역에 입금 기록 추가 (INSERT)
    # from_account_id가 NULL인 이유는 외부(ATM)에서 돈이 들어왔기 때문입니다.
    cursor.execute(
        "INSERT INTO transactions (tx_id, from_account_id, to_account_id, amount, tx_type) "
        "VALUES (tx_seq.NEXTVAL, NULL, :1, :2, 'DEPOSIT')",
        (account_id, amount)
    )

    conn.commit()   # 확정 도장
    cursor.close()
    conn.close()

    print(f"\n[안내] {amount:,}원이 정상적으로 입금되었습니다.")

# [출금 함수] 선택된 계좌에서 돈을 뺍니다.
def withdraw(account_id):
    if account_id is None:
        print("\n[안내] 선택된 계좌가 없습니다. 계좌를 먼저 선택해주세요.")
        return

    amount_str = input("출금하실 금액을 입력해주세요: ")

    if not amount_str.isdigit():
        print("\n[안내] 금액은 숫자로만 입력해주세요.")
        return

    amount = int(amount_str)
    if amount <= 0:
        print("\n[안내] 1원 이상부터 출금 가능합니다.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # 1. 잔액이 충분한지 먼저 확인 (SELECT)
    cursor.execute(
        "SELECT balance FROM accounts WHERE account_id=:1",
        (account_id,)
    )
    row = cursor.fetchone()

    if row is None:
        print("\n[안내] 계좌 정보를 찾을 수 없습니다.")
        cursor.close()
        conn.close()
        return

    if row[0] < amount:     # 가진 돈보다 많이 빼려고 할 때
        print(f"\n[안내] 잔액이 부족합니다. (출금 가능 금액: {row[0]:,}원)")
        cursor.close()
        conn.close()
        return

    # 2. 내 계좌 잔액 줄이기 (UPDATE)
    cursor.execute(
        "UPDATE accounts SET balance = balance - :1 WHERE account_id=:2",
        (amount, account_id)
    )

    # 3. 거래 내역에 출금 기록 추가 (INSERT)
    # to_account_id가 NULL인 이유는 내 주머니로 돈이 나갔기 때문입니다.
    cursor.execute(
        "INSERT INTO transactions (tx_id, from_account_id, to_account_id, amount, tx_type) "
        "VALUES (tx_seq.NEXTVAL, :1, NULL, :2, 'WITHDRAW')",
        (account_id, amount)
    )

    conn.commit()   # 확정
    cursor.close()
    conn.close()

    print(f"\n[안내] {amount:,}원이 정상적으로 출금되었습니다.")

# [이체 함수] 내 계좌에서 상대 계좌로 돈을 보냅니다.
def transfer(account_id):
    if account_id is None:
        print("\n[안내] 선택된 계좌가 없습니다. 계좌를 먼저 선택해주세요.")
        return

    to_account_str = input("이체받으실 분의 계좌번호를 입력해주세요: ")

    if not to_account_str.isdigit():
        print("\n[안내] 계좌번호는 숫자로만 입력해주세요.")
        return

    to_account = int(to_account_str)

    if to_account == account_id:    # 나한테 보내기 방지
        print("\n[안내] 본인의 현재 계좌로는 이체할 수 없습니다.")
        return

    amount_str = input("이체하실 금액을 입력해주세요: ")

    if not amount_str.isdigit():
        print("\n[안내] 금액은 숫자로만 입력해주세요.")
        return

    amount = int(amount_str)
    if amount <= 0:
        print("\n[안내] 1원 이상부터 이체 가능합니다.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # 1. 받는 사람 계좌가 진짜 있는지 확인 (SELECT)
    cursor.execute(
        "SELECT balance, user_id FROM accounts WHERE account_id=:1",
        (to_account,)
    )
    target = cursor.fetchone()

    if target is None:
        print("\n[안내] 입력하신 계좌번호가 존재하지 않습니다. 다시 확인해주세요.")
        cursor.close()
        conn.close()
        return

    target_user_name = target[1]    # 수취인 이름(user_id) 보관

    # 2. 내 잔액이 충분한지 확인 (SELECT)
    cursor.execute(
        "SELECT balance FROM accounts WHERE account_id=:1",
        (account_id,)
    )
    row = cursor.fetchone()

    if row is None:
        print("\n[안내] 본인의 계좌 정보를 찾을 수 없습니다.")
        cursor.close()
        conn.close()
        return

    if row[0] < amount:
        print(f"\n[안내] 잔액이 부족합니다. (이체 가능 금액: {row[0]:,}원)")
        cursor.close()
        conn.close()
        return

    # 3. 이체 진행 (내 돈 깎고 + 상대 돈 늘리고 + 영수증 쓰기)
    # 내 통장 차감 (UPDATE)
    cursor.execute(
        "UPDATE accounts SET balance = balance - :1 WHERE account_id=:2",
        (amount, account_id)
    )

    # 상대 통장 증액 (UPDATE)
    cursor.execute(
        "UPDATE accounts SET balance = balance + :1 WHERE account_id=:2",
        (amount, to_account)
    )

    # 거래 내역 기록 (INSERT)
    cursor.execute(
        "INSERT INTO transactions (tx_id, from_account_id, to_account_id, amount, tx_type) "
        "VALUES (tx_seq.NEXTVAL, :1, :2, :3, 'TRANSFER')",
        (account_id, to_account, amount)
    )

    conn.commit()   # 이 모든 과정이 완벽할 때만 한 번에 저장!
    cursor.close()
    conn.close()

    print(f"\n[안내] {target_user_name}님에게 {amount:,}원이 이체되었습니다.")

# [거래내역 조회] 내가 쓴 돈, 받은 돈 기록을 보여줍니다.
def show_transactions(account_id):
    if account_id is None:
        print("\n[안내] 선택된 계좌가 없습니다. 계좌를 먼저 선택해주세요.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    # 내가 보낸 계좌이거나(from), 내가 받은 계좌인(to) 기록을 최신순(DESC)으로 조회
    cursor.execute(
        """
        SELECT tx_type, from_account_id, to_account_id, amount, tx_date
        FROM transactions
        WHERE from_account_id = :1 OR to_account_id = :2
        ORDER BY tx_date DESC
        """,
        (account_id, account_id)
    )

    rows = cursor.fetchall()

    if not rows:
        print("\n[안내] 거래내역이 존재하지 않습니다.")
        cursor.close()
        conn.close()
        return

    print("\n========================= 거래 내역 =========================")
    print("  구분  |   출금계좌   |   입금계좌   |      금액      |     날짜")
    print("-------------------------------------------------------------")

    for r in rows:
        tx_type = convert_tx_type(r[0])         # 'DEPOSIT' -> '입금' 변환
        from_acc = r[1] if r[1] else "ATM"      # 보내는 계좌 없으면 입금임
        to_acc = r[2] if r[2] else "ATM"        # 받는 계좌 없으면 출금임
        amt = f"{r[3]:,}"                       # 금액 콤마 표시
        date = r[4].strftime("%Y-%m-%d %H:%M") if r[4] else ""      # 날짜 예쁘게 출력
        print(f" {tx_type:^4} | {str(from_acc):^10} | {str(to_acc):^10} | {amt:>12}원 | {date}")
    print("=============================================================")

    cursor.close()
    conn.close()