import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import pydeck as pdk

from config.settings import MAP_DEFAULT_ZOOM, MAP_TILES
from utils.helpers import hex_to_rgb
from config.constants import CORES_FOLIUM, ICONES_USO_LOTE, CORES_USO_LOTE, TIPOS_USO_COMERCIAL
from utils.html_templates import generate_bloco_popup_html


class MapaBlocos:
    """Componente de mapa para blocos."""
    
    def __init__(self, df: pd.DataFrame, df_lotes: pd.DataFrame = None, 
                 colors_config: dict = None, icons_config: dict = None):
        # A lógica de cálculo foi movida para StatsService.
        # df já deve vir enriquecido com ['total_lotes', 'uso_predominante', 'usos_counts']
        self.df = df
        self.colors_config = colors_config or CORES_FOLIUM
        self.icons_config = icons_config or ICONES_USO_LOTE
    
    def _adicionar_marcadores(self, mapa):
        """Adiciona marcadores ao mapa com estatísticas pré-calculadas."""
        for _, row in self.df.iterrows():
            id_bloco = row.get('id_bloco', row.get('ID', 'N/A'))
            lat = row["latitude"]
            lon = row["longitude"]
            
            # Gerar HTML usando template
            popup_html = generate_bloco_popup_html(
                row.to_dict() # Passa a linha como dict, que já contém usos_counts etc
            )
            
            # Determinar ícone e cor com base no uso predominante (já calculado)
            uso_predominante = row.get('uso_predominante', 'N/A')
            cor_icon = self.colors_config.get(uso_predominante, "gray")
            icon_name = self.icons_config.get(uso_predominante, "info-sign")
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=f"{id_bloco} - {uso_predominante}",
                icon=folium.Icon(color=cor_icon, icon=icon_name, prefix="fa")
            ).add_to(mapa)
    
    def renderizar(self):
        """Renderiza o mapa no Streamlit de forma estável."""
        if self.df is None or self.df.empty:
            st.warning("Nenhum dado disponível para exibir.")
            return

        # Centro inicial se não houver estado
        centro_inicial = [self.df["latitude"].mean(), self.df["longitude"].mean()]
        
        mapa = folium.Map(
            location=centro_inicial,
            zoom_start=MAP_DEFAULT_ZOOM,
            tiles=MAP_TILES
        )
        self._adicionar_marcadores(mapa)
        
        # O segredo para estabilidade no zoom é remover returned_objects
        # Isso evita que o Streamlit recarregue a página a cada pequena interação
        st_folium(
            mapa, 
            key="folium_blocos",
            width=None, 
            height=1000, 
            use_container_width=True,
            returned_objects=[] # Vazio para evitar reruns automáticos no zoom/pan
        )

        st.markdown(f"**Total de Blocos:** {len(self.df)}")


class MapaLotes:
    """Componente de mapa para lotes."""
    
    def __init__(self, df: pd.DataFrame, colors_config: dict = None, icons_config: dict = None):
        self.df = df
        self.colors_config = colors_config or CORES_FOLIUM
        self.icons_config = icons_config or ICONES_USO_LOTE
    
    def _adicionar_marcadores(self, mapa):
        """Adiciona marcadores ao mapa."""
        for _, row in self.df.iterrows():
            uso = row.get("uso_lote", "Desconhecido")
            cor = self.colors_config.get(uso, "gray")
            icone = self.icons_config.get(uso, "map-marker")
            
            nome_fantasia = row.get("nome_fantasia", "")
            endereco = f"{row.get('rua', '')} {row.get('numero', '')}".strip()
            lat = row["latitude"]
            lon = row["longitude"]
            
            popup_html = f"""
            <div style="font-family: Arial; min-width: 200px;">
                <h4 style="margin: 0; color: #333;">{row['id_lote']}</h4>
                <p style="margin: 5px 0; color: #666;">
                    <b>Bloco:</b> {row.get('id_bloco', 'N/A')}<br>
                    <b>Quadra:</b> {row.get('id_quadra', 'N/A')}<br>
                    <b>Uso:</b> <span style="font-weight: bold;">{uso}</span><br>
                    {f'<b>Nome:</b> {nome_fantasia}<br>' if nome_fantasia else ''}
                    <b>Endereço:</b> {endereco if endereco else 'N/A'}<br>
                    <b>Tipologia:</b> {row.get('tipologia', 'N/A')}
                </p>
                <p style="margin: 5px 0; color: #999; font-size: 10px; border-top: 1px solid #ddd; padding-top: 5px;">
                    <b>Coordenadas:</b><br>
                    Lat: {lat:.6f} | Lon: {lon:.6f}
                </p>
            </div>
            """
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{row['id_lote']} - {uso}",
                icon=folium.Icon(color=cor, icon=icone, prefix="fa")
            ).add_to(mapa)
    
    def renderizar(self):
        """Renderiza o mapa no Streamlit de forma estável."""
        if self.df is None or self.df.empty:
            st.warning("Nenhum dado disponível para exibir.")
            return

        centro_inicial = [self.df["latitude"].mean(), self.df["longitude"].mean()]
        
        mapa = folium.Map(
            location=centro_inicial,
            zoom_start=MAP_DEFAULT_ZOOM,
            tiles=MAP_TILES
        )
        
        self._adicionar_marcadores(mapa)
        
        st_folium(
            mapa, 
            key="folium_lotes",
            width=None, 
            height=1000, 
            use_container_width=True,
            returned_objects=[] # Crucial para estabilidade
        )


class Mapa3D:
    """Componente de mapa 3D usando PyDeck."""
    
    def __init__(self, df: pd.DataFrame, pin_size: int = 30):
        self.df = df
        self.pin_size = pin_size
    
    def renderizar(self):
        if self.df is None or self.df.empty:
            st.warning("Nenhum dado disponível para o mapa 3D.")
            return

        # Preparar dados para o PyDeck
        df_pdk = self.df.copy()
        df_pdk["color_rgb"] = df_pdk["uso_lote"].apply(
            lambda x: hex_to_rgb(CORES_USO_LOTE.get(x, "#95a5a6"))
        )
        
        # Camada de Colunas (representando os pins em 3D)
        layer = pdk.Layer(
            "ColumnLayer",
            data=df_pdk,
            get_position=["longitude", "latitude"],
            get_elevation=self.pin_size * 0.5,
            elevation_scale=10,
            radius=self.pin_size / 4,
            get_fill_color="color_rgb",
            pickable=True,
            auto_highlight=True,
        )

        view_state = pdk.ViewState(
            latitude=self.df["latitude"].mean(),
            longitude=self.df["longitude"].mean(),
            zoom=15,
            pitch=45,
            bearing=0
        )

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            height=1000,
            tooltip={
                "html": "<b>Lote:</b> {id_lote}<br><b>Uso:</b> {uso_lote}<br><b>Bloco:</b> {id_bloco}",
                "style": {"color": "white"}
            },
            map_style=None # Usa o padrão ou dark se configurado
        ))


class MapaCalor:
    """Componente de mapa de calor por densidade de uso selecionado."""
    
    def __init__(self, df_lotes: pd.DataFrame, usos_selecionados: list = None):
        self.df_lotes = df_lotes
        self.usos_selecionados = usos_selecionados if usos_selecionados else TIPOS_USO_COMERCIAL
    
    def renderizar(self):
        """Renderiza o mapa de calor."""
        st.subheader("Mapa de Calor - Densidade de Usos Selecionados")
        
        if self.df_lotes is None or self.df_lotes.empty:
            st.warning("Sem dados de lotes para gerar o mapa de calor.")
            return
            
        if not self.usos_selecionados:
            st.warning("Selecione pelo menos um tipo de uso para gerar o mapa.")
            return

        # Filtrar lotes de interesse
        lotes_interesse = self.df_lotes[self.df_lotes['uso_lote'].isin(self.usos_selecionados)].copy()
        
        if lotes_interesse.empty:
            st.info("Nenhum lote com os usos selecionados encontrado para gerar o mapa.")
            return
            
        # Preparar dados para o HeatMap: [lat, lon, weight=1]
        # Usamos 1.0 como peso para cada lote (proporção 1:1)
        heat_data = lotes_interesse[['latitude', 'longitude']].dropna().values.tolist()
        heat_data = [[lat, lon, 1.0] for lat, lon in heat_data]
        
        if not heat_data:
            st.warning("Não foi possível obter coordenadas para os lotes selecionados.")
            return

        # Criar mapa base
        map_center = [lotes_interesse['latitude'].mean(), lotes_interesse['longitude'].mean()]
        m = folium.Map(location=map_center, zoom_start=MAP_DEFAULT_ZOOM, tiles=MAP_TILES)
        
        # Adicionar HeatMap
        HeatMap(
            heat_data,
            name="Densidade",
            min_opacity=0.4,
            radius=15,    # Ajustado para visualização mais granular
            blur=10,      # Blur menor para distinguir pontos próximos
            max_zoom=1,
        ).add_to(m)
        
        # Adicionar legenda simples
        st.markdown(f"**Total de Lotes Exibidos:** {len(heat_data)}")

        # Renderizar com estabilidade (returned_objects=[])
        st_folium(
            m, 
            width="100%", 
            height=600, 
            key="mapa_calor", 
            returned_objects=[] # Garante que o mapa não recarregue em loop
        )
