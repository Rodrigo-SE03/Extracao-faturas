from PyPDF2 import PdfReader 
import pandas as pd 
import os,sys 
import re 
 
#função a ser testada 


def format_number(num): 
    num = num.replace('.','')
    num = num.replace(',','.')
    return float(num)

reader = PdfReader('23-04.pdf') 
text = reader.pages[0].extract_text() 
print(text) 
#print(get_bandeiras(text,True)) 

