import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import time

class Geocodificador:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="RotasWizard_Final_Project_2026")
        self.ESTADOS_BR = {
            "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM", "Bahia": "BA",
            "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES", "Goiás": "GO",
            "Maranhão": "MA", "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG",
            "Pará": "PA", "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE", "Piauí": "PI",
            "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS",
            "Rondônia": "RO", "Roraima": "RR", "Santa Catarina": "SC", "São Paulo": "SP",
            "Sergipe": "SE", "Tocantins": "TO"
        }

    def buscar_coordenadas(self, endereco):
        """Converte o endereço final selecionado em coordenadas (Lat, Lon)."""
        try:
            time.sleep(1)
            localizacao = self.geolocator.geocode(endereco)
            if localizacao:
                return (localizacao.latitude, localizacao.longitude)
            return None
        except GeopyError:
            return None

    def buscar_sugestoes(self, busca: str):
        """Busca sugestões e formata no padrão Google Maps."""
        busca_limpa = busca.strip() if busca else ""
        if not busca_limpa or len(busca_limpa) < 3:
            return []
            
        url = "https://photon.komoot.io/api"
        params = {"q": busca_limpa, "limit": 5}
        headers = {"User-Agent": "Mozilla/5.0 RotasWizard/1.1"}
        
        try:
            print(f"📡 Solicitando: '{busca_limpa}'...")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                sugestoes = []
                
                for feature in data.get('features', []):
                    p = feature.get('properties', {})
                    rua = p.get('street', p.get('name', ''))
                    numero = p.get('housenumber', '')
                    bairro = p.get('district', p.get('suburb', ''))
                    cidade = p.get('city', '')
                    est_longo = p.get('state', '')
                    uf = self.ESTADOS_BR.get(est_longo, est_longo)
                    cep = p.get('postcode', '')

                    # Formatação Estilo Google
                    end = f"{rua}"
                    if numero: end += f", {numero}"
                    if bairro: end += f" - {bairro}"
                    if cidade: end += f", {cidade}"
                    if uf: end += f" - {uf}"
                    if cep: end += f", {cep}"

                    if end not in sugestoes:
                        sugestoes.append(end)
                
                print(f"✅ {len(sugestoes)} opções encontradas.")
                return sugestoes
            else:
                print(f"⚠️ API Status: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return []