import time
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter,landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os, random




def generar_pdf(datos,fecha,idpres,cliente,raiz):
    print(raiz)
    ruta = os.path.join(raiz,'static\pago-{}-{}-{}.pdf'.format(fecha,idpres,random.randrange(1000)))
    doc = SimpleDocTemplate(ruta, pagesize=landscape(letter),
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    Story = []
    logotipo = os.path.join(raiz,'static\python.png')
    nombreRevista = "COMPROBANTE DE PAGO MENSUAL"
    numero = idpres
    formatoFecha = time.ctime()
    nombreCompleto = cliente
    partesDeDireccion = ["Universidad Politecnica Salesiana", "Moran Valverde y Rumichaca"]
    imagen = Image(logotipo, 1 * inch, 1 * inch)
    Story.append(imagen)
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    texto = '%s' % formatoFecha
    Story.append(Paragraph(texto, estilos["Normal"]))
    Story.append(Spacer(1, 12))
    # Se construye la dirección   
    for part in partesDeDireccion:
        texto = '%s' % part.strip()
        Story.append(Paragraph(texto, estilos["Normal"]))
    Story.append(Spacer(1, 12))
    texto = 'Cliente: %s' % nombreCompleto
    Story.append(Paragraph(texto, estilos["Normal"]))
    Story.append(Spacer(1, 12))
    texto = 'Prestamo ID: %s' % idpres
    Story.append(Paragraph(texto, estilos["Normal"]))
    Story.append(Spacer(1, 12))

    texto= 'CUOTA ANUAL|\t\tFECHA PAGO|\t\tINTERES|\t\tAMORTIZACION|\t\tCAP. AMORTIZADO|\n'
    Story.append(Paragraph(texto, estilos["Normal"]))    
    texto2=''
    for dato in datos:
        texto2 += '{}|\t{}|\t{}|\t{}|\t{}|\n\n'.format(dato[3],dato[2],dato[4],dato[5],dato[7])
    Story.append(Paragraph(texto2, estilos["Normal"]))
    Story.append(Spacer(1, 25))
    texto = '-----------------\nFirma Autorizada'
    Story.append(Paragraph(texto, estilos["Normal"]))
    Story.append(Spacer(1, 12))
    doc.build(Story)
    return ruta