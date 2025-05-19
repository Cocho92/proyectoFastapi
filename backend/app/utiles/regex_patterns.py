# Patrones predefinidos para identificar diferentes tipos de errores
PATRONES_DEFAULT = [
    #1 Fecha/Hora Medicación Fuera de Rango internacion
    r'Fecha/Hora Medicación: (\d{2}/\d{2}/\d{4} \d{2}:\d{2})[^:]+: (\d{2}/\d{2}/\d{4} \d{2}:\d{2}) Nº Afiliado: (\d+), F.Int.: (\d{2}/\d{2}/\d{4})',
    #2 Practica a Transmitir por Panel OME
    r'Amb\. PANEL OME Práctica (\d+) Mód\. (\d+) OME Nº (\d+) con TURNO sin TRANSMITIR a través del PANEL OME, en Nº afil: (\d+) , Fecha.: (\d{2}/\d{2}/\d{4})',
    #3 Practicas Excluyentes
    r'Int\. Práct\. Excluyente Códigos: (\d+-\d+) en Nº afil: (\d+) Fecha: (\d{2}/\d{2}/\d{4})',
    #4 Practicas Amb Fuera de Rango
    r'^Amb\. Práctica Fuera de Rango Diario:*',
    #5 Solapamiento Ambulatorio Internado
    r'Solapamiento Ambulatorio/Internado*',
    #6 Sin Cuit
    r'SIN CUIT*',
    #7 Practicas deben ser transmitidas por OME
    r'Amb\. Práctica \d+ Mód\. \d+ SI debe ser transmitido a través del PANEL OME',
    #8 Fecha de Realizacion Fuera de rango Practica
    r'Fecha de Realiz.: \d{2}/\d{2}/\d{4} \d{2}:\d{2} Fuera de Rango para la práct.',
    #9 Cantidad de Horas internado
    r'Int\. Area \b\w+ \d{1,2} dias (?!(?:4|5|22|23)\b)\d{1,2} hs',
    #10 Fuera de rango diario
    r'Int\. Práctica Fuera de Rango (Diario|Mensual): \d+',
    #11 Practica internacion fuera del rango de la internacion
    r'Fecha/Hora Alta: \d{2}/\d{2}/\d{4} \d{2}:\d{2} Anterior a F/H Realización: \d{2}/\d{2}/\d{4} \d{2}:\d{2}'
]