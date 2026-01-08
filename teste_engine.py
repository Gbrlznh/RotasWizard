import osmnx as ox
from src.engine.dijkstra import RouteEngine
from src.engine.graph_utils import GraphManager

def testar_modos_de_rota():
    print("🚀 Iniciando Teste de Estresse do Motor de Cálculo...")
    
    # 1. Configuração inicial
    engine = RouteEngine()
    manager = GraphManager()
    
    # Coordenadas de teste (Ex: São Paulo - MASP)
    ponto_teste = (-23.5615, -46.6559) 
    
    # 2. Configurações de Veículo (Cenário de combustível caro)
    config = {
        'preco_combustivel': 6.50,
        'consumo_urbano': 7.0,
        'consumo_pista': 11.0
    }

    print("🛰️ Baixando mapa local para o teste...")
    G = manager.obter_mapa_por_ponto(ponto_teste, raio=3000)
    
    if G is None:
        print("❌ Erro ao baixar o mapa.")
        return

    # Definimos dois pontos aleatórios no grafo para cruzar
    nodes = list(G.nodes())
    origem = nodes[0]
    destino = nodes[-1]

    print("-" * 50)
    print(f"{'MODO':<15} | {'PESO TOTAL':<12}")
    print("-" * 50)

    # 3. Execução dos 3 modos e comparação de "Peso"
    modos = ['economico', 'rapido', 'equilibrado']
    
    for modo in modos:
        rota = engine.encontrar_melhor_rota(G, origem, destino, modo, config)
        
        # Calculamos o peso final somando os pesos das arestas da rota
        peso_total = 0
        for u, v in zip(rota[:-1], rota[1:]):
            edge_data = G.get_edge_data(u, v)[0]
            peso_total += engine.calcular_peso_estrada(u, v, edge_data, modo, config)
        
        print(f"{modo.capitalize():<15} | {peso_total:<12.4f}")

    print("-" * 50)
    print("✅ Teste concluído. Se os valores acima forem diferentes, a inteligência financeira está ativa!")

if __name__ == "__main__":
    testar_modos_de_rota()