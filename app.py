import streamlit as st
import sys
from io import StringIO
import ply.yacc as yacc
import ply.lex as lex

from main import parser, run, lexer

st.set_page_config(page_title="R-Script Interpreter", layout="wide")

if 'code_input' not in st.session_state:
    st.session_state['code_input'] = """num1 <- 10
num2 <- 20
if (num1 < num2) {
    cat("Num2 is bigger: ", num2)
} else {
    cat("Num1 is bigger: ", num1)
}"""

def load_file():
    """Callback function to load uploaded file content into the text area"""
    uploaded_file = st.session_state.uploader
    if uploaded_file is not None:
        string_data = uploaded_file.getvalue().decode("utf-8")
        st.session_state['code_input'] = string_data

st.title("R-Script Like Interpreter")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Source Code Input")
    st.file_uploader(
        "Upload .r file (Optional)", 
        type=['r', 'txt'], 
        key='uploader', 
        on_change=load_file
    )
    
    code_area = st.text_area(
        "Editor", 
        height=300, 
        key='code_input' 
    )
    
    run_button = st.button("RUN INTERPRETER", type="primary")

with col2:
    st.subheader("Console Output")
    
    if run_button:
        old_stdout = sys.stdout
        result_buffer = StringIO()
        sys.stdout = result_buffer

        try:
            lexer.lineno = 1
            
            ast = parser.parse(st.session_state['code_input'])
            
            if ast:
                run(ast)
            else:
                pass 

        except Exception as e:
            print(f"Runtime Error: {e}")

        sys.stdout = old_stdout
        
        output_text = result_buffer.getvalue()
        if output_text:
            st.code(output_text, language="text")
        else:
            st.info("Program executed successfully with no output.")