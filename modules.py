# clear_screen_module.py
import os
import unicodedata

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
#왼쪽 칸수 맞춰 채우기
def lpad(i, width, fillchar='0'):
    return str(i).rjust(width,fillchar)
#오른쪽 칸수 맞춰 채우기
def rpad(i, width, fillchar='0'):
    return str(i).ljust(width,fillchar)

#한글과 영어의 크기가 다른 문제를 해결
def fill_str_with_space(input_s="", max_size=60, fill_char="*"):
    # """
    # - 길이가 긴 문자는 2칸으로 체크하고, 짧으면 1칸으로 체크함. 
    # - 최대 길이(max_size)는 40이며, input_s의 실제 길이가 이보다 짧으면 
    # 남은 문자를 fill_char로 채운다.
    # """
    l = 0 
    for c in input_s:
        if unicodedata.east_asian_width(c) in ['F', 'W']:
            l+=2
        else: 
            l+=1
    return input_s+fill_char*(max_size-l)
