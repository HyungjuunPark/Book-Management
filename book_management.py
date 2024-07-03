import pymysql
from modules import clear_screen, fill_str_with_space
import pandas as pd
from tabulate import tabulate

#도서정보 검색
def searchInfo(target):
    try:
        cmd = f"SELECT * FROM book_info WHERE title LIKE '%{target}%' OR author LIKE '%{target}%' OR publisher LIKE '%{target}%'"
        curs.execute(cmd)
        data = curs.fetchall()

        if data:
            print("\n검색 결과:")

            df = pd.DataFrame(data)
            df.columns = ['ISBN','제목','저자','출판년도','출판사']
            print(tabulate(df,headers='keys'))
            
            print(fill_str_with_space("", 110, '-'))
        else:
            print(f"검색 결과가 없습니다.")
    except Exception as e:
        print(f"도서 정보 검색 중 오류가 발생했습니다: {e}")

def searchBooks(target):
    try:
        cmd = f"SELECT * FROM books NATURAL JOIN book_info WHERE title LIKE '%{target}%' OR author LIKE '%{target}%' OR publisher LIKE '%{target}%' OR ISBN LIKE '%{target}%'"
        curs.execute(cmd)
        data = curs.fetchall()

        print("\n검색 결과:")

        df = pd.DataFrame(data)
        df.columns = ['ISBN','Book ID','borrow','제목','저자','출판년도','출판사']
        df = df[['Book ID','ISBN','제목','저자','출판년도','출판사']]
        print(tabulate(df,headers='keys'))
        
        print(fill_str_with_space("", 110, '-'))
    except Exception as e:
        print(f"도서 검색 중 오류가 발생했습니다: {e}")

# 도서를 추가합니다. 추가된 도서의 id를 리턴합니다. 만약 도서정보에 등록할 도서의 ISBN이 없으면 -1을 리턴합니다.
def addBooks(ISBN):
    try:
        # 항상 중복을 허용하므로 바로 books 테이블에 추가
        cmd_get_max_id = "SELECT MAX(book_ID) FROM books"
        curs.execute(cmd_get_max_id)
        data = curs.fetchall()

        if len(data) > 0 and data[0][0] is not None:
            book_ID = data[0][0] + 1
        else:
            book_ID = 0

        values = f"VALUES('{book_ID}','{ISBN}','0')"

        cmd_insert_into_books = "INSERT INTO books " + values
        curs.execute(cmd_insert_into_books)

        return book_ID
    except Exception as e:
        raise

# 도서정보를 추가합니다. 추가된 도서정보의 isbn을 리턴합니다. 이미 등록된 정보면 -1을 리턴합니다.
def addInfo(ISBN, title, author, year, publisher):
    cmd = f"select ISBN from book_info where ISBN = '{ISBN}'"
    curs.execute(cmd)
    data = curs.fetchall()

    if len(data) > 0 and data[0][0] is not None:
        return -1

    values = f"values('{ISBN}','{title}','{author}','{year}','{publisher}')"

    cmd = "insert into book_info " + values
    curs.execute(cmd)

    return ISBN

def remove_book_copy():
    try:
        # 검색 기능을 통해 도서 목록 표시
        target = input("삭제할 도서를 검색할 키워드를 입력하세요: ")
        searchBooks(target)

        # 도서 ID 선택
        book_id_to_remove = input("삭제할 도서의 Book ID를 입력하세요: ")

        # 선택한 도서 사본 삭제 여부 확인
        confirm = input(f"정말로 도서 사본(ID: {book_id_to_remove})을 삭제하시겠습니까? (y/n): ")
        if confirm.lower() == 'y':
            delete_cmd = f"DELETE FROM books WHERE book_ID = {book_id_to_remove}"
            curs.execute(delete_cmd)
            clear_screen()
            print(f"도서 사본(ID: {book_id_to_remove})가 성공적으로 삭제되었습니다.")
        else:
            clear_screen()
            print("도서 사본 삭제가 취소되었습니다.")

    except Exception as e:
        print(f"도서 사본 삭제 중 오류가 발생했습니다: {e}")

def remove_info():
    try:
        # 도서 정보 검색
        target = input("삭제할 도서 정보를 검색할 키워드를 입력하세요: ")
        searchInfo(target)

        # 도서 정보 삭제 여부 확인
        isbn_to_remove = input("삭제할 도서의 ISBN을 입력하세요: ")
        confirm = input(f"정말로 도서 정보(ISBN: {isbn_to_remove})를 삭제하시겠습니까? (y/n): ")
        if confirm.lower() == 'y':
            delete_cmd = f"DELETE FROM book_info WHERE ISBN = '{isbn_to_remove}'"
            curs.execute(delete_cmd)
            clear_screen()
            print(f"도서 정보(ISBN: {isbn_to_remove})가 성공적으로 삭제되었습니다.")
        else:
            clear_screen()
            print("도서 정보 삭제가 취소되었습니다.")

    except Exception as e:
        print(f"도서 정보 삭제 중 오류가 발생했습니다: {e}")


def display_book_list():
    try:
        # 모든 도서 정보 검색 
        cmd = "SELECT *,(SELECT COUNT(*) FROM books AS B WHERE B.ISBN = A.ISBN) AS book_count FROM book_info AS A" 
        
        curs.execute(cmd)
        data = curs.fetchall()
        # 도서 목록 출력
        print("\n전체 도서 목록:")

        df = pd.DataFrame(data)
        df.columns = ['ISBN','제목','저자','출판년도','출판사','소장권수']
        print(tabulate(df,headers='keys'))

        print(fill_str_with_space("", 110, '-'))
    except Exception as e:
        print(f"도서 목록을 가져오는 중 오류가 발생했습니다: {e}")

# 도서 관리 서비스 함수
def book_management_service(cur, conn):
    # 데이터베이스 연결 설정
    global curs
    curs = cur

    while True:
        print("도서관 관리>도서 관리\n")
        display_book_list()
        print("1. 도서 추가\t 2.도서 검색\t 3.도서 사본 삭제\t4.도서 정보 삭제\t 5.뒤로 가기")
        choice = input("원하는 도서 관리 서비스를 선택하세요: ")
        clear_screen()

        if choice == "1":
            print("도서관 관리>도서 관리>도서 추가\n")
            ISBN = input("도서의 ISBN을 입력하세요: ")
            try:
                result_books = addBooks(ISBN)
                print("이미 도서정보가 등록되어 도서만 추가합니다.")
            except Exception as e:
                title = input("도서의 제목을 입력하세요: ")
                author = input("도서의 저자를 입력하세요: ")
                year = input("도서의 출판년도를 입력하세요: ")
                publisher = input("도서의 출판사를 입력하세요: ")
                clear_screen()
                result_info = addInfo(ISBN, title, author, year, publisher)
                result_books = addBooks(ISBN)
                print("도서정보와 도서를 추가했습니다.")
            # commit 추가
            conn.commit()            
            
        elif choice == "2":
            print("도서관 관리>도서 관리>도서 검색\n")
            target = input("도서를 검색할 키워드를 입력하세요: ")
            clear_screen()
            result = searchInfo(target)
            if result is not None:
                for row in result:
                    print(row)

        elif choice == "3":
            print("도서관 관리>도서 관리>도서 사본 삭제\n")
            remove_book_copy()
            # commit 추가
            conn.commit()

        elif choice == "4":
            print("도서관 관리>도서 관리>도서 정보 삭제\n")
            remove_info()
            # commit 추가
            conn.commit()

        elif choice == "5":
            print("메인 메뉴로 돌아갑니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 선택하세요.")