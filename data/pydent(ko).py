# coding:UTF-8
from __future__ import print_function, unicode_literals, division, absolute_import
import sys
import io
import re
import os
import textwrap
from Npp import *

G_CURRENT_BUFFER_ID = notepad.getCurrentBufferID()

# 'use strict';

# let g_description_en = "";
# let g_description_ko = "";

# let g_config; # [g]lobal [config]uration
# let g_var  ; # [g]lobal [var]iables

class PydentVariables(object):
    def __init__(self):
        self.refresh()        
    def refresh(self):
        self.stripped = ""; # [s]tripped [t]ext
        self.lev = 0;  # [lev]el
        self.sio = io.StringIO(); # [S]tring[IO]
        self.text = "";
        self.inside_triple_singles = False;
        self.inside_triple_doubles = False;
        self.indent_off = False


class PydentConfig (object):
    def __init__(self):
        self.refresh()
    def refresh(self):
        self.tabsize = 4
        self.indent = ' '* self.tabsize
        self.auto_unindent = True
        self.indent_comment = True
        self.dedent_end_tag = True

#end class

g_config = PydentConfig()
g_var = PydentVariables()

#indent-off
g_description = textwrap.dedent('''
    - 파이썬 코드의 들여쓰기를 고치는 프로그램.
    -
    - 쌍점(:)으로 끝나는 실행문 뒤에서 들여쓰기 수준을
    - 한 단계 늘림
    -
    - 코드 안에 다음 특별 주석을 넣어 주세요:
    -
    - #TABSIZE 4
    -     들여쓰기 수준 당 빈칸 수. (기본값은 4)
    - #END
    -     들여쓰기 수준을 한 단계 줄임
    - #END if while for
    -     들여쓰기 수준을 3 단계 줄임
    -     (3 은  #END 뒤의 단어 개수)
    - #END 2
    -     들여쓰기 수준을 2 단계 줄임
    - #INDENT 0
    -     들여 쓰기 수준을 0으로 함
    - #INDENT @+3
    -     들여쓰기 수준을 3 단계 늘림
    - #INDENT @-3
    -     들여쓰기 수준을 3 단계 줄임
    - #AUTO-UNINDENT ON
    - #AUTO-UNINDENT-ON
    -     'elif', 'else', 'except' 및 'case' 문을 자동으로 내어쓰기 함. (기본값)
    - #AUTO-UNINDENT OFF (폐기 예정)
    - #AUTO-UNINDENT-OFF (폐기 예정)
    -     AUTO-UNINDENT 를 끔
    - #INDENT OFF
    - #INDENT-OFF
    -     이 줄 부터 들여쓰기를 고치지 않음.
    - #INDENT ON
    - #INDENT-ON
    -     이 줄 다음부터 들여쓰기 고치기를 다시 시작함
    - #INDENT-COMMENT OFF
    - #INDENT-COMMENT-OFF
    -     주석 줄을 들여쓰지 않음
    - #INDENT-COMMENT ON
    - #INDENT-COMMENT-ON
    -     주석 줄을 들여 씀 (기본값임)
    - #DEDENT-END-TAG ON
    - #DEDENT-END-TAG-ON
    -     #END 태그 줄 내어쓰기 (기본값임)
    - #DEDENT-END-TAG OFF
    - #DEDENT-END-TAG-OFF
    -     #END 태그 줄 내어쓰지 않기
    ''')
#indent-on

def dlgstr(pystr):
    if sys.version_info.major < 3:
        return pystr.encode('mbcs')
    else:
        return pystr+""
#end if def

def pystr(dlgstr):
    if sys.version_info.major < 3:
        return dlgstr.decode('mbcs')
    else:
        return dlgstr+""
#end if def

def getPyEncodingName(bufferid=None):
    #indent-off
    name_to_encoding = {
        'ENC8BIT':'mbcs', #ANSI
        'COOKIE':'utf_8', # UTF-8
        'UTF8': 'utf_8_sig', # UTF-8-BOM
        'UCS2BE': 'utf_16_be', # UCS2-BE BOM
        'UCS2LE': 'utf_16_le', # UCS2-LE BOM
    }
    #indent-on
    if bufferid==None:
        bufferid = notepad.getCurrentBufferID()
    #end if
    return name_to_encoding[notepad.getEncoding(bufferid).name]
#end def

def getEOLstr(bufferid=None):
    if bufferid == None:
        bufferid = notepad.getCurrentBufferID()
    #end if
    EolFormat = str(notepad.getFormatType(bufferid))
    if EolFormat == "WIN":
        EolStr="\r\n"
    elif EolFormat == "UNIX":
        EolStr="\n"
    elif EolFormat == "MAC":
        EolStr="\r"
    else:
        EolStr="\r\n"
    #end if
    return EolStr
#end def

def getSelectedText(bufferid=None):
    if bufferid == None:
        bufferid = notepad.getCurrentBufferID()
    #end if
    if editor.getSelectionEmpty():
        text=editor.getText()
    else:
        text=editor.getSelText()
    #end if
    if sys.version_info.major < 3:
        text = text.decode(getPyEncodingName(bufferid))
    #end if
    text = text.replace(getEOLstr(bufferid), "\n")
    return text
#end def

def setSelectedText(text, bufferid=None):
    if bufferid == None:
        bufferid = notepad.getCurrentBufferID()
    #end if
    text = text.replace("\r\n","\n")
    text = text.replace("\r","\n")
    text = text.replace("\n",getEOLstr(bufferid))

    if sys.version_info.major < 3:
        text = text.encode(getPyEncodingName(bufferid))
    #end if
    if editor.getSelectionEmpty():
        editor.setText(text)
    else:
        editor.replaceSel(text)
#end if def

def npPrompt(prompt, title, defaultText=""):
    ret = notepad.prompt(dlgstr(prompt),dlgstr(title), dlgstr(defaultText))
    if ret != None:
        ret = pystr(ret)
    #end if
    return ret
#end def

def npMessageBox(message, title="Notepad++ 용 파이썬 스크립트", flags=0):
    retflag = notepad.messageBox(dlgstr(message), dlgstr(title), flags)
    return retflag
#end def

def CheckVerAndCoding(bufferid=None,lang="ko"):
    if bufferid == None:
        bufferid = notepad.getCurrentBufferID()
    #end if
    #indent-off
    if all((
        sys.version_info.major >= 3,
        getPyEncodingName(bufferid) != 'utf_8',
        getPyEncodingName(bufferid) != 'utf_8_sig'
        )):
        prompt = "Error"
        message = '\r\n'.join([
            "현재로서는 Python3 용 PythonScript 플러그인은 UTF-8으로 인코딩된 문서에서만 작동함.",
            "",
            "종료 하기"])
        title = 'pydent.py2py3.py Error'
        notepad.prompt(prompt,title, message)
        return False
    else:
        return True
    #end if
    #indent-on
#end def

def check_if_auto_words(st): # [s]tripped [t]ext
    #indent-off
    if (g_config.auto_unindent==True):
        for x in ['else:', 'else :', 'elif ', 'elif(',
                  'except ','except:', 'except :', 'finally:', 'finally :',
                  'case (', 'case(', 'case ' # Python 3.10 match case
            ]:
            if st.startswith(x):
                return True
    #end if for if
    #indent-on
    return False
#end def

def check_if_two_level_word_beginning(st): # [s]tripped [t]ext
    for x in ['match (', 'match(', 'match ']:
        if  st.startswith(x):
            return True
    #end for if
    return False
#end def

def check_if_end_of_two_level_word(wrd):
    for x in ['match']:
        if wrd == x:
            return  True;
    #end for if
    return False
#end def

def handle_end():
    #indent-off
    if g_var.stripped.upper().startswith("#END") :
        if(len(g_var.stripped)>len("#END")):
            commentpos=g_var.stripped.find('#',len("#END"))
            if -1 !=commentpos:
                g_var.stripped=g_var.stripped[:commentpos]
        #end if if
        wa=g_var.stripped.split(' ')
    else:
        if(len(g_var.stripped)>len("# END")):
            commentpos=g_var.stripped.find('#',len("# END"))
            if -1 !=commentpos:
                g_var.stripped=g_var.stripped[:commentpos]
        #end if if
        stx = "#END " + g_var.stripped[len("# END"):]
        wa=stx.split(' ')
    #end if
    #indent-on

    while '' in wa:
        wa.remove('')
    #end while
    if len(wa)==1:
        g_var.lev-=1
        g_var.lev = max(0,g_var.lev)
    else:
        if wa[1].isdigit():
            g_var.lev -= int(wa[1])
            g_var.lev = max(0,g_var.lev)
        else:
            g_var.lev -= len(wa) -1
            for i in range(len(wa)):
                if check_if_end_of_two_level_word(wa[i]):
                    g_var.lev -= 1
            #end if for
            g_var.lev = max(0,g_var.lev)
    #end if if
    print(g_config.indent*(g_var.lev+ 1*(g_config.dedent_end_tag!=True)), g_var.text.strip(),file=g_var.sio,sep='')
#end def

def handle_indent():
    #indent-off
    if g_var.stripped.upper().startswith("#INDENT"):
        wa=g_var.stripped.split(' ')
    else:
        stx= "#INDENT" + g_var.stripped[len("# INDENT"):]
        wa=stx.split(' ')
    #end if
    #indent-on
    if len(wa)<2:
        print(g_config.indent*g_var.lev, g_var.text.strip(),file=g_var.sio,sep='')
    else:
        ag_sLevel=wa[1]
        if ag_sLevel.isdigit():
            g_var.lev = int(ag_sLevel)
            g_var.lev = max(0,g_var.lev)
            print(g_config.indent*g_var.lev, g_var.stripped,file=g_var.sio,sep='')
        else:
            if len(ag_sLevel)>=2 and ag_sLevel[0]=='@':
                try:
                    delta = int(ag_sLevel[1:])
                except ValueError:
                    delta = 0
                #end try
                g_var.lev += delta
                g_var.lev = max(0,g_var.lev)
            #end if
            print(g_config.indent*g_var.lev, g_var.text.strip(),file=g_var.sio,sep='')
    #end if if
#end def

def handle_multiline_starter():
    rstripped = g_var.text.rstrip()
    lQuotes = rstripped.find("'''")
    if lQuotes != -1:
        rQuotes = -1
        if lQuotes + 3 <= len(rstripped) -1:
            rQuotes = g_var.text.rstrip().find("'''",lQuotes+3)
        #end if
        if rQuotes == -1:
            g_var.inside_triple_singles = True
        #end if
    else:
        lQuotes = g_var.text.find('"""')
        if lQuotes != -1:
            rQuotes = -1
            if lQuotes + 3 <= len(g_var.text.rstrip('\n')) -1:
                rQuotes = g_var.text.find('"""',lQuotes+3)
            #end if
            if rQuotes == -1:
                g_var.inside_triple_doubles = True
    #end if if if
#end def

def indent_pycode(code):
    g_config.refresh()
    g_var.refresh()

    code=code.split('\n')

    for g_var.text in code:
        g_var.stripped = g_var.text.strip()
        if g_var.stripped=='':
            print('\n',file=g_var.sio,sep='', end='')
            continue
        #end if

        if g_var.indent_off==True:
            #indent-off
            if (
                g_var.stripped.upper()=='#INDENT-ON'
                or g_var.stripped.upper()=='# INDENT-ON'
                or g_var.stripped.upper()=='#INDENT ON'
                or g_var.stripped.upper()=='# INDENT ON'
                ):
                g_var.indent_off=False
            else:
                pass
            #end if
            #indent-on
            print(g_var.text.rstrip(),file=g_var.sio,sep='')
            continue
        #end if

        if g_var.inside_triple_singles == True:
            print(g_var.text.rstrip(),file=g_var.sio,sep='')
            if g_var.text.rstrip().endswith("'''"):
                g_var.inside_triple_singles = False
            #end if
            continue
        #end if

        if g_var.inside_triple_doubles == True:
            print(g_var.text.rstrip(),file=g_var.sio,sep='')
            if g_var.text.rstrip().endswith('"""'):
                g_var.inside_triple_doubles = False
            #end if
            continue
        #end if

        #indent-off
        if (
            g_var.stripped.upper()=='#INDENT-OFF'
            or g_var.stripped.upper()=='# INDENT-OFF'
            or g_var.stripped.upper()=='#INDENT OFF'
            or g_var.stripped.upper()=='# INDENT OFF'
            ):
            g_var.indent_off=True
            print(g_var.text.rstrip(),file=g_var.sio,sep='')
            continue
        #indent-on

        #indent-off
        if g_var.stripped.upper()[:9] in ['#TABSIZE ', '#TABSIZE\t']:
            try:
                g_config.tabsize = int(g_var.stripped[9:])
            except:
                g_config.tabsize = 4
            finally:
                g_config.indent = ' ' * g_config.tabsize
            #end try
            print(g_var.text.rstrip(),file=g_var.sio,sep='')
            continue
        #end if
        #indent-on

        #indent-off
        if (
            g_var.stripped.upper()=='#AUTO-UNINDENT OFF'
            or g_var.stripped.upper()=='# AUTO-UNINDENT OFF'
            or g_var.stripped.upper()=='#AUTO-UNINDENT-OFF'
            or g_var.stripped.upper()=='# AUTO-UNINDENT-OFF'
            ):
            g_config.auto_unindent=False
            print(g_var.text.rstrip(),file=g_var.sio,sep='')
        elif (
            g_var.stripped.upper()=='#AUTO-UNINDENT ON'
            or g_var.stripped.upper()=='# AUTO-UNINDENT ON'
            or g_var.stripped.upper()=='#AUTO-UNINDENT-ON'
            or g_var.stripped.upper()=='# AUTO-UNINDENT-ON'
            ):
            g_config.auto_unindent=True
            print(g_var.text.rstrip(),file=g_var.sio,sep='')
        elif (
            g_var.stripped.upper()=='#INDENT-COMMENT-OFF'
            or g_var.stripped.upper()=='# INDENT-COMMENT-OFF'
            or g_var.stripped.upper()=='#INDENT-COMMENT OFF'
            or g_var.stripped.upper()=='# INDENT-COMMENT OFF'
            ):
            g_config.indent_comment=False
            print(g_var.text.rstrip(),file=g_var.sio,sep='')
        elif (
            g_var.stripped.upper()=='#INDENT-COMMENT-ON'
            or g_var.stripped.upper()=='# INDENT-COMMENT-ON'
            or g_var.stripped.upper()=='#INDENT-COMMENT ON'
            or g_var.stripped.upper()=='# INDENT-COMMENT ON'
            ):
            g_config.indent_comment=True
            print(g_var.text.rstrip(),file=g_var.sio,sep='')
        elif (
            g_var.stripped.upper()=='#DEDENT-END-TAG ON'
            or g_var.stripped.upper()=='# DEDENT-END-TAG-ON'
            or g_var.stripped.upper()=='#DEDENT-END-TAG ON'
            or g_var.stripped.upper()=='# DEDENT-END-TAG ON'
            ):
            g_config.dedent_end_tag=True
            print(g_var.text.rstrip(),file=g_var.sio,sep='')
        elif (
            g_var.stripped.upper()=='#DEDENT-END-TAG OFF'
            or g_var.stripped.upper()=='# DEDENT-END-TAG-OFF'
            or g_var.stripped.upper()=='#DEDENT-END-TAG OFF'
            or g_var.stripped.upper()=='# DEDENT-END-TAG OFF'
            ):
            g_config.dedent_end_tag=False
            print(g_var.text.rstrip(),file=g_var.sio,sep='')
        elif (
            g_var.stripped.upper().startswith("#END")
            or g_var.stripped.upper().startswith("# END")
            ):
            handle_end()
        elif (
            g_var.stripped.upper().startswith("#INDENT")
            or g_var.stripped.upper().startswith("# INDENT")
            ):
            handle_indent()
        elif (
            g_var.stripped.upper()=="#BEGIN"
            or g_var.stripped.upper()=="# BEGIN"
            ):
            g_var.lev -=1
            print(g_config.indent*g_var.lev, g_var.text.strip(), file=g_var.sio,sep='')
            g_var.lev += 1
        elif g_var.stripped.startswith("#"):
            if g_config.indent_comment:
                print(g_config.indent*g_var.lev, g_var.text.strip(), file=g_var.sio,sep='')
            else:
                print(g_var.text.rstrip(), file=g_var.sio,sep='')
            #end if
        else:            
            if check_if_auto_words(g_var.stripped)==True:
                g_var.lev -=1
                g_var.lev = max(0,g_var.lev)
                print(g_config.indent*g_var.lev, g_var.text.strip(),file=g_var.sio,sep='')
                g_var.lev += 1
            elif ( g_var.stripped.endswith(':') if g_var.stripped.find('#') == -1 else (
                    g_var.stripped[:g_var.stripped.find('#')].strip().endswith(':'))
                ):
                print(g_config.indent*g_var.lev, g_var.text.strip(),file=g_var.sio,sep='')
                g_var.lev +=1
                if check_if_two_level_word_beginning(g_var.stripped):
                    g_var.lev += 1
                #end if
            else:
                if g_var.text.strip()=='':
                    print('\n', file=g_var.sio, sep='',end='')
                else:
                    print(g_config.indent*g_var.lev, g_var.text.strip(),file=g_var.sio,sep='')
                    handle_multiline_starter()
                #end if # g_var.text.strip()
            #end if
        #end if
        #indent-on
    #end for
    content = g_var.sio.getvalue()
    g_var.sio.close()
    return content

#end def

def indent_py_main():
    g_config.tabsize = 4
    prompt="탭 크기: "
    while True:
        strTab = npPrompt(prompt, 'pydent.py2py3.py Input', str(g_config.tabsize))
        if not strTab:
            break
        #end if
        if strTab[0]!='0' and all(map(lambda c: '0'<=c<='9', strTab)) and set(strTab)!={'0'}:
            g_config.tabsize=int(strTab)
            break
        #end if
        prompt='0보다 큰 정수 입력. \n탭 크기: '
        continue
    #end while

    g_config.indent = ' '*g_config.tabsize

    text = getSelectedText(G_CURRENT_BUFFER_ID)
    text = indent_pycode(text)
    setSelectedText(text, G_CURRENT_BUFFER_ID)
#end def

if CheckVerAndCoding(G_CURRENT_BUFFER_ID):
    indent_py_main()
#end if
