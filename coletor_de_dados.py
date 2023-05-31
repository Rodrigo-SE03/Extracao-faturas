import PySimpleGUI as sg
import os
from PyPDF2 import PdfReader
import pandas as pd
import re
import xlsxwriter

sg.theme('Dark')   

layout = [[sg.Text('Selecione a pasta com as faturas')],
          [sg.Text('Faturas', size=(8, 1)), sg.Input(), sg.FolderBrowse()],
          [sg.Text('Selecione a pasta onde serão salvos os dados')],
          [sg.Text('Pasta', size=(8, 1)), sg.Input(), sg.FolderBrowse()],
          [sg.Text('Digite o nome da planilha com os dados')],
          [sg.Text('Nome', size=(8, 1)), sg.Input()],
          [sg.Submit(), sg.Cancel()]]

window = sg.Window('Coleta de dados', layout)


event, values = window.read()
pasta = values[0]
saida = f'{values[1]}/{values[2]}.xlsx'
'''
fatura = os.path.join(pasta,'04-22.pdf')
reader = PdfReader(fatura)           #para teste individual, inserir o nome do arquivo aqui, para gerar o total coloque    fatura
page = reader.pages[0]
texto = page.extract_text()
print(texto)
'''

def get_data(texto):
    mes,ano = re.search('([A-Z]{3})[\/]([0-9]{4})',texto).groups()
    data = [mes,ano]
    return data

def get_demanda_contratada(texto):
    return format_number(re.search(r'[0-9]+(DEMANDA \- kW )([0-9]+)\n',texto).group(2))

def get_demanda_hp(texto,old):
    if old:
        demanda_P = format_number(re.search(r'(DEMANDA NA PONTA )[\-,A-Z0-9a-z]+[ ]([0-9,.]+)[0-9a-z,. %\-]+(PONTA)',texto).group(2))
    else:
        demanda_P = format_number(re.search(r'(DEMANDA \- KW )[\-,A-Z0-9a-z]+[ ]([0-9,.]+)',texto).group(2))

    return demanda_P

def get_demanda_hfp(texto,old):
    if old:
        preco_demanda = format_number(re.search(r'(DEMANDA )[\-A-Z0-9%a-z, ]+[ ]([,0-9]+)[ ,\-,A-Z,0-9,%,a-z]+([0-9][.][0-9,\,]+)',texto).group(3))
        demanda = format_number(re.search(r'(DEMANDA FORA )([\-A-Z,0-9]+[ ]){3}([1-9][0-9,.]+)[ ,\-,A-Z,0-9]+(FORA PONTA)\n',texto).group(3))
    else:
        preco_demanda = format_number(re.search(r'(DEMANDA kW )([,\-A-Z0-9%a-z]+[ ]){7}([0-9]+[.,][,0-9]+)\n',texto).group(3))
        demanda = format_number(re.search(r'(DEMANDA )[\-A-Z,0-9]+[ ][\-A-Z,0-9]+[ ][\-A-Z,0-9]+[ ]([1-9][0-9,.]+)[ \-A-Z,0-9]+(FORA PONTA)\n',texto).group(2))
    dem = [demanda,preco_demanda]
    return dem

def get_demanda_exd(texto,demanda,demanda_contratada):
    demanda_exd = demanda_contratada - demanda
    if demanda_exd<=0:
        demanda_exd = 0
        preco_demanda_exd = 0
    else:
        try:
            preco_demanda_exd = format_number(re.search(r'(DEMANDA EXCED\. CONTRATADA )([ ,\-A-Z0-9%a-z]+[ ])+([0-9]+[.[0-9\,]+)\n',texto).group(3))
        except:
            preco_demanda_exd = 0
    dem_exd = [demanda_exd,preco_demanda_exd]
    return dem_exd

def get_ultrapassagem(texto):
    try:
        demanda_ultrapassagem = format_number(re.search(r'(DEMANDA ULTRAPASSAGEM )([,\-,A-Z,0-9,%,a-z]+[ ]){2}([0-9]{1,}[,][0-9]+)([,\-,A-Z,0-9,%,a-z]+[ ]){6}([0-9,.]+)',texto).group(3))
        preco_demanda_ultrapassagem = format_number(re.search(r'(DEMANDA ULTRAPASSAGEM )([,\-,A-Z,0-9,%,a-z]+[ ]){2}([0-9]{1,}[,][0-9]+)([,\-,A-Z,0-9,%,a-z]+[ ]){6}([0-9,.]+)',texto).group(5))
    except:
        demanda_ultrapassagem=0
        preco_demanda_ultrapassagem=0
    ultra = [demanda_ultrapassagem,preco_demanda_ultrapassagem]
    return ultra

def get_consumo_hp(texto,old,gen):
    if old and not gen:
        consumo_p = format_number(re.search(r'(CONSUMO P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)\n',texto).group(2))
        preco_consumo_p = format_number(re.search(r'(CONSUMO P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)\n',texto).group(3))
    elif not gen:
        consumo_p = format_number(re.search(r'(CONSUMO P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([.0-9,]+)\n',texto).group(2))
        preco_consumo_p = format_number(re.search(r'(CONSUMO P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([.0-9,]+)\n',texto).group(3))
    else:
        consumo_p = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([.0-9,]+)',texto).group(2))
        preco_consumo_p = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([.0-9,]+)',texto).group(3))
    
    if gen:
        parcela_te_p = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA P - PARC.[\n -,\-])[ ,\-A-Z,0-9%a-z]+[ ][0-9,]{7}([.,0-9]+)',texto).group(2))
    else:
        parcela_te_p = format_number(re.search(r'(PARCELA TE P)[ ,\-A-Z,0-9%a-z]+[ ]([.,0-9]+)',texto).group(2))
    preco_consumo_p = preco_consumo_p + parcela_te_p
    con_hp = [consumo_p,preco_consumo_p]
    return con_hp

def get_consumo_hfp(texto,old,gen):
    if old and not gen:
        consumo_fp = format_number(re.search(r'(CONSUMO FP [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)\n',texto).group(2))
        preco_consumo_fp = format_number(re.search(r'(CONSUMO FP [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)\n',texto).group(3))
        consumo_r = format_number(re.search(r'(CONSUMO HR [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)\n',texto).group(2))
        preco_consumo_r = format_number(re.search(r'(CONSUMO HR [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)\n',texto).group(3))
    elif not gen:
        consumo_fp = format_number(re.search(r'(CONSUMO FP kWh )[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)\n',texto).group(2))
        preco_consumo_fp = format_number(re.search(r'(CONSUMO FP kWh )[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)\n',texto).group(3))
        consumo_r = format_number(re.search(r'(CONSUMO HR kWh )[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)\n',texto).group(2))
        preco_consumo_r = format_number(re.search(r'(CONSUMO HR kWh )[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)\n',texto).group(3))
    
    else:
        consumo_fp = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA FP [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([.0-9,]+)',texto).group(2))
        preco_consumo_fp = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA FP [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([.0-9,]+)',texto).group(3))
        consumo_r = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA HR [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)\n',texto).group(2))
        preco_consumo_r = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA HR [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)\n',texto).group(3))
    
    if gen:
        parcela_te_fp = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA FP - PARC.[\n -,\-])[ ,\-A-Z,0-9%a-z]+[ ][0-9,]{7}([.,0-9]+)',texto).group(2))
        parcela_te_r = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA HR - PARC.[\n -,\-])[ ,\-A-Z,0-9%a-z]+[ ][0-9,]{7}([.,0-9]+)',texto).group(2))
    else:
        parcela_te_fp = format_number(re.search(r'(PARCELA TE FP)[ ,\-A-Z,0-9%a-z]+[ ]([0-9]+[.,\][0-9]+)',texto).group(2))
        parcela_te_r = format_number(re.search(r'(PARCELA TE HR)[ ,\-A-Z,0-9%a-z]+[ ]([0-9]+[.,\][0-9]+)',texto).group(2))
    preco_consumo_fp = preco_consumo_fp + parcela_te_fp + parcela_te_r + preco_consumo_r
    consumo_fp = consumo_fp + consumo_r
    con_hfp = [consumo_fp,preco_consumo_fp]
    return con_hfp

def get_bandeiras(texto,gen,fail=3):
    bandeira_hr = 0
    bandeira_hfp = 0
    bandeira_hp = 0
    try:
        if gen:
            try:
                bandeira_hr = format_number(re.search('(AD. BAND. VERMELHA EN. ATIVA FORN.[\\n ]HR - PARC. )([ ,\\-,A-Z,0-9,%%,a-z]+[ ][0-9,]){6}[,][0-9]{%d}([0-9]+[.,\\][0-9]+)'%(fail),texto).group(3))
                bandeira_hfp = format_number(re.search('(AD. BAND. VERMELHA EN. ATIVA FORN.[\\n ]FP - PARC. )([ ,\\-,A-Z,0-9,%%,a-z]+[ ][0-9,]){6}[,][0-9]{%d}([0-9]+[.,\\][0-9]+)'%(fail),texto).group(3))
                bandeira_hp = format_number(re.search('(AD. BAND. VERMELHA EN. ATIVA FORN.[\\n ]P - PARC. )([ ,\\-,A-Z,0-9,%%,a-z]+[ ][0-9,]){6}[,][0-9]{%d}([0-9]+[.,\\][0-9]+)'%(fail),texto).group(3))
            except:
                pass
            try:
                bandeira_hr += format_number(re.search(r'(ADC BAND. VERMELHA[ ]+INJET. HR TE )[ ,\-,A-Z,0-9,%,a-z]+[ ]([0-9.,\-]+)',texto).group(2))
            except:
                pass
            try:
                bandeira_hfp += format_number(re.search(r'(ADC BAND. VERMELHA[ ]+INJET. FP TE )[ ,\-,A-Z,0-9,%,a-z]+[ ]([0-9.,\-]+)',texto).group(2))
            except:
                pass
            try:
                bandeira_hp += format_number(re.search(r'(ADC BAND. VERMELHA[ ]+INJET. P TE )[ ,\-,A-Z,0-9,%,a-z]+[ ]([0-9.,\-]+)',texto).group(2))
            except:
                pass
        else:
            bandeira_hr = format_number(re.search(r'(ADC BAND. VERMELHA TE HR )[ ,\-,A-Z,0-9,%,a-z]+[ ]([0-9]+[.,\][0-9]+)',texto).group(2))
            bandeira_hfp = format_number(re.search(r'(ADC BAND. VERMELHA TE FP )[ ,\-,A-Z,0-9,%,a-z]+[ ]([0-9]+[.,\][0-9]+)',texto).group(2))
            bandeira_hp = format_number(re.search(r'(ADC BAND. VERMELHA TE P )[ ,\-,A-Z,0-9,%,a-z]+[ ]([0-9]+[.,\][0-9]+)',texto).group(2))

        bandeiras_preco = bandeira_hfp + bandeira_hp + bandeira_hr
    except:
        bandeiras_preco = 0
    if bandeiras_preco != 0:
        bandeiras_tipo = 'VERMELHA'
    else:
        bandeiras_tipo = 'VERDE'

    bandeiras = [bandeiras_tipo,bandeiras_preco]
    return bandeiras

def get_energia_reativa(texto,old):
    if old:
        try:
            ufer_p = re.search(r'(UFER P - kVArh )[,\-A-Z0-9%a-z]+[ ]([0-9]+[.,\][0-9]+)[ ]([0-9]+[.,\][0-9]+)',texto)
            preco_ufer_p = float(format_number(ufer_p.group(3)))
            ufer_p = float(format_number(ufer_p.group(2)))
        except:
            ufer_p = 0
            preco_ufer_p = 0
        
        try:
            ufer_fp = re.search(r'(UFER FP - kVArh )[\-A-Z0-9%,a-z]+[ ]([0-9]+[.,\][0-9]+)[ ]([0-9]+[.,\][0-9]+)',texto)
            preco_ufer_fp = float(format_number(ufer_fp.group(3)))
            ufer_fp = float(format_number(ufer_fp.group(2)))
        except:
            ufer_fp = 0
            preco_ufer_fp = 0
        
        try:
            ufer_hr = re.search(r'(UFER HR - kVArh )[\-A-Z0-9%,a-z]+[ ]([0-9]+[.,\][0-9]+)[ ]([0-9]+[.,\][0-9]+)',texto)
            preco_ufer_hr = format_number(ufer_hr.group(3))
            ufer_hr = format_number(ufer_hr.group(2))
        except:
            ufer_hr = 0
            preco_ufer_hr = 0
    else:
        try:
            ufer_p = re.search(r'(UFER P )([\-A-Z0-9%,a-z]+[ ]){2}([0-9,.]+)([\-A-Z0-9%,a-z]+[ ]){6}([0-9,.]+)',texto)
            preco_ufer_p = format_number(ufer_p.group(5))
            ufer_p = format_number(ufer_p.group(3))
        except:
            ufer_p = 0
            preco_ufer_p = 0
        
        try:
            ufer_fp = re.search(r'(UFER FP )([\-A-Z0-9%,a-z]+[ ]){2}([0-9,.]+)([\-A-Z0-9%,a-z]+[ ]){6}([0-9,.]+)',texto)
            preco_ufer_fp = format_number(ufer_fp.group(5))
            ufer_fp = format_number(ufer_fp.group(3))
        except:
            ufer_fp = 0
            preco_ufer_fp = 0
        
        try:
            ufer_hr = re.search(r'(UFER HR )([\-A-Z0-9%,a-z]+[ ]){2}([0-9,.]+)([\-A-Z0-9%,a-z]+[ ]){6}([0-9,.]+)',texto)
            preco_ufer_hr = float(format_number(ufer_hr.group(5)))
            ufer_hr = float(format_number(ufer_hr.group(3)))
        except:
            ufer_hr = 0
            preco_ufer_hr = 0
        
    ufer = ufer_p + ufer_fp + ufer_hr
    preco_ufer = preco_ufer_p + preco_ufer_fp + preco_ufer_hr
    energia_reativa = [ufer,preco_ufer]
    return energia_reativa

def get_dem_reativa(texto):
    try:
        dem_reativa = format_number(re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)([ ][0-9,%]+){6}[ ]([0-9,.]+)',texto).group(2))
        preco_dem_reativa = format_number(re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)([ ][0-9,%]+){6}[ ]([0-9,.]+)',texto).group(4))
    except:
        dem_reativa = 0
        preco_dem_reativa = 0

    demanda_reativa = [dem_reativa,preco_dem_reativa]
    return demanda_reativa

def get_ilum(texto):
    ilum = format_number(re.search(r'(ILUM)[ ,.,A-Z,a-z,Ú,\-]+([0-9]+[.,\][0-9]+)',texto).group(2))
    return ilum

def get_impostos(texto):
    pasep = format_number(re.search(r'(PIS\/PASEP )[0-9,% ]+[ ]([0-9,]+)',texto).group(2))
    cofins = format_number(re.search(r'(COFINS)[0-9,% ]+[ ]([0-9,]+)',texto).group(2))
    icms = format_number(re.search(r'(ICMS )[^0][0-9,% ]+[ ]([0-9,]+)',texto).group(2))
    impostos = [icms,pasep,cofins]
    return impostos

def get_compesacoes(texto):
    try:
        taxa = format_number(re.search('(TAXA END\. ALTERNATIVO )([0-9,]+)',texto).group(2))
    except:
        taxa = 0
    
    try:
        religacao = format_number(re.search('(RELIGAÇÃO PROGRAMADA)([ ][0-9,%]+){2}[ ]([0-9,.]+)',texto).group(3))
    except:
        religacao = 0
    
    try:
        desligamento = format_number(re.search('(DESLIGAMENTO PROGRAMADO)([ ][0-9,%]+){2}[ ]([0-9,.]+)',texto).group(3))
    except:
        desligamento = 0
    
    try:
        debito = format_number(re.search('(PARC\. DEBITO-PRC \- [0-9\/]+ \- [0-9\/]+)[ ]([0-9,.]+)',texto).group(2))
    except:
        debito = 0

    try:
        compensacao_fic_anual = format_number(re.search('(COMPENSACAO DE FIC ANUAL )[ \-]([\-0-9,.]+)',texto).group(2))*-1
    except:
        compensacao_fic_anual = 0
    
    try:
        compensacao_dic_anual = format_number(re.search('(COMPENSACAO DE DIC ANUAL )[ \-]([\-0-9,.]+)',texto).group(2))*-1
    except:
        compensacao_dic_anual = 0
    
    try:
        compensacao_dic_mensal = format_number(re.search('(COMPENSAÇÃO DE DIC MENSAL )[ \-]([\-0-9,.]+)',texto).group(2))*-1
    except:
        compensacao_dic_mensal = 0

    try:
        compensacao_fic_mensal = format_number(re.search('(COMPENSAÇÃO DE FIC MENSAL )[ \-]([\-0-9,.]+)',texto).group(2))*-1
    except:
        compensacao_fic_mensal = 0
    
    compesacoes = taxa + compensacao_dic_mensal + compensacao_fic_mensal + compensacao_dic_anual + compensacao_fic_anual + religacao + desligamento + debito
    return compesacoes

def get_multas(texto):  
    try:
        juros = format_number(re.search(r'(JUROS MORATÓRIA. )([\-0-9,]+)',texto).group(2))
        multa = format_number(re.search(r'(MULTA )[\- ][ 0-9\/.][0-9\/.]+[ ]([\-0-9,]+)',texto).group(2))
        multa = juros + multa
    except:
        multa = 0

    try:
        dev_juros = format_number(re.search(r'(DEV\. JUROS PG INDEVIDO )[ \-]([\-0-9,]+)',texto).group(2))
        dev_multa = format_number(re.search(r'(DEV\. MULTA PG\. INDEVIDA )[ \-()]+([\-0-9,]+)',texto).group(2))
        dev_multa = (dev_juros + dev_multa)*-1
    except:
        dev_multa = 0

    try:
        dev_multa += format_number(re.search(r'(ENERGIA INJETADA FP kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto).group(3))
        dev_multa += format_number(re.search(r'(ENERGIA INJETADA FP kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)\n(ENERGIA INJETADA FP kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto).group(6))
    except:
        pass

    try:
        dev_multa += format_number(re.search(r'(ENERGIA INJETADA HR kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto).group(3))
        dev_multa += format_number(re.search(r'(ENERGIA INJETADA HR kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)\n(ENERGIA INJETADA HR kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto).group(6))
    except:
        pass

    try:
        dev_multa += format_number(re.search(r'(ENERGIA INJETADA P kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto).group(3))
        dev_multa += format_number(re.search(r'(ENERGIA INJETADA P kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)\n(ENERGIA INJETADA P kWh )([0-9,%\-]+[ ]){7}([\-,0-9.]+)',texto).group(6))
    except:
        pass
    
    
    multa = multa+dev_multa
    return multa

def conferir(precos,preco_total):
    preco_calculado = 0 
    for preco in precos:
        preco_calculado += preco
    if (preco_calculado >= preco_total-0.05) and (preco_calculado <= preco_total+0.05):
        flag_confere = 'CONFERE'
    else:
        flag_confere = 'NÃO CONFERE'
        print("erro")
    conferir = [preco_calculado,flag_confere]
    return conferir

def definir_valor(texto):
    preco_total = float(format_number(re.search('(R\$)[\*]+([0-9,.]+)',texto).group(2)))

    data = get_data(texto)
    mes,ano = data
    if (mes == "JAN" and int(ano) == 2022) or (int(ano)<2022): isOld = True
    else: isOld = False
    try:
        re.search('(GERAÇÃO)',texto).group(1)
        gen = True
    except:
        gen = False

    demanda_contratada = get_demanda_contratada(texto)
    demanda_P = get_demanda_hp(texto,isOld)
    demanda,preco_demanda = get_demanda_hfp(texto,isOld)
    demanda_ex,preco_demanda_ex = get_demanda_exd(texto,demanda,demanda_contratada)
    demanda_ultrapassagem,preco_demanda_ultrapassagem = get_ultrapassagem(texto)
    consumo_hp,preco_consumo_hp = get_consumo_hp(texto,isOld,gen)
    consumo_hfp,preco_consumo_hfp = get_consumo_hfp(texto,isOld,gen)
    bandeiras_tipo,bandeiras = get_bandeiras(texto,gen)
    consumo_reativa,preco_reativa = get_energia_reativa(texto,isOld)
    dem_reativa,preco_dem_reativa = get_dem_reativa(texto)
    ilum = get_ilum(texto)
    valor_extra = get_compesacoes(texto)
    multa = get_multas(texto)
    icms,pasep,cofins = get_impostos(texto)
    precos = [preco_demanda,preco_demanda_ex,preco_demanda_ultrapassagem,preco_consumo_hp,preco_consumo_hfp,bandeiras,preco_reativa,preco_dem_reativa,ilum,valor_extra,multa]
    preco_calculado,flag_confere = conferir(precos,preco_total)
    fails = 3
    while flag_confere == "NÃO CONFERE" and gen and fails<7:
        bandeiras_tipo,bandeiras = get_bandeiras(texto,gen,fails)
        precos = [preco_demanda,preco_demanda_ex,preco_demanda_ultrapassagem,preco_consumo_hp,preco_consumo_hfp,bandeiras,preco_reativa,preco_dem_reativa,ilum,valor_extra,multa]
        preco_calculado,flag_confere = conferir(precos,preco_total)
        fails+=1

    data = f'{mes}/{ano}'
    
    maior_que = demanda_P if demanda_P>demanda else demanda

    valores = [data,demanda_P,demanda,preco_demanda,maior_que,demanda_ex,preco_demanda_ex,demanda_ultrapassagem,preco_demanda_ultrapassagem,consumo_hp,preco_consumo_hp,consumo_hfp,preco_consumo_hfp,bandeiras_tipo,bandeiras,consumo_reativa,preco_reativa,dem_reativa,preco_dem_reativa,ilum,valor_extra,multa,icms,pasep,cofins,preco_total,preco_calculado,flag_confere]
    return valores

def format_number(num):
    num = num.replace('.','')
    num = num.replace(',','.')
    return float(num)

def definir_colunas(classificacao):
    if classificacao == 'Verde':
        planilha = {'Data': [],
            'Demanda Registrada HP':[],
            'Demanda Ativa HFP/Único HFP kW':[],
            'Demanda Ativa HFP/Único R$': [],
            'Maior Entre kW':[],
            'Demanda Ativa HFP/Único S/ICMS kW':[],   # CALCULADO NA PLANILHA -- NÃO PREENCHER
            'Demanda Ativa HFP/Único S/ICMS R$':[],
            'Ultrapassagem Demanda kW':[], 
            'Ultrapassagem Demanda R$':[],
            'Consumo Energia Ativa HP kWh':[],
            'Consumo Energia Ativa HP  R$':[],
            'Consumo Energia Ativa HFP kWh':[],
            'Consumo Energia Ativa HFP  R$':[],
            'Bandeira Tarifária TIPO':[],             # CALCULADO NA PLANILHA -- NÃO PREENCHER
            'Bandeira Tarifária R$':[],
            'Energia Reativa kWh':[],
            'Energia Reativa R$':[],
            'Demanda Reativa kWh':[],
            'Demanda Reativa R$':[],
            'Contribuição iluminação pública':[],
            'Compensações Diversas':[],
            'Multa por atraso':[],
            'ICMS':[],
            'PASEP':[],
            'COFINS':[],
            'VALOR TOTAL':[],
            'VALOR CALCULADO':[],
            'CONFERÊNCIA DE VALORES':[],
            }
    return planilha


def inserir_valores(colunas,valores):
    num=0
    for coluna,item in colunas.items():
        item.append(valores[num])
        num+=1

def cor_bandeira(val):
    bg_color = '#FFC7CE' if val == "VERMELHA" else '#C6EFCE'
    color = '#9C0006' if val == "VERMELHA" else '#006100'
    return f'background-color: {bg_color}; color: {color}'

def cor_geral(val):
    bg_color = '#92D050' if val != "NÃO CONFERE" else '#FFC7CE'
    return f'background-color: {bg_color}'

planilha = definir_colunas('Verde')

for arquivo in os.listdir(pasta):
    fatura = os.path.join(pasta,arquivo)
    reader = PdfReader(fatura)           #para teste individual, inserir o nome do arquivo aqui, para gerar o total coloque    fatura
    page = reader.pages[0]
    texto = page.extract_text()
    #print(texto)

    valores = definir_valor(texto)
    inserir_valores(planilha,valores)

df = pd.DataFrame(data = planilha)
pd.set_option('display.max_colwidth', None)
writer = pd.ExcelWriter(saida, engine="xlsxwriter")


s = df.style.applymap(cor_geral).applymap(cor_bandeira,subset=pd.IndexSlice[:,['Bandeira Tarifária TIPO']]).set_properties(**{'text-align': 'center'}).set_properties(subset=['Data','VALOR TOTAL','VALOR CALCULADO'], **{'background-color': 'white'})

df.to_excel(writer, sheet_name='Sheet1')
workbook = writer.book
worksheet = writer.sheets['Sheet1']

border_fmt = workbook.add_format({'bottom':1, 'top':1, 'left':1, 'right':1})
worksheet.conditional_format(xlsxwriter.utility.xl_range(0, 0, len(df), len(df.columns)), {'type': 'no_errors', 'format': border_fmt})

s.to_excel(writer, sheet_name='Sheet1')

writer.close()



#Após determinar a classificação tarifária e se há geração própria, será montado o dicionário contendo as colunas respectivas (é preciso adicionar a coluna de "mês");
#Será criada uma função principal para atribuir os valores de cada coluna, nela vão estar presentes as condições (ex: se for azul adiciona a demanda na ponta e fora da ponta);