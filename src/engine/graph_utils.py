import osmnx as ox

class GraphManager:
    def __init__(self):
        # Cache para não baixar o mesmo mapa várias vezes
        ox.settings.use_cache = True
        ox.settings.log_console = False

    def obter_mapa_por_ponto(self, coordenadas, raio=15000):
        """
        Baixa o mapa de ruas ao redor de um ponto específico.
        """
        try:
            # Baixa o grafo de vias dirigíveis
            G = ox.graph_from_point(coordenadas, dist=raio, network_type='drive')
            # Adiciona velocidades e tempos de viagem baseados nas tags das vias
            G = ox.add_edge_speeds(G)
            G = ox.add_edge_travel_times(G)
            return G
        except Exception as e:
            print(f"Erro ao baixar mapa: {e}")
            return None