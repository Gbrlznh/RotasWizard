import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import pandas as pd
from datetime import datetime
from streamlit_searchbox import st_searchbox

# Importações dos seus módulos internos
from src.engine.dijkstra import RouteEngine
from src.maps.geocoder import Geocodificador
from src.export.share import gerar_link_google_maps, gerar_qr_code
from src.export.pdf_gen import gerar_pdf_manifesto
from src.ui.styles import aplicar_estilos_customizados

st.set_page_config(page_title="RotasWizard - Debug Mode", page_icon="🚚", layout="wide")
aplicar_estilos_customizados()

if 'paradas' not in st.session_state:
    st.session_state.paradas = []

engine = RouteEngine()
geo = Geocodificador()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Configurações")
    preco_comb = st.number_input("Preço Combustível (R$)", value=5.85, step=0.01)
    cons_urbano = st.number_input("Consumo Urbano (km/L)", value=8.5, step=0.1)
    cons_pista = st.number_input("Consumo Rodoviário (km/L)", value=12.5, step=0.1)
    modo_selecionado = st.selectbox("Estratégia", ["economico", "rapido", "equilibrado"])

st.title("🚚 RotasWizard: Inteligência Logística")
col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("📍 Itinerário")
    origem_txt = st_searchbox(geo.buscar_sugestoes, key="search_origem", placeholder="Origem...")
    
    for i in range(len(st.session_state.paradas)):
        st.session_state.paradas[i] = st_searchbox(geo.buscar_sugestoes, key=f"search_stop_{i}", placeholder=f"Parada {i+1}...")
    
    if st.button("➕ Add Parada"):
        st.session_state.paradas.append("")
        st.rerun()
            
    destino_txt = st_searchbox(geo.buscar_sugestoes, key="search_destino", placeholder="Destino Final...")
    btn_calc = st.button("🚀 Calcular Rota", use_container_width=True, type="primary")

# --- BLOCO DE DEBUG E PROCESSAMENTO ---
if btn_calc:
    print("\n" + "="*50)
    print("🚀 INICIANDO DEBUG DE CÁLCULO")
    
    if origem_txt and destino_txt:
        itinerario = [origem_txt] + [p for p in st.session_state.paradas if p] + [destino_txt]
        print(f"📍 Itinerário Selecionado: {itinerario}")
        
        with st.spinner("Geocodificando endereços..."):
            coords = []
            for local in itinerario:
                c = geo.buscar_coordenadas(local)
                print(f"🔍 Buscando Coordenadas para '{local}': {c}")
                if c: coords.append(c)
            
            if len(coords) == len(itinerario):
                print(f"✅ Todas as coordenadas obtidas: {coords}")
                try:
                    # Carregamento do Mapa (Aumentado para 20km para evitar erro de borda)
                    print("🗺️ Baixando grafo das ruas (isso pode demorar)...")
                    G = ox.graph_from_point(coords[0], dist=20000, network_type='drive')
                    G = ox.add_edge_speeds(G)
                    G = ox.add_edge_travel_times(G)
                    print("✅ Grafo carregado com sucesso.")

                    config = {'preco_combustivel': preco_comb, 'consumo_urbano': cons_urbano, 'consumo_pista': cons_pista}
                    
                    resumo = []
                    for m in ["economico", "rapido", "equilibrado"]:
                        dist_m = 0
                        tempo_s = 0
                        rota_final_nodes = []
                        
                        for j in range(len(coords) - 1):
                            n1 = ox.nearest_nodes(G, coords[j][1], coords[j][0])
                            n2 = ox.nearest_nodes(G, coords[j+1][1], coords[j+1][0])
                            print(f"🛣️ Calculando segmento {j+1}: Nó {n1} para Nó {n2} ({m})")
                            
                            seg = engine.encontrar_melhor_rota(G, n1, n2, m, config)
                            
                            # CORREÇÃO OSMNX VERSÃO NOVA:
                            edges_data = ox.routing.route_to_gdf(G, seg)
                            dist_m += edges_data['length'].sum()
                            tempo_s += edges_data['travel_time'].sum()
                            
                            if m == modo_selecionado:
                                if j == 0: rota_final_nodes.extend(seg)
                                else: rota_final_nodes.extend(seg[1:])

                        km = dist_m / 1000
                        custo = (km / ((cons_urbano + cons_pista)/2)) * preco_comb
                        resumo.append({"Perfil": m.capitalize(), "KM": f"{km:.2f}", "Custo": f"R$ {custo:.2f}"})
                        
                        if m == modo_selecionado: 
                            d_final, c_final, nodes_plot = km, custo, rota_final_nodes

                    with col_out:
                        st.table(pd.DataFrame(resumo))
                        st.metric("Custo Total", f"R$ {c_final:.2f}")
                        st_folium(ox.plot_route_folium(G, nodes_plot, color='orange'), width=750)
                        print("✨ Rota renderizada com sucesso.")

                except Exception as e:
                    print(f"❌ ERRO NO MOTOR: {e}")
                    st.error(f"Erro no processamento geográfico: {e}")
            else:
                print(f"⚠️ FALHA: Obtidas {len(coords)} de {len(itinerario)} coordenadas.")
                st.error("Endereços não localizados. Tente selecionar novamente nas sugestões.")
    else:
        st.warning("Preencha origem e destino.")
    print("="*50 + "\n")