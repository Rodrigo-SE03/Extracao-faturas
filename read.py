from PyPDF2 import PdfReader 
import pandas as pd 
import os,sys 
import re 
 
def get_dem_reativa(texto): 
    try:
        dem_reativa_p = format_number(re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)[ ][0-9., ]+(PONTA)',texto).group(2))
    except:
        dem_reativa_p = 0
    try:
        dem_reativa_fp = format_number(re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)[ ][0-9., ]+(FORA PONTA)',texto).group(2))
    except:
        dem_reativa_fp = 0
    try:    
        dem_reativa_hr = format_number(re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)[ ][0-9., ]+(RESERVADO)',texto).group(2))
    except:
        dem_reativa_hr = 0
    
    try:
        preco_dem_reativa = format_number(re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)([ ][0-9,%]+){6}[ ]([0-9,.]+)',texto).group(4))
    except:
        preco_dem_reativa = 0

    dem_reativa = dem_reativa_p+dem_reativa_fp+dem_reativa_hr
    demanda_reativa = [dem_reativa,preco_dem_reativa]
    return demanda_reativa

def format_number(num): 
    num = num.replace('.','')
    num = num.replace(',','.')
    return float(num)

reader = PdfReader('07-22.pdf') 
text = reader.pages[0].extract_text() 
print(text) 
print(get_dem_reativa(text)) 


# Testar ultrapassagem 
# Testar geração fotovoltaica 
# Energia injetada não consta 