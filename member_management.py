# member_management.py
import pymysql
from modules import clear_screen, fill_str_with_space
import pandas as pd
from tabulate import tabulate

# 원하는 내용의 회원정보를 검색합니다.
def search_member(curs, target):
    cmd = f"SELECT * FROM member WHERE member_ID LIKE '{target}%' OR name LIKE '{target}%' OR addr LIKE '{target}%' OR tel LIKE '{target}%' OR birthday LIKE '{target}%'"
    curs.execute(cmd)
    data = curs.fetchall()
    return data

# add_member 함수 
def add_member(curs, name, addr, tel, birthday):
    try:
        # 회원 추가 쿼리 실행
        cmd = "INSERT INTO member (name, addr, tel, birthday) VALUES (%s, %s, %s, %s)"
        values = (name, addr, tel, birthday)
        curs.execute(cmd, values)

        # 추가된 회원의 ID 반환
        return curs.lastrowid  # 새로 추가된 회원의 ID를 반환

    except Exception as e:
        print(f"회원 추가 중 오류가 발생했습니다: {e}")
        raise  # 발생한 예외를 다시 던져서 호출 부분에서 예외를 처리할 수 있도록 함


#회원삭제 함수
def remove_member(curs):
    print("회원 삭제 서비스를 선택하셨습니다.")
    display_member_list(curs)
    print("\n")

    # 회원 검색 기능 호출
    target = input("삭제할 회원의 이름 또는 ID를 입력하세요: ")
    data = search_member(curs, target)

    if not data:
        print(f"해당 검색어를 포함하는 회원을 찾을 수 없습니다.")
    else:
        print("검색된 회원 정보:")
        for row in data:
            print(row)

        member_id = input("삭제할 회원의 ID를 입력하세요: ")
        choice = input("이 회원을 삭제하시겠습니까? (y/n): ")
        if choice.lower() == 'y':
            try:
                # 선택된 회원 삭제
                cmd_delete_member = f"DELETE FROM member WHERE member_ID = '{member_id}'"
                curs.execute(cmd_delete_member)

                clear_screen()
                print(f"ID가 {member_id}인 회원이 삭제되었습니다.")
            except Exception as e:
                print(f"회원 삭제 중 오류가 발생했습니다: {e}")
        elif choice.lower() == 'n':
            print("회원 삭제를 취소했습니다.")
        else:
            print("잘못된 입력입니다. 회원 삭제를 취소합니다.")

# Function to update a member
def update_member(curs):
    print("회원 수정 서비스를 선택하셨습니다.")
    
    display_member_list(curs)
    print("\n")

    # 회원 수정을 위한 ID 입력   
    target = input("수정할 회원의 이름 또는 ID를 입력하세요: ")
    data = search_member(curs, target)

    if not data:
        print(f"해당 검색어를 포함하는 회원을 찾을 수 없습니다.")
    else:
        print("검색된 회원 정보:")
        for row in data:
            print(row)
        member_id = input("수정할 회원의 ID를 입력하세요: ")

    # 사용자에게 어떤 정보를 수정할지 물어보기
    print("1. 이름 수정")
    print("2. 주소 수정")
    print("3. 전화번호 수정")
    print("4. 생년월일 수정")
    print("5. 뒤로 가기")
    choice = input("수정할 정보를 선택하세요 (1-5): ")
    clear_screen()
    # 사용자의 선택에 따라 정보 수정
    if choice == "1":
        new_value = input("새로운 이름을 입력하세요: ")
        column = "name"
    elif choice == "2":
        new_value = input("새로운 주소를 입력하세요: ")
        column = "addr"
    elif choice == "3":
        new_value = input("새로운 전화번호를 입력하세요: ")
        column = "tel"
    elif choice == "4":
        new_value = input("새로운 생년월일을 입력하세요: ")
        column = "birthday"
    elif choice == "5":
        print("회원 수정을 종료합니다.")
        return
    else:
        print("잘못된 선택입니다. 회원 수정을 종료합니다.")
        return

    # SQL 쿼리 실행하여 회원 정보 수정
    cmd = f"UPDATE member SET {column} = '{new_value}' WHERE member_ID = '{member_id}'"
    curs.execute(cmd)

    print(f"ID가 {member_id}인 회원의 {column}이(가) 수정되었습니다.")

    
def display_member_list(curs):
    try:
                # 모든 회원 정보 검색
        cmd = "SELECT * FROM member"
        curs.execute(cmd)
        data = curs.fetchall()
        # 회원 목록 출력
        print("\n전체 회원 목록:")

        df = pd.DataFrame(data)
        df.columns = ['ID','이름','주소','전화번호','생년월일']
        print(tabulate(df,headers='keys'))
        
        print(fill_str_with_space("", 90, '-'))
    except Exception as e:
        print(f"회원 목록을 가져오는 중 오류가 발생했습니다: {e}")

            
# Function for member management service
def member_management_service(curs,conn):    
    while True:
        print("도서관 관리>회원관리\n")
        display_member_list(curs)
        print("1. 회원 추가\t 2.회원 수정\t 3.회원 삭제\t 4.뒤로가기\n")
        
        choice = input("원하는 회원 관리 서비스를 선택하세요: ")
        clear_screen()

        # UI 단에서의 코드 수정
        if choice == "1":
            print("도서관 관리>회원 관리>회원 추가\n")
            name = input('성함을 입력하세요.')
            addr = input('도로명 주소를 입력하세요.')
            tel = input('휴대전화번호를 입력하세요')
            birthday = input('생년월일을 입력하세요')

            try:
                # add_member 함수 호출
                result_member = add_member(curs, name, addr, tel, birthday)
                clear_screen()
                if result_member is not None:
                    print(f"회원이 추가되었습니다. 회원 ID: {result_member}")
                    conn.commit()
                else:
                    print("회원 추가에 실패했습니다.")

            except Exception as e:
                print(f"오류가 발생했습니다: {e}")


        elif choice == "2":
            print("도서관 관리>회원 관리>회원 수정\n")
            update_member(curs)
            conn.commit()
        
        elif choice == "3":
            print("도서관 관리> 회원 관리> 회원 삭제\n")
            remove_member(curs)
            conn.commit()

        elif choice == "4":
            print("메인 메뉴로 돌아갑니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 선택하세요.")
