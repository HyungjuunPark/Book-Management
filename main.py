# main.py
import member_management as mm
import book_management as bm
import book_loan as bl
from modules import clear_screen
import os
import pymysql

def main():  
    clear_screen()
    # MySQL 연결 설정
    conn = pymysql.connect(host='localhost', user='root', password='inose10731@', db='Library')
    curs = conn.cursor()

    while True:
                
        print("도서관 관리 시스템입니다\n")
        print("1. 회원 관리\n")
        print("2. 도서 관리\n")
        print("3. 도서 대출\n")
        print("4. 종료\n")

        choice = input("원하는 서비스를 선택하세요: ")
        clear_screen()
        if choice == "1":
            mm.member_management_service(curs, conn)
        elif choice == "2":
            bm.book_management_service(curs, conn)
        elif choice == "3":
            bl.book_loan_service(curs, conn)
        elif choice == "4":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 선택하세요.")

    # 연결 종료
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()