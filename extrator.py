import re

def format_number(num):
    num = num.replace('.','')
    num = num.replace(',','.')
    return float(num)

def get_data(texto):
    mes,ano = re.search('([A-Z]{3})[\/]([0-9]{4})',texto).groups()
    data = [mes,ano]
    return data

def get_demanda_contratada(texto):
    return format_number(re.search(r'(DEMANDA \- kW )([0-9]+)\n',texto).group(2))

def get_demanda_hp(texto):
    demanda_P = format_number(re.search(r'(DEMANDA \- KW )[\-,A-Z0-9a-z]+[ ]([0-9,.]+)',texto).group(2))
    return demanda_P

def get_demanda_hfp(texto):
    preco_demanda = format_number(re.search(r'(DEMANDA kW )([,\-A-Z0-9%a-z]+[ ]){7}([0-9]+[.,][,0-9]+)\n',texto).group(3))
    demanda = format_number(re.search(r'(DEMANDA )[\-A-Z,0-9]+[ ][\-A-Z,0-9]+[ ][\-A-Z,0-9]+[ ]([1-9][0-9,.]+)[ \-A-Z,0-9]+(FORA PONTA)',texto).group(2))
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

def get_consumo_hp(texto,gen):
    if gen:
        consumo_p = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[0-9 ,%]+[ ]([0-9.,]+)\n',texto).group(2))
        preco_consumo_p = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[0-9 ,%]+[ ]([0-9.,]+)\n',texto).group(3))
        parcela_te_p = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA P - PARC.[\n -,\-])[ ,\-A-Z,0-9%a-z]+[ ]([.,0-9]+)\n',texto).group(2))
    else:
        consumo_p = format_number(re.search(r'(CONSUMO P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([.0-9,]+)\n',texto).group(2))
        preco_consumo_p = format_number(re.search(r'(CONSUMO P [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([.0-9,]+)\n',texto).group(3))
        parcela_te_p = format_number(re.search(r'(PARCELA TE P)[ ,\-A-Z,0-9%a-z]+[ ]([.,0-9]+)',texto).group(2))
    preco_consumo_p = preco_consumo_p + parcela_te_p
    con_hp = [consumo_p,preco_consumo_p]
    return con_hp

def get_consumo_hfp(texto,gen):
    if gen:
        consumo_fp = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA FP [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)',texto).group(2))
        preco_consumo_fp = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA FP [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)',texto).group(3))
        consumo_r = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA HR [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)',texto).group(2))
        preco_consumo_r = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA HR [ \-a-zA-Z]+)[0-9,]+[ ]([.0-9,]+)[ ]([.0-9,]+)',texto).group(3))
        parcela_te_fp = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA FP - PARC.[\n -,\-])[ ,\-A-Z,0-9%a-z]+[ ]([.,0-9]+)\n',texto).group(2))
        parcela_te_r = format_number(re.search(r'(ENERGIA ATIVA FORNECIDA HR - PARC.[\n -,\-])[ ,\-A-Z,0-9%a-z]+[ ]([.,0-9]+)\n',texto).group(2))
    else:
        consumo_fp = format_number(re.search(r'(CONSUMO FP kWh )[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)\n',texto).group(2))
        preco_consumo_fp = format_number(re.search(r'(CONSUMO FP kWh )[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)\n',texto).group(3))
        consumo_r = format_number(re.search(r'(CONSUMO HR kWh )[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)\n',texto).group(2))
        preco_consumo_r = format_number(re.search(r'(CONSUMO HR kWh )[0-9,]+[ ]([.0-9,]+)[ ][ 0-9,%]+[ ]([0-9][.,\][0-9,\,]+)\n',texto).group(3))
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
                bandeira_hr = format_number(re.search(r'(AD. BAND. VERMELHA EN. ATIVA FORN. HR - PARC. )([ ,\-,A-Z,0-9,%,a-z]+[ ]){2}([0-9,.]+)',texto).group(3))
                bandeira_hfp = format_number(re.search(r'(AD. BAND. VERMELHA EN. ATIVA FORN. FP - PARC. )([ ,\-,A-Z,0-9,%,a-z]+[ ]){2}([0-9,.]+)',texto).group(3))
                bandeira_hp = format_number(re.search(r'(AD. BAND. VERMELHA EN. ATIVA FORN. P - PARC. )([ ,\-,A-Z,0-9,%,a-z]+[ ]){2}([0-9,.]+)',texto).group(3))
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

def get_energia_reativa(texto):
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