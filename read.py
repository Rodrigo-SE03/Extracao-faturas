from PyPDF2 import PdfReader 
import pandas as pd 
import os,sys 
import re 
 
#função a ser testada 
def get_multas(texto): 
    """
    Retorna a soma das multas contidas nas faturas \n
    Deve ser sempre conferido
    """
    multa = 0
    dev_multa = 0
    if re.search(r'(JUROS MORATÓRIA. )([\-0-9,.]+)',texto) != None:
        juros = format_number(re.search(r'(JUROS MORATÓRIA. )([\-0-9,.]+)',texto).group(2))
        multa = format_number(re.search(r'(MULTA )[\- ][ 0-9\/.][0-9\/.]+[ ]([\-0-9,.]+)',texto).group(2))
        multa = juros + multa
    else:
        multa = 0
    
    if re.search(r'(VALOR [A-Z ÇÃ.]+)([\-0-9,.]+)',texto) != None:
        multa += format_number(re.search(r'(VALOR [A-Z ÇÃ.]+)([\-0-9,.]+)',texto).group(2))
    else:
        multa = 0
        
    if re.search(r'(DEV\. JUROS PG INDEVIDO )[ \-]([\-0-9,.]+)',texto) != None:
        dev_juros = format_number(re.search(r'(DEV\. JUROS PG INDEVIDO )[ \-]([\-0-9,.]+)',texto).group(2))
        dev_multa = format_number(re.search(r'(DEV\. MULTA PG\. INDEVIDA )[ \-()]+([\-0-9,.]+)',texto).group(2))
        dev_multa = (dev_juros + dev_multa)*-1
    else:
        dev_multa = 0

    if re.search(r'(ENERGIA INJETADA FP kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto) != None:
        dev_multa += format_number(re.search(r'(ENERGIA INJETADA FP kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto).group(3))
        dev_multa += format_number(re.search(r'(ENERGIA INJETADA FP kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)\n(ENERGIA INJETADA FP kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto).group(6))
    else:
        pass

    if re.search(r'(ENERGIA INJETADA HR kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto) != None:
        dev_multa += format_number(re.search(r'(ENERGIA INJETADA HR kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto).group(3))
        dev_multa += format_number(re.search(r'(ENERGIA INJETADA HR kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)\n(ENERGIA INJETADA HR kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto).group(6))
    else:
        pass

    if re.search(r'(ENERGIA INJETADA P kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto) != None:
        dev_multa += format_number(re.search(r'(ENERGIA INJETADA P kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto).group(3))
        dev_multa += format_number(re.search(r'(ENERGIA INJETADA P kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)\n(ENERGIA INJETADA P kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto).group(6))
    else:
        pass
    
    
    multa = multa+dev_multa
    return multa
#--------------------

def format_number(num): 
    num = num.replace('.','')
    num = num.replace(',','.')
    return float(num)

reader = PdfReader('09-22.pdf') 
text = reader.pages[0].extract_text() 
print(text) 
#print(get_bandeiras(text,True)) 

