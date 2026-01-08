import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import pandas as pd
from datetime import datetime

# Importações dos módulos internos
from src.engine.dijkstra import RouteEngine
from src.maps.geocoder import Geocodificador
from src.export.share import gerar_link_google_maps, gerar_qr_code
from src.export.pdf_gen import gerar_pdf_manifesto
from src.ui.styles import aplicar_estilos_customizados

# 1. Configuração Inicial e Estética
st.set_page_config(
    page_title="RotasWizard - Logística Inteligente",
    page_icon="🚚",
    layout="wide"
)

# Aplica o CSS customizado para o modo Dark e tabelas
aplicar_estilos_customizados()

# Inicialização do estado para paradas dinâmicas
if 'paradas' not in st.session_state:
    st.session_state.paradas = []

# Inicialização dos motores técnicos
engine = RouteEngine()
geo = Geocodificador()

# --- BARRA LATERAL: CONFIGURAÇÕES ---
with st.sidebar:
    st.title("⚙️ Painel de Controle")
    st.subheader("Configurações do Veículo")
    preco_comb = st.number_input("Preço do Combustível (R$)", value=5.85, step=0.01)
    cons_urbano = st.number_input("Consumo Urbano (km/L)", value=8.5, step=0.1)
    cons_pista = st.number_input("Consumo Rodoviário (km/L)", value=12.5, step=0.1)
    
    st.divider()
    st.subheader("Estratégia de Cálculo")
    modo_selecionado = st.selectbox(
        "Modo Ativo", 
        options=["economico", "rapido", "equilibrado"],
        index=0,
        format_func=lambda x: x.capitalize()
    )
    st.caption("Ajuste os valores de consumo para que o algoritmo Dijkstra calcule o custo real por trecho.")

# --- COLUNA PRINCIPAL: ENTRADA DE DADOS ---
st.title("🚚 RotasWizard: Inteligência Logística")

col_input, col_output = st.columns([1, 2])

with col_input:
    st.markdown("### 📍 Itinerário de Entrega")
    
    origem_txt = st.text_input("Ponto de Partida", placeholder="Ex: Av. Paulista, 1000, SP")
    
    # Gerenciamento de Paradas Dinâmicas
    st.write("**Paradas Intermediárias**")
    for i in range(len(st.session_state.paradas)):
        st.session_state.paradas[i] = st.text_input(
            f"Parada {i+1}", 
            value=st.session_state.paradas[i], 
            key=f"input_stop_{i}"
        )
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Add Parada", use_container_width=True):
            st.session_state.paradas.append("")
            st.rerun()
    with c2:
        if st.button("➖ Remover", use_container_width=True) and st.session_state.paradas:
            st.session_state.paradas.pop()
            st.rerun()
            
    destino_txt = st.text_input("Destino Final", placeholder="Ex: Porto de Santos, SP")
    
    btn_calcular = st.button("🚀 Calcular Melhor Rota Financeira", use_container_width=True, type="primary")

# --- LÓGICA DE PROCESSAMENTO ---
if btn_calcular:
    if origem_txt and destino_txt:
        with st.spinner("Otimizando custos e analisando vias..."):
            # 1. Preparação da lista de locais
            itinerario = [origem_txt] + [p for p in st.session_state.paradas if p] + [destino_txt]
            
            # 2. Geocodificação
            coords = [geo.buscar_coordenadas(local) for local in itinerario]
            coords = [c for c in coords if c is not None]
            
            if len(coords) >= 2:
                try:
                    # Configurações do usuário para o algoritmo
                    config_user = {
                        'preco_combustivel': preco_comb,
                        'consumo_urbano': cons_urbano,
                        'consumo_pista': cons_pista
                    }

                    # 3. Download do Mapa (Bounding box ao redor dos pontos)
                    G = ox.graph_from_point(coords[0], dist=20000, network_type='drive')
                    G = ox.add_edge_speeds(G)
                    G = ox.add_edge_travel_times(G)

                    # 4. Cálculo Comparativo para a Tabela de UX
                    resumo_comparativo = []
                    for m in ["economico", "rapido", "equilibrado"]:
                        dist_m = 0
                        tempo_s = 0
                        rota_temp_nodes = []
                        
                        for j in range(len(coords) - 1):
                            n1 = ox.nearest_nodes(G, coords[j][1], coords[j][0])
                            n2 = ox.nearest_nodes(G, coords[j+1][1], coords[j+1][0])
                            seg = engine.encontrar_melhor_rota(G, n1, n2, m, config_user)
                            
                            # Acumula dados para o resumo
                            dist_m += sum(ox.utils_graph.get_route_edge_attributes(G, seg, 'length'))
                            tempo_s += sum(ox.utils_graph.get_route_edge_attributes(G, seg, 'travel_time'))
                            if m == modo_selecionado:
                                if j == 0: rota_temp_nodes.extend(seg)
                                else: rota_temp_nodes.extend(seg[1:])

                        d_km = dist_m / 1000
                        # Estimativa de custo baseada no peso do modo
                        cons_base = cons_pista if m == "economico" else cons_urbano
                        custo_estimado = (d_km / cons_base) * preco_comb
                        
                        resumo_comparativo.append({
                            "Perfil": "🌿 Econômico" if m == "economico" else "⚡ Rápido" if m == "rapido" else "⚖️ Equilibrado",
                            "Distância": f"{d_km:.2f} km",
                            "Custo Est.": f"R$ {custo_estimado:.2f}",
                            "Tempo": f"{int(tempo_s/60)} min"
                        })
                        
                        if m == modo_selecionado:
                            rota_final_nodes = rota_temp_nodes
                            distancia_final_km = d_km
                            custo_final_rs = custo_estimado

                    # 5. Exibição dos Resultados (Coluna Direita)
                    with col_output:
                        st.subheader("📊 Matriz de Decisão Logística")
                        df_comp = pd.DataFrame(resumo_comparativo)
                        st.table(df_comp)
                        
                        m1, m2 = st.columns(2)
                        m1.metric("Distância Total", f"{distancia_final_km:.2f} km")
                        m2.metric("Custo da Rota Ativa", f"R$ {custo_final_rs:.2f}")

                        # Renderização do Mapa
                        st.write("**Visualização do Trajeto Selecionado**")
                        mapa_f = ox.plot_route_folium(G, rota_final_nodes, color='#FFA500', weight=5)
                        st_folium(mapa_f, width=800, height=450)

                        # --- SEÇÃO DE EXPORTAÇÃO ---
                        st.divider()
                        exp1, exp2, exp3 = st.columns([1.5, 1.5, 1])
                        
                        with exp1:
                            link_maps = gerar_link_google_maps(itinerario)
                            st.link_button("🌐 Abrir no Google Maps", link_maps, use_container_width=True)
                            
                        with exp2:
                            pdf_data = gerar_pdf_manifesto(itinerario, distancia_final_km, custo_final_rs, modo_selecionado)
                            st.download_button(
                                label="📄 Baixar PDF para Assinatura",
                                data=pdf_data,
                                file_name=f"itinerario_{datetime.now().strftime('%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        with exp3:
                            qr_img = gerar_qr_code(link_maps)
                            st.image(qr_img, caption="Scan para GPS", width=120)

                except Exception as e:
                    st.error(f"Erro no processamento: {e}")
            else:
                st.error("Por favor, informe pelo menos dois endereços válidos.")
    else:
        st.warning("Preencha a origem e o destino para começar.")