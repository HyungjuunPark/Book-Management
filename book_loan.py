import pymysql
from member_management import display_member_list
from modules import clear_screen, fill_str_with_space
import datetime
from datetime import timedelta
import unicodedata
import pandas as pd
from tabulate import tabulate

def borrow_book(curs, book_ID, member_ID):
    try:
        book_ID = int(book_ID)
        member_ID = int(member_ID)
        
        today = datetime.datetime.now().date()

        # 도서가 이미 대출 중인지 확인
        cmd_check_borrow = f"SELECT borrow FROM books WHERE book_ID = '{book_ID}'"
        curs.execute(cmd_check_borrow)
        data = curs.fetchall()

        if data and data[0][0] == 1:
            return 1  # 이미 대출 중이면 1을 반환

        # 도서 예약 정보 확인
        cmd_check_reservation = f"SELECT member_ID, r_date FROM reservation WHERE book_ID = '{book_ID}' ORDER BY r_date LIMIT 1"
        curs.execute(cmd_check_reservation)
        reservation_data = curs.fetchone()

        if reservation_data:
            reserved_member_ID, r_date = reservation_data
            r_date = datetime.datetime.combine(r_date, datetime.datetime.min.time()).date()

            # MySQL의 DATEDIFF 함수를 사용하여 날짜 차이 계산
            date_diff = (today - r_date).days

            if reserved_member_ID == member_ID and date_diff >= 0:

                # 예약자가 맞고 예약 기간이 지났다면 예약 삭제
                cmd_delete_reservation = f"DELETE FROM reservation WHERE book_ID = '{book_ID}' AND member_ID = '{member_ID}'"
                curs.execute(cmd_delete_reservation)

                # 대출로 변경
                cmd_update_borrow = f"UPDATE books SET borrow = 1 WHERE book_ID = '{book_ID}'"
                curs.execute(cmd_update_borrow)

                # 대출 기록 추가
                cmd_insert_borrow = f"INSERT INTO borrows (book_ID, member_ID, b_date, due_date) VALUES ('{book_ID}', '{member_ID}', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 14 DAY))"
                curs.execute(cmd_insert_borrow)                
               
                return 0  # 성공적으로 대출되면 0을 반환
            else:
                return 2

        else:
            # 예약이 없는 경우에도 대출로 변경
            cmd_update_borrow = f"UPDATE books SET borrow = 1 WHERE book_ID = '{book_ID}'"
            curs.execute(cmd_update_borrow)

            # 대출 기록 추가
            cmd_insert_borrow = f"INSERT INTO borrows (book_ID, member_ID, b_date, due_date) VALUES ('{book_ID}', '{member_ID}', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 14 DAY))"
            curs.execute(cmd_insert_borrow)

            return 0  # 성공적으로 대출되면 0을 반환

    except Exception as e:
        raise


def extension_loan(curs, book_ID):
    try:
        cmd = f"select extend from borrows where book_ID = '{book_ID}'"
        curs.execute(cmd)
        data = curs.fetchall()

        if not data or data[0][0] == 1:
            return -1

        cmd = f"select date_add(due_date, interval 7 day) from borrows where book_ID = '{book_ID}'"
        curs.execute(cmd)
        data = curs.fetchall()

        if not data or not data[0][0]:
            return -2

        ex_date = data[0][0]

        cmd = f"select r_date < '{ex_date}' from reservation where book_ID= '{book_ID}'"
        curs.execute(cmd)
        data = curs.fetchall()

        if data and data[0][0] == 1:
            return -3

        cmd = f"update borrows set due_date = '{ex_date}', extend = 1 where book_ID = '{book_ID}'"
        curs.execute(cmd)
                
        return ex_date
    except Exception as e:
        raise
    
    

def return_book(curs, book_ID):
    try:
        cmd = f"update books set borrow = '0' where book_ID = '{book_ID}'"
        curs.execute(cmd)

        cmd = f"select if(curdate() > due_date, datediff(curdate(), due_date), 0) from borrows where book_ID = '{book_ID}'"
        curs.execute(cmd)
        data = curs.fetchall()

        cmd = f"delete from borrows where book_ID = '{book_ID}'"
        curs.execute(cmd)

        overdue_days = data[0][0]
        if overdue_days > 0:
            print(f"도서 반납이 성공적으로 완료되었습니다. 연체료 {overdue_days}일이 부과되었습니다.")
        else:
            print("도서 반납이 성공적으로 완료되었습니다.")
    except Exception as e:
        raise



def reservation_book(curs, book_ID, member_ID, custom_r_date=None):
    try:
        while True:
            if custom_r_date:
                r_date = custom_r_date
            else:
                # Use today's date without time
                r_date = input("Enter the reservation date (YYYY-MM-DD): ")
            try:
                # 입력받은 날짜가 유효한지 체크
                datetime.datetime.strptime(r_date, "%Y-%m-%d")
                break
            except ValueError:
                print("올바른 날짜 형식이 아닙니다. 다시 입력하세요.")

        cmd = f"select r_date from reservation where book_ID = '{book_ID}'"
        curs.execute(cmd)
        data = curs.fetchall()

        # 예약 정보가 없을 경우
        if not data:
            values = f"('{book_ID}', '{member_ID}', '{r_date}')"
            cmd = "INSERT INTO reservation (book_ID, member_ID, r_date) VALUES " + values
            curs.execute(cmd)

            cmd = f"select r_date from reservation where book_ID = '{book_ID}'"
            curs.execute(cmd)
            data = curs.fetchall()

            print("도서 예약이 성공적으로 완료되었습니다.")
            return data[0][0]
        else:
            print("이미 예약된 도서입니다.")
            return -1
    except Exception as e:
        print(f"예약 중 오류가 발생했습니다: {e}")
        return -1

def fill_str_with_space(input_s="", max_size=60, fill_char="*"):
    l = 0 
    for c in input_s:
        if unicodedata.east_asian_width(c) in ['F', 'W']:
            l += 2
        else: 
            l += 1
    return input_s + fill_char * (max_size - l)

def display_books_table(curs):
    try:
        # 도서 목록 조회
        cmd = "SELECT * FROM books natural join book_info"
        curs.execute(cmd)
        data = curs.fetchall()

        # 도서 목록 출력
        print("\n도서 목록:")

        df = pd.DataFrame(data)
        df.columns = ['ISBN', 'book_ID', '대출 상태','제목','저자','출판년도','출판사']
        df = df[['book_ID','ISBN','제목','저자','출판년도','출판사','대출 상태']]
        df['대출 상태'] = ['대출 중' if df['대출 상태'][i] == 1 else '대출 가능' for i in range(len(df))]
        print(tabulate(df,headers='keys'))
        
        print(fill_str_with_space("", 110, '-'))
    except Exception as e:
        print(f"도서 목록을 가져오는 중 오류가 발생했습니다: {e}")

def book_loan_service(curs, conn):

    while True:
        print("도서관 관리>도서 대출")
        display_books_table(curs)
        print("1. 도서 대출\t 2.도서 반납\t 3.대출 연장 \t 4.대출 예약\t 5. 뒤로가기")

        choice = input("원하는 도서 관리 서비스를 선택하세요: ")
        clear_screen()

        if choice == "1":
            print("도서관 관리>도서 대출>도서 대출")            
            display_member_list(curs)
            print("\n")
            display_books_table(curs)
            print("\n")
            book_ID = input("대출할 도서의 ID를 입력하세요: ")
            member_ID = input("대출할 회원의 ID를 입력하세요: ")            
            try:
                result = borrow_book(curs, book_ID, member_ID)

                if result == 1:
                    print("이미 대출 중인 도서입니다.")
                elif result == 2:
                    print("예약자가 아니거나 예약 기간이 아닙니다.")
                else:
                    print("도서가 성공적으로 대출되었습니다.")
                    conn.commit()  # 변경사항을 커밋
            except Exception as e:
                print(f"에러 발생: {e}")
                conn.rollback()  # 예외 발생 시 롤백


        elif choice == "2":
            print("도서관 관리>도서 대출>도서 반납")
            book_ID = input("반납할 도서의 ID를 입력하세요: ")
            try:
                return_book(curs, book_ID)
                conn.commit()
            except Exception as e:
                print(f"도서 반납 중 오류가 발생했습니다: {e}")

        elif choice == "3":
            print("도서관 관리>도서 대출>대출 연장")
            book_ID = input("연장할 도서의 ID를 입력하세요: ")            
            try:
                result = extension_loan(curs, book_ID)
                if result == -1:
                    print("이미 연장된 도서거나 연장이 불가능한 도서입니다.")
                elif result == -2:
                    print("연장 기간을 설정하는 중 오류가 발생했습니다.")
                elif result == -3:
                    print("도서 예약 중인 도서는 연장할 수 없습니다.")
                else:
                    print(f"도서 연장이 성공적으로 완료되었습니다. 새로운 반납일은 {result}입니다.")
                    conn.commit()
            except Exception as e:
                print(f"도서 연장 중 오류가 발생했습니다: {e}")

        elif choice == "4":
            print("도서관 관리>도서 대출>대출 예약")
            display_books_table(curs)
            print("\n")
            display_member_list(curs)
            print("\n")
            book_ID = input("예약할 도서의 ID를 입력하세요: ")
            member_ID = input("예약할 회원의 ID를 입력하세요: ")

            result = reservation_book(curs, book_ID, member_ID)
            if result != -1:
                conn.commit()

        elif choice == "5":
            print("메인 메뉴로 돌아갑니다.")
            break
        
        else:
            print("잘못된 선택입니다. 다시 선택하세요.")
