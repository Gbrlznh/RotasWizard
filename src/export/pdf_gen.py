from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
from io import BytesIO

def gerar_pdf_manifesto(itinerario, distancia, custo, modo):
    """
    Gera um PDF profissional com os dados da rota.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    # --- CABEÇALHO ---
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, altura - 50, "MANIFESTO DE VIAGEM - LOGÍSTICA PRO")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, altura - 70, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    p.line(50, altura - 75, largura - 50, altura - 75)

    # --- RESUMO FINANCEIRO ---
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, altura - 100, "Resumo da Rota:")
    p.setFont("Helvetica", 11)
    p.drawString(60, altura - 120, f"Modo de Otimização: {modo.capitalize()}")
    p.drawString(60, altura - 135, f"Distância Total: {distancia:.2f} km")
    p.drawString(60, altura - 150, f"Custo Estimado de Combustível: R$ {custo:.2f}")

    # --- ITINERÁRIO (ORDEM DE ENTREGA) ---
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, altura - 180, "Ordem das Paradas:")
    
    y = altura - 205
    p.setFont("Helvetica", 10)
    for i, local in enumerate(itinerario):
        prefixo = "INÍCIO" if i == 0 else "FINAL" if i == len(itinerario)-1 else f"PARADA {i}"
        p.drawString(60, y, f"[  ] {prefixo}: {local}")
        y -= 20 # Espaçamento entre linhas
        
        if y < 100: # Cria nova página se estiver sem espaço
            p.showPage()
            y = altura - 50

    # --- ASSINATURA ---
    p.line(50, 100, 250, 100)
    p.drawString(50, 85, "Assinatura do Motorista")
    
    p.line(largura - 250, 100, largura - 50, 100)
    p.drawString(largura - 250, 85, "Data e Horário de Saída")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer