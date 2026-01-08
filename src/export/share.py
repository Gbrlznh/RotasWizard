import urllib.parse
import qrcode
from io import BytesIO

def gerar_link_google_maps(itinerario):
    """
    Gera um link de navegação para o Google Maps com múltiplas paradas.
    """
    # Base da URL para rotas (dirigindo)
    base_url = "https://www.google.com/maps/dir/?api=1&"
    
    origin = itinerario[0]
    destination = itinerario[-1]
    
    # Se houver paradas intermediárias, elas entram como 'waypoints'
    if len(itinerario) > 2:
        waypoints = "|".join(itinerario[1:-1])
        params = {
            'origin': origin,
            'destination': destination,
            'waypoints': waypoints,
            'travelmode': 'driving'
        }
    else:
        params = {
            'origin': origin,
            'destination': destination,
            'travelmode': 'driving'
        }
        
    return base_url + urllib.parse.urlencode(params)

def gerar_qr_code(url):
    """
    Gera um objeto de imagem QR Code a partir de uma URL.
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converte a imagem para um formato que o Streamlit consegue ler (Bytes)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()