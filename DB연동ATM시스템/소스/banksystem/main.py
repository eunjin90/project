# 메뉴, 전체 흐름

# [파일 불러오기] 각 기능별로 분리한 전문 부품들을 가져옵니다.
import user         # 회원가입, 로그인을 담당하는 부품
import account      # 계좌 생성, 선택, 잔액 조회를 담당하는 부품
import banking      # 입금, 출금, 이체, 거래내역 조회를 담당하는 부품

# [상태 변수] 현재 누가 로그인했는지, 어떤 계좌를 쓰고 있는지 기억하는 저장소입니다.
login_user = None           # 처음에 아무도 로그인 안 했으므로 비어 있음(None)
selected_account = None     # 처음에 선택된 계좌가 없으므로 비어 있음(None)

# [전체 무한 루프] ATM 기기는 전원을 끄기 전까지 이 안에서 계속 돌아갑니다.
# 로그인 정보가 없을 때(None일 때) 실행됩니다.
while True:
    # ================= 1단계: 로그인 전 화면 =================
    if login_user is None:
        print("\n=========== [은행 ATM 메인화면] ===========")
        print(" 1. 회원가입 (실명 등록)")
        print(" 2. 로그인")
        print(" 3. 업무 종료")
        print("===========================================")

        menu = input("원하시는 업무의 번호를 입력해주세요: ")

        if menu == "1":
            user.register()     # user.py의 회원가입 함수 호출
        elif menu == "2":       # 로그인 성공 시 사용자 이름(user_id)을 받아와 login_user에 저장합니다.
            login_user = user.login()
            if login_user:
                selected_account = None  # 로그인이 막 되었을 땐 계좌 선택 전이므로 초기화
        elif menu == "3":
            print("\n[안내] ATM 기기 이용을 종료합니다. 감사합니다.")
            break               # while 루프를 깨고 프로그램을 완전히 종료합니다.
        else:   # 1, 2, 3 외의 다른 입력을 했을 때 처리
            print("\n[안내] 잘못된 입력입니다. 1~3 사이의 번호를 입력해주세요.")

    # ================= 2단계: 로그인 후 + 계좌 선택 전 화면 =================
    # 로그인은 되어있으나(`else`), 아직 계좌를 고르지 않았을 때 실행됩니다.
    else:
        # 계좌 선택 전 화면
        if selected_account is None:
            print(f"\n=========== [{login_user}님 환영합니다] ===========")
            print(" 1. 신규 계좌 개설")
            print(" 2. 보유 계좌 선택 (ATM 시작)")
            print(" 3. 로그아웃")
            print("===============================================")

            menu = input("원하시는 업무의 번호를 입력해주세요: ")

            if menu == "1":     # 새 계좌를 만들고, 만든 계좌번호를 바로 선택된 계좌로 저장합니다.
                selected_account = account.create_account(login_user)
            elif menu == "2":   # 본인의 계좌 목록을 보고 그중 하나를 골라 selected_account에 저장합니다.
                selected_account = account.select_account(login_user)
            elif menu == "3":   # 로그아웃 시 모든 정보를 초기화하여 '1단계(메인화면)'로 돌아가게 합니다.
                print(f"\n[안내] {login_user}님, 안전하게 로그아웃 되었습니다.")
                login_user = None
                selected_account = None
            else:               # 계좌를 선택했거나 로그아웃을 했으므로 다시 while문의 처음으로 올라가 상태를 체크합니다.
                print("\n[안내] 잘못된 입력입니다. 1~3 사이의 번호를 입력해주세요.")

            continue

        # ================= 3단계: 실제 ATM 업무 화면 =================
        # 로그인도 했고, 계좌도 선택되었을 때 비로소 금융 업무 메뉴가 나옵니다.
        print(f"\n=========== [{login_user}님의 ATM 메뉴] ===========")
        print(f" [선택된 계좌번호: {selected_account}]")
        print(" 1. 잔액 조회")
        print(" 2. 입금")
        print(" 3. 출금")
        print(" 4. 이체")
        print(" 5. 거래내역 조회")
        print(" 6. 다른 계좌로 변경")
        print(" 7. 로그아웃")
        print("===============================================")

        menu = input("원하시는 업무의 번호를 입력해주세요: ")

        if menu == "1":
            account.check_balance(selected_account)     # 현재 계좌의 잔액 확인
        elif menu == "2":
            banking.deposit(selected_account)           # 현재 계좌에 입금
        elif menu == "3":
            banking.withdraw(selected_account)          # 현재 계좌에서 출금
        elif menu == "4":
            banking.transfer(selected_account)          # 현재 계좌에서 타인 계좌로 이체
        elif menu == "5":
            banking.show_transactions(selected_account) # 현재 계좌의 거래 기록 조회
        elif menu == "6":
            new_account = account.select_account(login_user)    # 현재 로그인 상태는 유지하되, 업무를 볼 계좌번호만 다시 고릅니다.
            if new_account:
                selected_account = new_account
        elif menu == "7":       # 모든 세션을 종료하고 메인 메뉴로 나갑니다.
            print(f"\n[안내] {login_user}님, 안전하게 로그아웃 되었습니다. 카드를 챙겨주세요.")
            login_user = None
            selected_account = None
        else:                   # 1~7 외의 잘못된 번호 입력 시 에러 방지
            print("\n[안내] 잘못된 번호입니다. 1~7 사이의 메뉴를 선택해주세요.")