from PyPDF2 import PdfReader 
import pandas as pd 
import os,sys 
import re 
 
def get_classificacao(pasta):
    fatura = os.path.join(pasta,os.listdir(pasta)[0])
    reader = PdfReader(fatura)           
    page = reader.pages[0]
    texto = page.extract_text()
    classificacao = "Azul"  if re.search(r'(THS_VERDE)',texto) is None else "Verde"
    return classificacao

def format_number(num): 
    num = num.replace('.','')
    num = num.replace(',','.')
    return float(num)

reader = PdfReader('10-22.pdf') 
text = reader.pages[0].extract_text() 
print(text) 
print(get_classificacao(text)) 


# Testar geração fotovoltaica 
# Energia injetada não consta 