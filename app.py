import streamlit as st
import pandas as pd

from config.settings import PAGE_CONFIG, CACHE_TTL
from config.styles import DARK_THEME_CSS
from services.google_sheets import GoogleSheetsService
from services.data_loader import DataLoader
from services.stats_service import StatsService
from services.exceptions import (
    AppError, 
    DataConnectionError, 
    DataPermissionError, 
    DataValidationError, 
    DataNotFoundError
)
from utils.coordinates import processar_coordenadas
from components.maps import MapaBlocos, MapaLotes, Mapa3D, MapaCalor
from components.legend import exibir_legenda
from components.statistics import exibir_estatisticas_lotes, exibir_resumo_bloco
from config.constants import CORES_FOLIUM, ICONES_USO_LOTE, FOLIUM_OK_COLORS, SUGGESTED_ICONS


# Configuração da página
st.set_page_config(**PAGE_CONFIG)

# Aplicar tema escuro
st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)


# --- Funções de Cache Wrapper ---

@st.cache_data(ttl=CACHE_TTL)
def get_blocos_data(_loader: DataLoader) -> pd.DataFrame:
    """Wrapper com cache para carregar dados de blocos."""
    return _loader.carregar_dados_blocos()


@st.cache_data(ttl=CACHE_TTL)
def get_lotes_data(_loader: DataLoader) -> pd.DataFrame:
    """Wrapper com cache para carregar dados de lotes."""
    return _loader.carregar_dados_lotes()


@st.cache_data(ttl=CACHE_TTL)
def processar_dados_cached(df: pd.DataFrame) -> pd.DataFrame:
    """Wrapper com cache para processamento de coordenadas."""
    return processar_coordenadas(df)


@st.cache_data(ttl=CACHE_TTL)
def enrich_blocos_cached(df_blocos: pd.DataFrame, df_lotes: pd.DataFrame) -> pd.DataFrame:
    """Wrapper com cache para enriquecimento estatístico."""
    return StatsService.enrich_blocos_data(df_blocos, df_lotes)


def render_customization_ui(key_prefix, title, default_colors, default_icons):
    """Renderiza controles de customização na barra lateral."""
    with st.expander(title, expanded=False):
        st.markdown("Customize cores e ícones para cada categoria.")
        new_colors = default_colors.copy()
        new_icons = default_icons.copy()
        
        # Iterar sobre as chaves existentes (Tipos de Uso)
        for usage in default_colors.keys():
            st.caption(f"**{usage}**")
            c1, c2 = st.columns(2)
            
            # Cor
            current_color = default_colors.get(usage, 'gray')
            idx_color = FOLIUM_OK_COLORS.index(current_color) if current_color in FOLIUM_OK_COLORS else 0
            new_colors[usage] = c1.selectbox(
                "Cor", 
                options=FOLIUM_OK_COLORS, 
                index=idx_color, 
                key=f"{key_prefix}_color_{usage}",
                label_visibility="collapsed"
            )
            
            # Ícone
            current_icon = default_icons.get(usage, 'info-sign')
            idx_icon = SUGGESTED_ICONS.index(current_icon) if current_icon in SUGGESTED_ICONS else 0
            new_icons[usage] = c2.selectbox(
                "Ícone", 
                options=SUGGESTED_ICONS, 
                index=idx_icon, 
                key=f"{key_prefix}_icon_{usage}",
                label_visibility="collapsed"
            )
        return new_colors, new_icons


# --- Main ---

def main():
    st.title("🗺️ Mapeamento Urbano - Bairro Brasília")
    st.markdown("**Altamira/PA** - 80 Quarteirões catalogados")
    
    # Sidebar para controles globais
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Botão de atualização
        if st.button("🔄 Atualizar Mapa", use_container_width=True):
            st.cache_data.clear()
            st.success("Dados atualizados com sucesso!")
            st.rerun()
            
        st.divider()

        # Customização Blocos
        custom_colors_blocos, custom_icons_blocos = render_customization_ui(
            "blocos", "🎨 Personalização - Blocos", CORES_FOLIUM, ICONES_USO_LOTE
        )
        
        # Customização Lotes
        custom_colors_lotes, custom_icons_lotes = render_customization_ui(
            "lotes", "🎨 Personalização - Lotes", CORES_FOLIUM, ICONES_USO_LOTE
        )
        
        st.divider()
        
        # Tamanho dos pinos
        pin_size = st.slider("Tamanho dos Pinos (3D/Círculos):", 10, 100, 30, help="Ajusta o tamanho dos marcadores no mapa.")
        st.session_state["pin_size"] = pin_size

    st.markdown("---")
    
    try:
        # 1. Injeção de Dependência (Composition Root)
        # Tenta obter credenciais de st.secrets (com fallback para raiz)
        creds_dict = None
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
        elif "private_key" in st.secrets:
            creds_dict = st.secrets
            
        sheets_service = GoogleSheetsService(credentials_dict=creds_dict)
        data_loader = DataLoader(sheets_service)
        
        # 2. Carregar dados (usando wrappers com cache)
        # Note: hash_funcs podem ser necessárias se DataLoader não for hashable, 
        # mas aqui usamos _loader (leading underscore) para evitar hash do objeto se desejado,
        # ou o Streamlit tentará hashear. Como DataLoader só tem ref para service, pode ser ok.
        # Se falhar hash, usamos _loader no parametro para pular hash.
        
        with st.spinner("Carregando dados..."):
            df_blocos = get_blocos_data(data_loader)
            df_lotes = get_lotes_data(data_loader)
        
        # 3. Processamento (Pure functions)
        try:
            if df_blocos is not None and not df_blocos.empty:
                df_blocos = processar_dados_cached(df_blocos)
            
            if df_lotes is not None and not df_lotes.empty:
                df_lotes = processar_dados_cached(df_lotes)

            # 4. Enriquecimento de Dados (Business Logic)
            if df_blocos is not None and not df_blocos.empty:
                # O StatsService lida com df_lotes sendo None/Vazio internamente se necessário
                df_blocos = enrich_blocos_cached(df_blocos, df_lotes)
                
        except ValueError as ve:
            # Captura erro de validação de coordenadas
            raise DataValidationError(f"Erro ao processar coordenadas: {str(ve)}")
            
        # --- Configurações de Filtro (Compartilhadas entre 2D e 3D) ---
        usos_disponiveis = ["Todos"] + sorted(df_lotes["uso_lote"].unique().tolist()) if df_lotes is not None else []
        uso_selecionado = st.sidebar.selectbox("Filtrar por Uso:", usos_disponiveis)
        
        df_lotes_filtrado = df_lotes
        if df_lotes is not None and uso_selecionado != "Todos":
            df_lotes_filtrado = df_lotes[df_lotes["uso_lote"] == uso_selecionado]

        # 4. Interface do Usuário
        tab_blocos, tab_lotes, tab_3d, tab_calor = st.tabs(["🏘️ Blocos", "📍 Lotes", "🧊 Mapa 3D", "🔥 Mapa de Calor"])
        
        with tab_blocos:
            st.header("Mapa de Blocos")
            st.markdown("Visualização dos 80 blocos catalogados no bairro Brasília.")
            
            if df_blocos is not None and not df_blocos.empty:
                st.success(f"✅ {len(df_blocos)} blocos carregados!")
                mapa_blocos = MapaBlocos(
                    df_blocos, 
                    df_lotes, 
                    colors_config=custom_colors_blocos, 
                    icons_config=custom_icons_blocos
                )
                mapa_blocos.renderizar()

                st.markdown("---")
                
                # Filtro por Bloco
                st.subheader("🔍 Detalhes por Bloco")
                blocos_ids = sorted(df_blocos["id_bloco"].unique().tolist())
                bloco_selecionado = st.selectbox("Selecione um bloco para detalhamento:", blocos_ids)
                
                if df_lotes is not None:
                    df_bloco_info = df_lotes[df_lotes["id_bloco"] == bloco_selecionado]
                    exibir_resumo_bloco(df_bloco_info, bloco_selecionado)
            else:
                st.info("Nenhum dado de blocos disponível.")
        
        with tab_lotes:
            st.header("Mapa de Lotes")
            st.markdown(f"Visualização de lotes ({uso_selecionado}).")
            
            if df_lotes_filtrado is not None and not df_lotes_filtrado.empty:
                st.success(f"✅ {len(df_lotes_filtrado)} lotes exibidos!")
                
                mapa_lotes = MapaLotes(
                    df_lotes_filtrado,
                    colors_config=custom_colors_lotes,
                    icons_config=custom_icons_lotes
                )
                mapa_lotes.renderizar()
                exibir_legenda()
                exibir_estatisticas_lotes(df_lotes_filtrado)
            else:
                st.info("Nenhum dado de lotes disponível para este filtro.")

        with tab_3d:
            st.header("Visualização 3D")
            st.markdown(f"Perspectiva tridimensional ({uso_selecionado}).")
            
            if df_lotes_filtrado is not None and not df_lotes_filtrado.empty:
                mapa_3d = Mapa3D(df_lotes_filtrado, pin_size=st.session_state.get("pin_size", 30))
                mapa_3d.renderizar()
            else:
                st.info("Dados insuficientes para visualização 3D.")

        with tab_calor:
            if df_lotes is not None:
                # 1. Definir opções
                todos_usos = sorted(list(set(df_lotes['uso_lote'].dropna().unique())))
                
                # 2. Definir padrão (Empresarial, Misto, Institucional - validando existência)
                # TIPOS_USO_COMERCIAL já inclui Institucional após atualização
                from config.constants import TIPOS_USO_COMERCIAL
                default_usos = [u for u in TIPOS_USO_COMERCIAL if u in todos_usos]
                
                # Se a lista padrão estiver vazia (nomes diferentes?), selecionar os 3 primeiros
                if not default_usos and todos_usos:
                    default_usos = todos_usos[:3]

                # 3. Widget de multiselect
                usos_calor = st.multiselect(
                    "Selecione os Tipos de Uso para o Mapa de Calor:",
                    options=todos_usos,
                    default=default_usos,
                    key="multiselect_calor"
                )
                
                # 4. Renderizar mapa
                mapa_calor = MapaCalor(df_lotes, usos_selecionados=usos_calor)
                mapa_calor.renderizar()

    # --- Tratamento Granular de Erros ---
    except DataConnectionError as e:
        st.error(f"""
        ⚠️ **Erro de Conexão**
        
        Não foi possível conectar ao Google Sheets.
        Detalhe: {e}
        
        Verifique sua internet e tente novamente.
        """)
        
    except DataPermissionError as e:
        st.error(f"""
        🔒 **Acesso Negado**
        
        O sistema não tem permissão para acessar a planilha.
        Verifique se o e-mail da conta de serviço foi adicionado à planilha.
        Detalhe: {e}
        """)
        
    except DataNotFoundError as e:
        st.error(f"""
        📄 **Dados não encontrados**
        
        A planilha ou aba solicitada não existe.
        Detalhe: {e}
        """)
        
    except DataValidationError as e:
        st.error(f"""
        ❌ **Erro nos Dados**
        
        A estrutura dos dados na planilha não está conforme o esperado.
        Detalhe: {e}
        """)
        
    except AppError as e:
        st.error(f"Erro na aplicação: {e}")
        
    except Exception as e:
        st.error(f"⚠️ Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()
