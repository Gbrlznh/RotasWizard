import streamlit as st

def aplicar_estilos_customizados():
    st.markdown("""
        <style>
        /* Estilo Dark e Cores Logísticas */
        .main { background-color: #0E1117; }
        h1, h2, h3 { color: #FFA500 !important; }
        
        /* Customização da Tabela */
        table {
            width: 100%;
            border-radius: 10px;
            margin-top: 10px;
        }
        th { background-color: #1E1E1E !important; color: white !important; }
        
        /* Métricas */
        [data-testid="stMetricValue"] { color: #FFA500; }
        
        /* Botões */
        .stButton>button {
            border-radius: 8px;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            border-color: #FFA500;
            color: #FFA500;
        }
        </style>
    """, unsafe_allow_html=True)