import re
from PyPDF2 import PdfReader
import os

def get_texto(fatura):
    """
    Retorna o texto contido na fatura
    """
    reader = PdfReader(fatura)           
    page = reader.pages[0]
    texto = page.extract_text()

    return texto

def get_classificacao(pasta):
    """
    Identifica a classificação tarifária da fatura (verde ou azul)
    """
    fatura = os.path.join(pasta,os.listdir(pasta)[0])
    reader = PdfReader(fatura)           
    page = reader.pages[0]
    texto = page.extract_text()
    classificacao = "Azul"  if re.search(r'(THS_VERDE)',texto) is None else "Verde"
    return classificacao

def get_gen(texto):
    """
    Verifica se a UC possui geração própria de energia
    """
    gen = False if re.search('(GERAÇÃO)',texto) is None else True
    return gen

def format_number(num):
    """
    Converte o número extraído como string para um float
    """
    num = num.replace('.','')
    num = num.replace(',','.')
    return float(num)

def get_data(texto):
    """
    Retorna uma lista com a data da fatura [mês, ano]
    """
    mes,ano = re.search('([A-Z]{3})[\/]([0-9]{4})',texto).groups()
    data = [mes,ano]
    return data

def get_demanda_contratada(texto):
    """
    Retorna a demanda contratada em kW
    """
    return format_number(re.search(r'(DEMANDA \- kW )([0-9]+)\n',texto).group(2))

def get_demanda_hp(texto):
    """
    Retorna a demanda no horário de ponta
    """
    demanda_P = format_number(re.search(r'(DEMANDA \- KW )[\-,A-Z0-9a-z]+[ ]([0-9,.]+)',texto).group(2))
    return demanda_P

def get_demanda_hfp(texto):
    """
    Retorna uma lista com a demanda fora do horário de ponta e o valor pago pela demanda na fatura [demanda fora de ponta, valor pago]
    """
    preco_demanda = format_number(re.search(r'(DEMANDA kW )([,\-A-Z0-9%a-z]+[ ]){7}([0-9]+[.,][,0-9]+)\n',texto).group(3))
    demanda = format_number(re.search(r'(DEMANDA )[\-A-Z,0-9]+[ ][\-A-Z,0-9]+[ ][\-A-Z,0-9]+[ ]([1-9][0-9,.]+)[ \-A-Z,0-9]+(FORA PONTA)',texto).group(2))
    dem = [demanda,preco_demanda]
    return dem

def get_demanda_exd(texto,demanda,demanda_contratada):
    """
    Retorna uma lista com a demanda excedente e o valor pago pelo excedente [demanda excedente, valor pago]
    """
    demanda_exd = demanda_contratada - demanda
    if demanda_exd<=0:
        demanda_exd = 0
        preco_demanda_exd = 0
    else:
        if re.search(r'(DEMANDA EXCED\. CONTRATADA )([ ,\-A-Z0-9%a-z]+[ ])+([0-9]+[.[0-9\,]+)\n',texto) is None:
            preco_demanda_exd = 0
        else: 
            preco_demanda_exd = format_number(re.search(r'(DEMANDA EXCED\. CONTRATADA )([ ,\-A-Z0-9%a-z]+[ ])+([0-9]+[.[0-9\,]+)\n',texto).group(3))
    dem_exd = [demanda_exd,preco_demanda_exd]
    return dem_exd

def get_ultrapassagem(texto):
    """
    Retorna uma lista com a demanda de ultrapassagem e o valor pago pela ultrapassagem na fatura [demanda de ultrapassagem, valor pago]
    """
    if re.search(r'(DEMANDA ULTRAPASSAGEM )([\-,A-Z0-9%a-z]+[ ]){2}([0-9]{1,}[,][0-9]+)([,\-A-Z0-9%a-z]+[ ]){6}([0-9,.]+)',texto) != None:
        demanda_ultrapassagem = format_number(re.search(r'(DEMANDA ULTRAPASSAGEM )([\-,A-Z0-9%a-z]+[ ]){2}([0-9]{1,}[,][0-9]+)([,\-A-Z0-9%a-z]+[ ]){6}([0-9,.]+)',texto).group(3))
        preco_demanda_ultrapassagem = format_number(re.search(r'(DEMANDA ULTRAPASSAGEM )([,\-A-Z0-9%a-z]+[ ]){2}([0-9]{1,}[,][0-9]+)([,\-A-Z0-9%a-z]+[ ]){6}([0-9,.]+)',texto).group(5))
    else:
        demanda_ultrapassagem=0
        preco_demanda_ultrapassagem=0
    ultra = [demanda_ultrapassagem,preco_demanda_ultrapassagem]
    return ultra

def get_consumo_hp(texto,gen):
    """
    Retorna uma lista com o consumo em kWh no horário de ponta e o valor pago (TUSD + TE) [consumo P, valor pago]
    """
    if gen:
        consumo_p = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[0-9 ,%]+[ ]([0-9.,]+)\n',texto).group(2))
        preco_consumo_p = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[0-9 ,%]+[ ]([0-9.,]+)\n',texto).group(3))
        parcela_te_p = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA P - PARC.[\n -,\-])[ ,\-A-Z,0-9%a-z]+[ ]([.,0-9]+)\n',texto).group(2))
    else:
        consumo_p = format_number(re.search(r'(CONSUMO P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([.0-9,]+)\n',texto).group(2))
        preco_consumo_p = format_number(re.search(r'(CONSUMO P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([.0-9,]+)\n',texto).group(3))
        parcela_te_p = format_number(re.search(r'(PARCELA TE P)[ ,\-A-Z0-9%a-z]+[ ]([.,0-9]+)',texto).group(2))
    preco_consumo_p = preco_consumo_p + parcela_te_p
    con_hp = [consumo_p,preco_consumo_p]
    return con_hp

def get_consumo_hfp(texto,gen):
    """
    Retorna uma lista com o consumo em kWh no horário fora de ponta e horário reservado e o valor pago (TUSD + TE) [consumo FP, valor pago]
    """
    if gen:
        consumo_fp = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA FP [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)',texto).group(2))
        preco_consumo_fp = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA FP [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)',texto).group(3))
        consumo_r = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA HR [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)',texto).group(2))
        preco_consumo_r = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA HR [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)',texto).group(3))
        parcela_te_fp = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA FP - PARC.[\n -,\-])[ ,\-A-Z0-9%a-z]+[ ]([.,0-9]+)\n',texto).group(2))
        parcela_te_r = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA HR - PARC.[\n -,\-])[ ,\-A-Z0-9%a-z]+[ ]([.,0-9]+)\n',texto).group(2))
    else:
        consumo_fp = format_number(re.search(r'(CONSUMO FP kWh )[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)',texto).group(2))
        preco_consumo_fp = format_number(re.search(r'(CONSUMO FP kWh )[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)',texto).group(3))
        consumo_r = format_number(re.search(r'(CONSUMO HR kWh )[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)\n',texto).group(2))
        preco_consumo_r = format_number(re.search(r'(CONSUMO HR kWh )[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)\n',texto).group(3))
        parcela_te_fp = format_number(re.search(r'(PARCELA TE FP)[ ,\-A-Z0-9%a-z]+[ ]([0-9]+[.,\][0-9]+)',texto).group(2))
        parcela_te_r = format_number(re.search(r'(PARCELA TE HR)[ ,\-A-Z0-9%a-z]+[ ]([0-9]+[.,\][0-9]+)',texto).group(2))
    preco_consumo_fp = preco_consumo_fp + parcela_te_fp + parcela_te_r + preco_consumo_r
    consumo_fp = consumo_fp + consumo_r
    con_hfp = [consumo_fp,preco_consumo_fp]
    return con_hfp

def get_bandeiras(texto,gen):
    """
    Retorna uma lista com o tipo da bandeira (vermelha/verde) e o valor pago total na fatura [tipo da bandeira, valor pago]
    """
    bandeira_hr = 0
    bandeira_hfp = 0
    bandeira_hp = 0

    if gen:
        if re.search(r'(AD. BAND. VERMELHA EN. ATIVA FORN. HR - PARC. )([ ,\-A-Z0-9%a-z]+[ ]){2}([0-9,.]+)',texto) != None:
            bandeira_hr = format_number(re.search(r'(AD. BAND. VERMELHA EN. ATIVA FORN. HR - PARC. )([ ,\-A-Z0-9%a-z]+[ ]){2}([0-9,.]+)',texto).group(3))
            bandeira_hfp = format_number(re.search(r'(AD. BAND. VERMELHA EN. ATIVA FORN. FP - PARC. )([ ,\-A-Z0-9%a-z]+[ ]){2}([0-9,.]+)',texto).group(3))
            bandeira_hp = format_number(re.search(r'(AD. BAND. VERMELHA EN. ATIVA FORN. P - PARC. )([ ,\-A-Z0-9%a-z]+[ ]){2}([0-9,.]+)',texto).group(3))
        else:
            pass
        if re.search(r'(ADC BAND. VERMELHA[ ]+INJET. HR TE )[ ,\-A-Z0-9%a-z]+[ ]([0-9.,\-]+)',texto) != None:
            bandeira_hr += format_number(re.search(r'(ADC BAND. VERMELHA[ ]+INJET. HR TE )[ ,\-A-Z0-9%a-z]+[ ]([0-9.,\-]+)',texto).group(2))
        else:
            pass
        if re.search(r'(ADC BAND. VERMELHA[ ]+INJET. FP TE )[ ,\-A-Z0-9%a-z]+[ ]([0-9.,\-]+)',texto) != None:
            bandeira_hfp += format_number(re.search(r'(ADC BAND. VERMELHA[ ]+INJET. FP TE )[ ,\-A-Z0-9%a-z]+[ ]([0-9.,\-]+)',texto).group(2))
        else:
            pass
        if re.search(r'(ADC BAND. VERMELHA[ ]+INJET. P TE )[ ,\-A-Z0-9%a-z]+[ ]([0-9.,\-]+)',texto) != None:
            bandeira_hp += format_number(re.search(r'(ADC BAND. VERMELHA[ ]+INJET. P TE )[ ,\-A-Z0-9%a-z]+[ ]([0-9.,\-]+)',texto).group(2))
        else:
            pass
    else:
        if re.search(r'(ADC BAND. VERMELHA TE HR )[ ,\-A-Z0-9%a-z]+[ ]([0-9]+[.,\][0-9]+)',texto) != None:
            bandeira_hr = format_number(re.search(r'(ADC BAND. VERMELHA TE HR )[ ,\-A-Z0-9%a-z]+[ ]([0-9]+[.,\][0-9]+)',texto).group(2))
            bandeira_hfp = format_number(re.search(r'(ADC BAND. VERMELHA TE FP )[ ,\-A-Z0-9%a-z]+[ ]([0-9]+[.,\][0-9]+)',texto).group(2))
            bandeira_hp = format_number(re.search(r'(ADC BAND. VERMELHA TE P )[ ,\-A-Z0-9%a-z]+[ ]([0-9]+[.,\][0-9]+)',texto).group(2))
        else:
            bandeiras_preco = 0

    bandeiras_preco = bandeira_hfp + bandeira_hp + bandeira_hr


    if bandeiras_preco != 0:
        bandeiras_tipo = 'VERMELHA'
    else:
        bandeiras_tipo = 'VERDE'

    bandeiras = [bandeiras_tipo,bandeiras_preco]
    return bandeiras

def get_energia_reativa(texto):
    """
    Retorna uma lista com o valor medido de energia reativa (UFER) e o valor pago com a energia reativa na fatura [ufer, valor pago]
    """
    if re.search(r'(UFER P )([\-A-Z0-9%,a-z]+[ ]){2}([0-9,.]+)([\-A-Z0-9%,a-z]+[ ]){6}([0-9,.]+)',texto) != None:
        ufer_p = re.search(r'(UFER P )([\-A-Z0-9%,a-z]+[ ]){2}([0-9,.]+)([\-A-Z0-9%,a-z]+[ ]){6}([0-9,.]+)',texto)
        preco_ufer_p = format_number(ufer_p.group(5))
        ufer_p = format_number(ufer_p.group(3))
    else:
        ufer_p = 0
        preco_ufer_p = 0
    
    if re.search(r'(UFER FP )([\-A-Z0-9%,a-z]+[ ]){2}([0-9,.]+)([\-A-Z0-9%,a-z]+[ ]){6}([0-9,.]+)',texto) != None:
        ufer_fp = re.search(r'(UFER FP )([\-A-Z0-9%,a-z]+[ ]){2}([0-9,.]+)([\-A-Z0-9%,a-z]+[ ]){6}([0-9,.]+)',texto)
        preco_ufer_fp = format_number(ufer_fp.group(5))
        ufer_fp = format_number(ufer_fp.group(3))
    else:
        ufer_fp = 0
        preco_ufer_fp = 0
    
    if re.search(r'(UFER HR )([\-A-Z0-9%,a-z]+[ ]){2}([0-9,.]+)([\-A-Z0-9%,a-z]+[ ]){6}([0-9,.]+)',texto) != None:
        ufer_hr = re.search(r'(UFER HR )([\-A-Z0-9%,a-z]+[ ]){2}([0-9,.]+)([\-A-Z0-9%,a-z]+[ ]){6}([0-9,.]+)',texto)
        preco_ufer_hr = float(format_number(ufer_hr.group(5)))
        ufer_hr = float(format_number(ufer_hr.group(3)))
    else:
        ufer_hr = 0
        preco_ufer_hr = 0
        
    ufer = ufer_p + ufer_fp + ufer_hr
    preco_ufer = preco_ufer_p + preco_ufer_fp + preco_ufer_hr
    energia_reativa = [ufer,preco_ufer]
    return energia_reativa

def get_dem_reativa(texto):
    """
    Retorna uma lista com o valor medido de demanda de energia reativa (UFER) e o valor pago com a demanda energia reativa na fatura [dmcr, valor pago]
    """
    if re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)[ ][0-9., ]+(PONTA)',texto) != None:
        dem_reativa_p = format_number(re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)[ ][0-9., ]+(PONTA)',texto).group(2))
    else:
        dem_reativa_p = 0

    if re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)[ ][0-9., ]+(FORA PONTA)',texto) != None:
        dem_reativa_fp = format_number(re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)[ ][0-9., ]+(FORA PONTA)',texto).group(2))
    else:
        dem_reativa_fp = 0

    if re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)[ ][0-9., ]+(RESERVADO)',texto) != None:    
        dem_reativa_hr = format_number(re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)[ ][0-9., ]+(RESERVADO)',texto).group(2))
    else:
        dem_reativa_hr = 0
    
    if re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)([ ][0-9,%]+){6}[ ]([0-9,.]+)',texto) != None:
        preco_dem_reativa = format_number(re.search(r'(DMCR [a-zA-Z0-9]+)[ ]([0-9,.]+)([ ][0-9,%]+){6}[ ]([0-9,.]+)',texto).group(4))
    else:
        preco_dem_reativa = 0

    dem_reativa = dem_reativa_p+dem_reativa_fp+dem_reativa_hr
    demanda_reativa = [dem_reativa,preco_dem_reativa]
    return demanda_reativa

def get_ilum(texto):
    """
    Retorna o valor pago com a iluminação pública na fatura
    """
    if re.search(r'(ILUM)[ .,A-Za-zÚ\-]+([0-9]+[.,\][0-9]+)',texto) != None:
        ilum = format_number(re.search(r'(ILUM)[ .,A-Za-zÚ\-]+([0-9]+[.,\][0-9]+)',texto).group(2))
    else:
        ilum = 0
    
    return ilum

def get_impostos(texto):
    """
    Retorna uma lista com os valores dos impostos (ICMS, PIS/PASEP e COFINS) [icms, pasep, cofins]
    """
    pasep = format_number(re.search(r'(PIS\/PASEP )[0-9,% ]+[ ]([0-9,]+)',texto).group(2))
    cofins = format_number(re.search(r'(COFINS)[0-9,% ]+[ ]([0-9,]+)',texto).group(2))
    icms = format_number(re.search(r'(ICMS )[^0][0-9,% ]+[ ]([0-9,]+)',texto).group(2))
    impostos = [icms,pasep,cofins]
    return impostos

def get_compesacoes(texto):
    """
    Retorna a soma dos valores das compensações contidas na fatura \n
    Deve ser sempre conferido
    """
    if re.search('(TAXA END\. ALTERNATIVO )([0-9,]+)',texto) != None:
        taxa = format_number(re.search('(TAXA END\. ALTERNATIVO )([0-9,]+)',texto).group(2))
    else:
        taxa = 0
    
    if re.search('(RELIGAÇÃO PROGRAMADA)([ ][0-9,%]+){2}[ ]([0-9,.]+)',texto) != None:
        religacao = format_number(re.search('(RELIGAÇÃO PROGRAMADA)([ ][0-9,%]+){2}[ ]([0-9,.]+)',texto).group(3))
    else:
        religacao = 0
    
    if re.search('(DESLIGAMENTO PROGRAMADO)([ ][0-9,%]+){2}[ ]([0-9,.]+)',texto) != None:
        desligamento = format_number(re.search('(DESLIGAMENTO PROGRAMADO)([ ][0-9,%]+){2}[ ]([0-9,.]+)',texto).group(3))
    else:
        desligamento = 0
    
    if re.search('(PARC\. DEBITO-PRC \- [0-9\/]+ \- [0-9\/]+)[ ]([0-9,.]+)',texto) != None:
        debito = format_number(re.search('(PARC\. DEBITO-PRC \- [0-9\/]+ \- [0-9\/]+)[ ]([0-9,.]+)',texto).group(2))
    else:
        debito = 0

    if re.search('(COMPENSACAO DE FIC ANUAL )[ \-]([\-0-9,.]+)',texto) != None:
        compensacao_fic_anual = format_number(re.search('(COMPENSACAO DE FIC ANUAL )[ \-]([\-0-9,.]+)',texto).group(2))*-1
    else:
        compensacao_fic_anual = 0
    
    if re.search('(COMPENSACAO DE DIC ANUAL )[ \-]([\-0-9,.]+)',texto) != None:
        compensacao_dic_anual = format_number(re.search('(COMPENSACAO DE DIC ANUAL )[ \-]([\-0-9,.]+)',texto).group(2))*-1
    else:
        compensacao_dic_anual = 0
    
    if re.search('(COMPENSAÇÃO DE DIC MENSAL )[ \-]([\-0-9,.]+)',texto) != None:
        compensacao_dic_mensal = format_number(re.search('(COMPENSAÇÃO DE DIC MENSAL )[ \-]([\-0-9,.]+)',texto).group(2))*-1
    else:
        compensacao_dic_mensal = 0

    if re.search('(COMPENSAÇÃO DE FIC MENSAL )[ \-]([\-0-9,.]+)',texto) != None:
        compensacao_fic_mensal = format_number(re.search('(COMPENSAÇÃO DE FIC MENSAL )[ \-]([\-0-9,.]+)',texto).group(2))*-1
    else:
        compensacao_fic_mensal = 0
    
    compesacoes = taxa + compensacao_dic_mensal + compensacao_fic_mensal + compensacao_dic_anual + compensacao_fic_anual + religacao + desligamento + debito
    return compesacoes

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
    
    if re.search(r'(VAL[A-Z ÇÃ.]+)([\-0-9,.]+)',texto) != None:
        multa += format_number(re.search(r'(VALOR [A-Z ÇÃ.]+)([\-0-9,.]+)',texto).group(2))
    else:
        pass

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

def conferir(precos,texto):
    """
    Verifica se a soma dos valores coletados está de acordo com o custo total da fatura \n
    Retorna uma lista com a soma dos valores coletados, o valor total lido na fatura e uma flag para identificar se está de acordo ou não [valor calculado, valor total, flag]
    """
    preco_total = format_number(re.search('(R\$)[\*]+([0-9,.]+)',texto).group(2))
    preco_calculado = 0 
    for preco in precos:
        preco_calculado += preco
    if (preco_calculado >= preco_total-0.05) and (preco_calculado <= preco_total+0.05):
        flag_confere = 'CONFERE'
    else:
        flag_confere = 'NÃO CONFERE'
        print("erro")
    conferir = [preco_calculado,preco_total,flag_confere]
    return conferir