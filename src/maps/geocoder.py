from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import time

class Geocodificador:
    def __init__(self):
        # O user_agent é obrigatório para identificar sua aplicação no serviço gratuito
        self.geolocator = Nominatim(user_agent="logistica_pro_app")

    def buscar_coordenadas(self, endereco):
        """
        Recebe uma string de endereço e retorna uma tupla (latitude, longitude).
        """
        try:
            # Adicionamos um pequeno delay para respeitar os termos de uso do Nominatim
            time.sleep(1) 
            
            localizacao = self.geolocator.geocode(endereco)
            
            if localizacao:
                print(f"✅ Endereço encontrado: {localizacao.address}")
                return (localizacao.latitude, localizacao.longitude)
            else:
                print(f"❌ Endereço não encontrado: {endereco}")
                return None
                
        except GeopyError as e:
            print(f"⚠️ Erro na geocodificação: {e}")
            return None

# Exemplo rápido para teste manual
if __name__ == "__main__":
    geo = Geocodificador()
    resultado = geo.buscar_coordenadas("MASP, São Paulo, Brasil")
    print(f"Resultado: {resultado}")