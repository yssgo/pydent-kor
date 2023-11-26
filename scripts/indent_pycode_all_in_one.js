'use strict';

let g_description_en = "";
let g_description_ko = "";

let g_config; // [g]lobal [config]uration
let g_var; // [g]lobal [var]iables
    
class PydentVariables {
    constructor(){
        this.refresh()
    }
    refresh() {
        this.stripped = ""; // [s]tripped [t]ext
        this.lev = 0;  // [lev]el
        this.sio = ""; // [S]tring[IO]
        this.text_ = "";
        this.inside_triple_singles = false;
        this.inside_triple_doubles = false;
        this.indent_off = false;
    }
}
class PydentConfig {
    constructor() {
        this.refresh();
    }
    refresh(){
        this.tabsize = 4;
        this.indent = ' '.repeat(this.tabsize);
        this.auto_unindent = true;
        this.indent_comment = true;
    }
};

g_config = new PydentConfig();
g_var = new PydentVariables();
    
g_description_en = `A proram that repairs indentation of python code.

After statements that end with a colon indetation level
increases automatically by one step.

Please insert the following special comments in the code:

#TABSIZE 4
    Number of spaces per indentation level (default: 4)
#END
    inentation level decreases by one step.
#END if while for
    inentation decrease by 3 levels.
    (3 is the number of words after #END )
#END 2
    decrease indentation level by 2 steps.
#INDENT 0
    indentation level is 0
#INDENT @+3
    increase indentation level by 3 steps.
#INDENT @-3
    decrease indentation level by 3 steps.
#AUTO-UNINDENT ON
#AUTO-UNINDENT-ON
    Automatically unindent 'elif', 'else', 'except', and 'case' statements. (default)
#AUTO-UNINDENT OFF (deprecated)
#AUTO-UNINDENT-OFF (deprecated)
    Turn off AUTO-UNINDENT
#INDENT OFF
#INDENT-OFF
    don't process indentation from this line
#INDENT ON
#INDENT-ON
    resume processing indentation after this line
#INDENT-COMMENT OFF
#INDENT-COMMENT-OFF
    don't indent comment lines
#INDENT-COMMENT ON
#INDENT-COMMENT-ON
    indent comment lines (default)\n`

g_description_ko = `파이썬 코드의 들여 쓰기를 고치는 프로그램.
콜론으로 끝나는 명령문 이후에, 들여 쓰기 수준이
한 단계 자동으로 증가함.

코드에 다음 특별 주석을 삽입하십시오:
'use strict';
#TABSIZE 4
    들여쓰기 수준 당 스페이스 개수 (기본값은 4)
#END
    들여쓰기 수준이 한 단계 감소합니다.
#END if while for
    들여쓰기 수준이 3 단계 감소.
    (3은 #END 뒤의 단어 수)
#END 2
    들여 쓰기 수준을 2 단계 줄입니다.
#INDENT 0
    들여 쓰기 수준이 0
#INDENT @+3
    들여 쓰기 수준을 3 단계 늘림.
#INDENT @-3
    들여 쓰기 수준을 3 단계 줄입니다.
#AUTO-UNINDENT ON
#AUTO-UNINDENT-ON
    'elif', 'else', 'except', 및 'else' 문을 자동으로 한 단계 내어쓰기 (기본 설정임)
#AUTO-UNINDENT OFF (폐기 예정)
#AUTO-UNINDENT-OFF (폐기 예정)
    AUTO-UNINDENT 를 끔.
#INDENT-OFF
#INDENT OFF
    이 줄부터 자동 들여쓰기를 하지 않음
#INDENT-ON
#INDENT ON
    이 줄 후에 자동 들여쓰기를 다시 시작
#COMMENT-ON
#COMMENT ON
    주석 줄도 자동 들여쓰기(기본)
#COMMENT-OFF
#COMMENT OFF
    주석 줄 자동 들여쓰기 하지 않음`;

// See also: https://stackoverflow.com/a/32523641
function enableTab(id){
    let obj = document.getElementById(id);   
    obj.addEventListener('keydown', function (ev){
        let obj = ev.target;
        if(ev.keyCode===9){
            let v=obj.value;
            let s=obj.selectionStart;
            let e=obj.selectionEnd;
            ev.preventDefault();
            if(ev.shiftKey){
                let s4s = v.substring(s-4,s)
                if(s4s.match(/^( {1,4})$/m) !== null){
                    let splen = (s4s.match(/^( {1,4})$/m))[1].length;
                    obj.value=v.substring(0,s-splen)+v.substring(e);
                    obj.selectionStart=obj.selectionEnd=s-splen;
                }
                else if(s4s.match(/^( {1,3})$/m) !== null){
                    let splen = (s4s.match(/^( {1,3})$/m))[1].length;
                    obj.value=v.substring(0,s-splen)+v.substring(e);
                    obj.selectionStart=obj.selectionEnd=s-splen;
                }                
            } else {
                obj.value=v.substring(0, s)+'    '+v.substring(e);
                obj.selectionStart=obj.selectionEnd=s+4;
            }
            return false;
        }
    });
}
function print(sz){
    g_var.sio += sz + "\n";
}    

function check_if_auto_words(st){
    if (g_config.auto_unindent === true) {
        let else_like = [
            'else:', 'else :' ,'elif ', 'elif(',
            'except ', 'except:',  'except :',
            'finally:', 'finally :',
			'case (', 'case(', 'case ' // Python 3.10 match case
        ];
        for(let i=0; i < else_like.length; i++){
            let x = else_like[i]
            if (st.startsWith(x)) {
                return true;
            } //end if
        }//end for
    } //end if
    return false;
}

function check_if_two_level_word_beginning(st){
    let two_level_word_beginnings = ['match (', 'match(', 'match '];
    for(let i=0; i < two_level_word_beginnings.length; i++){
        let x = two_level_word_beginnings[i];
        if (st.startsWith(x)){
            return true;
        }
    }
    return false;
}

function check_if_end_of_two_level_word(wrd){
    let two_level_words = ['match']
    for(let i=0; i < two_level_words.length; i++){
        let x = two_level_words[i];
        if (wrd == x){
            return  true;            
        }
    }
    return false;
}

function indentIt(){
    document.getElementById("indented").value = indent_pycode(document.getElementById("code").value);
}

function handle_end(){
    // global g_var.stripped, g_var.lev
    let wa = [] ;

    if (g_var.stripped.toUpperCase().startsWith("#END") ) {
        if (g_var.stripped.length>"#END".length) {
            let commentpos = g_var.stripped.indexOf('#', "#END".length);
            if (-1 !=commentpos) {
                g_var.stripped = g_var.stripped.substring(0, commentpos);
            } //end if
        } //end if
        wa = g_var.stripped.split(' ');
    } else {
        if(g_var.stripped.length > "# END".length){
            let commentpos = g_var.stripped.indexOf("#", "# END".length);
            if (-1 !=commentpos) {
                g_var.stripped = g_var.stripped.substring(0, commentpos);
            } //end if
        } //endif
        stx = "# END" + g_var.stripped.substring("# END".length);
        wa = stx.split(' ');
    } //end if

    while ( wa.indexOf('') !=  -1 ){
        let idx= wa.indexOf('');      
        wa.splice(idx, 1);
    } //end while
    if (wa.length == 1) {
        g_var.lev -= 1;
        g_var.lev = Math.max(0, g_var.lev);
    } else {
        if (!isNaN(wa[1])) {
            g_var.lev -= parseInt(wa[1]);
            g_var.lev = Math.max(0, g_var.lev);
        } else {
            g_var.lev -= wa.length -1;
            for(let i=0; i< wa.length; i++){
                if(check_if_end_of_two_level_word(wa[i])){
                    g_var.lev -= 1;
                }
            }
            g_var.lev = Math.max(0, g_var.lev);
        } //end if
    } //end if
    print(g_config.indent.repeat(g_var.lev) + g_var.text_.trim());    
}

function handle_indent(){
    // global g_var.lev
    let wa = [];
    if (g_var.stripped.startsWith("#INDENT")) {
        wa = g_var.stripped.split(' ');
    } else {
        let stx= "#INDENT" + g_var.stripped.substring("# INDENT".length);
        wa=stx.split(' ');
    } //end if
    if (wa.length < 2) {
        print (g_config.indent.repeat(g_var.lev) + g_var.text_.trim());
    } else {
        let ag_sLevel = wa[1];
        if (!isNaN(ag_sLevel)) {
            g_var.lev = parseInt(ag_sLevel);
            g_var.lev = Math.max(0, g_var.lev);
            print (g_config.indent.repeat(g_var.lev) + g_var.stripped);
        } else {
            if (ag_sLevel.length>=2 && ag_sLevel[0]=='@') {
                let delta = 0;
                if (!isNaN(ag_sLevel.substring(1))){
                    delta = parseInt(ag_sLevel.substring(1));
                }else {
                    delta = 0;
                } //end if
                g_var.lev += delta;
                g_var.lev = Math.max(0, g_var.lev);
            } //end if
            print(g_config.indent.repeat(g_var.lev) + g_var.text_.trim());
        } //end if
    } //end if // (wa.length < 2)
}

function handle_multiline_starter() {
    let rstripped = g_var.text_.trimRight();
    let lQuotes = rstripped.indexOf(`'''`);  
    if (lQuotes != -1){
        let rQuotes = -1;
        if (lQuotes +3 <= rstripped.length - 1)
            rQuotes = g_var.text_.trimRight().indexOf(`'''`, lQuotes +3);
        if (rQuotes == -1){
            g_var.inside_triple_singles = true;            
        }
    } else {
        lQuotes = g_var.text_.indexOf(`"""`);
        if (lQuotes != -1){            
            let rQuotes = -1;
            if(lQuotes+3 <= g_var.text_.trimRight().length -1)
                rQuotes = g_var.text_.indexOf(`"""`, lQuotes+3);
            if(rQuotes == -1){
                g_var.inside_triple_doubles = true;                
            } // if
        }// if lQuotes != -1
    }// if lQuotes != -1 else
}

function indent_pycode(code){
    g_var.refresh();
    g_config.refresh();
    
    let code_split = code.split("\n");
    
    g_var.stripped = "";
    g_var.lev = 0;
    g_var.sio = "";
    g_var.text_ = "";
    
    g_config.auto_unindent = true;
    g_var.inside_triple_singles = false;
    g_var.inside_triple_doubles = false;
    
    g_config.indent_comment = true;
    g_var.indent_off = false;
    
    
    for (let i = 0;i < code_split.length; i++) {
        g_var.text_ = code_split[i];
        g_var.stripped =g_var.text_.trim();

        if (g_var.stripped === '') {
            print('');
            continue;
        }
        
        if (g_var.indent_off === true) {
            print(g_var.text_.trimRight());
            if (g_var.stripped.toUpperCase() == '#INDENT-ON' || g_var.stripped.toUpperCase() == '# INDENT-ON' ||
                g_var.stripped.toUpperCase() == '#INDENT ON' || g_var.stripped.toUpperCase() == '# INDENT ON'
            ) {
                g_var.indent_off = false;
            }
            continue;
        } //end if

        if (g_var.inside_triple_singles === true) {
            print(g_var.text_.trimRight());
            if (g_var.text_.trimRight().endsWith(`'''`)){
                g_var.inside_triple_singles = false;                
            }
            continue;
        }
        if (g_var.inside_triple_doubles === true){
            print(g_var.text_.trimRight());
            if (g_var.text_.trimRight().endsWith(`"""`)){
                g_var.inside_triple_doubles = false;                
            }
            continue;
        }

        if (g_var.stripped.toUpperCase() == '#INDENT-OFF' || g_var.stripped.toUpperCase() == '# INDENT-OFF' ||
            g_var.stripped.toUpperCase() == '#INDENT OFF' || g_var.stripped.toUpperCase() == '# INDENT OFF'
        ) {
            g_var.indent_off=true;
            print(g_var.text_.trimRight());            
            continue;
        }

        if ( ['#TABSIZE ', '#TABSIZE\t'].includes(g_var.stripped.toUpperCase().slice(0,9)) ){
            g_config.tabsize = parseInt(g_var.stripped.slice(9),10);
            if(g_config.tabsize < 1){
                g_config.tabsize = 4;
            }
            g_config.indent = " ".repeat(g_config.tabsize);
            print(g_var.text_.trimRight());
            continue
        }


        if (g_var.stripped.toUpperCase() == '#AUTO-UNINDENT OFF'
            || g_var.stripped.toUpperCase() == '# AUTO-UNINDENT OFF'
            || g_var.stripped.toUpperCase() == '#AUTO-UNINDENT-OFF'
            || g_var.stripped.toUpperCase() == '# AUTO-UNINDENT-OFF'
        ) {
            g_config.auto_unindent = false;
            print(g_var.text_.trimRight());
        } else if (g_var.stripped.toUpperCase() == '#AUTO-UNINDENT ON'
            || g_var.stripped.toUpperCase() == '# AUTO-UNINDENT ON'
            || g_var.stripped.toUpperCase() == '#AUTO-UNINDENT-ON'
            || g_var.stripped.toUpperCase() == '# AUTO-UNINDENT-ON'
        ) {
            g_config.auto_unindent = true;
            print(g_var.text_.trimRight());
        } else if (g_var.stripped.toUpperCase() == '# INDENT-COMMENT-OFF'
            || g_var.stripped.toUpperCase() == '# INDENT-COMMENT-OFF'
            || g_var.stripped.toUpperCase() == '# INDENT-COMMENT FF'
            || g_var.stripped.toUpperCase() == '# INDENT-COMMENT FF'
        ) {
            g_config.indent_comment = false;
            print(g_var.text_.trimRight());
        } else if (g_var.stripped.toUpperCase() == '# INDENT-COMMENT-ON'
            || g_var.stripped.toUpperCase() == '# INDENT-COMMENT-ON'
            || g_var.stripped.toUpperCase() == '# INDENT-COMMENT ON'
            || g_var.stripped.toUpperCase() == '# INDENT-COMMENT ON'
        ) {
            g_config.indent_comment = true;
            print(g_var.text_.trimRight());
        } else if (g_var.stripped.toUpperCase().startsWith("#END")
            || g_var.stripped.toUpperCase().startsWith("# END")
        ) {
            handle_end();
        } else if (g_var.stripped.startsWith("#INDENT")
            || g_var.stripped.startsWith("# INDENT")
        ) {
            handle_indent();
        } else if(g_var.stripped.toUpperCase() == '#BEGIN'
            || g_var.stripped.toUpperCase() == '# BEGIN'
        ){
            leve -= 1;
            print(g_config.indent.repeat(g_var.lev) + g_var.text_.trim());
            leve += 1;
        } else if (g_var.stripped.startsWith("#")) {
            if(g_config.indent_comment){
                print(g_config.indent.repeat(g_var.lev)+g_var.text_.trim());
            } else {
                print(g_var.text_.trimRight());
            }
        } else {                        
            if (check_if_auto_words(g_var.stripped) === true){
                g_var.lev -= 1;
                g_var.lev = Math.max(0, g_var.lev);                
                print(g_config.indent.repeat(g_var.lev) + g_var.text_.trim());
                g_var.lev += 1;             
            } else if  ( (g_var.stripped.indexOf('#') == -1) ? g_var.stripped.endsWith(':') : g_var.stripped.substring(0,g_var.stripped.indexOf('#')).trim().endsWith(':') ) {
                print(g_config.indent.repeat(g_var.lev) + g_var.text_.trim());
                g_var.lev += 1;
                if (check_if_two_level_word_beginning(g_var.stripped)){
                    g_var.lev += 1;
                }
            } else {
                if (g_var.text_.trim() === ''){
                    print("");
                }
                else{
                    print(g_config.indent.repeat(g_var.lev)+g_var.text_.trim());  
                    handle_multiline_starter();
              } // if g_var.text_.trim
            } // if check_if_auto_words
        } //end if // (g_var.stripped.toUpperCase() == '#INDENT-OFF'
    } //end for // let i = 0
    return g_var.sio;
}  //end

