import networkx as nx

class RouteEngine:
    def __init__(self):
        # Fator de importância do tempo no modo equilibrado (R$ por hora)
        self.valor_hora_padrao = 50.0 

    def calcular_peso_estrada(self, u, v, data, modo, config):
        """
        Calcula o 'custo' de atravessar uma rua específica.
        config deve conter: preco_combustivel, consumo_urbano, consumo_pista
        """
        distancia = data.get('length', 0) / 1000  # Converte metros para km
        velocidade_max = data.get('speed_kph', 40) # Velocidade da via ou padrão 40km/h
        
        # 1. Determina se é cidade ou pista baseado na velocidade
        # Geralmente, acima de 70km/h consideramos rodovia/pista
        if velocidade_max > 70:
            consumo = config['consumo_pista']
        else:
            consumo = config['consumo_urbano']

        # 2. Cálculos base
        custo_combustivel = (distancia / consumo) * config['preco_combustivel']
        tempo_horas = distancia / velocidade_max
        
        # 3. Aplicação dos Modos
        if modo == 'economico':
            # Foco total no custo financeiro (Combustível + Pedágios se houver)
            # Adicionamos uma pequena penalidade ao tempo para não escolher rotas infinitas
            return custo_combustivel + (0.01 * tempo_horas)
        
        elif modo == 'rapido':
            # Foco total no tempo de chegada
            return tempo_horas
        
        elif modo == 'equilibrado':
            # Custo financeiro + Valor do tempo do motorista
            return custo_combustivel + (self.valor_hora_padrao * tempo_horas)
        
        return distancia # Fallback para distância pura

    def encontrar_melhor_rota(self, G, origem, destino, modo, config):
        """
        Executa o Dijkstra no grafo G usando a função de peso customizada.
        """
        rota = nx.shortest_path(
            G, 
            source=origem, 
            target=destino, 
            weight=lambda u, v, d: self.calcular_peso_estrada(u, v, d, modo, config)
        )
        return rota