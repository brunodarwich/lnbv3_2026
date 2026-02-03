import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

from config.constants import CORES_USO_LOTE


def exibir_estatisticas_lotes(df: pd.DataFrame):
    """Exibe gráfico de pizza dos lotes por uso."""
    
    # Contagem por uso
    contagem_uso = df["uso_lote"].value_counts().reset_index()
    contagem_uso.columns = ["Uso", "Quantidade"]
    
    # Mapear cores
    cores = [CORES_USO_LOTE.get(uso, "#7f8c8d") for uso in contagem_uso["Uso"]]
    
    # Gráfico de pizza
    fig = px.pie(
        contagem_uso,
        values="Quantidade",
        names="Uso",
        color_discrete_sequence=cores,
        hole=0.5  # Donut chart
    )
    
    # Adicionar texto central
    total = contagem_uso["Quantidade"].sum()
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#a8b2d1", size=12, family="Inter, sans-serif"),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#8892b0"),
            bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(t=30, b=60, l=20, r=20),
        height=380,
        annotations=[
            dict(
                text=f"<b>{total}</b><br><span style='font-size:11px'>lotes</span>",
                x=0.5, y=0.5,
                font=dict(size=24, color="#ccd6f6"),
                showarrow=False
            )
        ]
    )
    
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(size=12, color="#ffffff"),
        hovertemplate="<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>",
        marker=dict(line=dict(color="#1a1a2e", width=2))
    )
    
    st.plotly_chart(fig, use_container_width=True)


def exibir_resumo_bloco(df_lotes_bloco: pd.DataFrame, id_bloco: str):
    """Exibe estatísticas específicas de um bloco selecionado e o gráfico poligonal."""
    
    st.subheader(f"📊 Detalhes do {id_bloco}")
    
    if df_lotes_bloco.empty:
        st.info("Nenhum lote associado a este bloco.")
        return

    # --- Gráfico de Polígono ---
    st.markdown("#### Área do Bloco (Geometria)")
    
    # Ordenação Radial para evitar zig-zag
    df_coords = df_lotes_bloco.copy()
    
    # 1. Calcular o centro (centróide)
    centro_lat = df_coords["latitude"].mean()
    centro_lon = df_coords["longitude"].mean()
    
    # 2. Calcular o ângulo de cada ponto em relação ao centro
    df_coords["angulo"] = np.arctan2(
        df_coords["latitude"] - centro_lat, 
        df_coords["longitude"] - centro_lon
    )
    
    # 3. Ordenar pelo ângulo para formar um perímetro estável
    df_coords = df_coords.sort_values("angulo")
    
    # 4. Fechar o polígono ligando o último ponto ao primeiro
    df_coords = pd.concat([df_coords, df_coords.head(1)])
    
    fig_poly = go.Figure()

    # Adicionar o polígono preenchido
    fig_poly.add_trace(go.Scatter(
        x=df_coords["longitude"],
        y=df_coords["latitude"],
        fill="toself",
        fillcolor="rgba(39, 174, 96, 0.5)", # Verde com 50% opacidade
        line=dict(color="#27ae60", width=2),
        marker=dict(size=8, color="#2ecc71"),
        name="Perímetro do Bloco",
        mode="lines+markers",
        text=df_coords["id_lote"]
    ))

    fig_poly.update_layout(
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        template="plotly_dark",
        height=1000,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', scaleanchor="x", scaleratio=1),
    )
    
    st.plotly_chart(fig_poly, use_container_width=True)

    # --- Métricas ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Lotes", len(df_lotes_bloco))
    
    with col2:
        residenciais = len(df_lotes_bloco[df_lotes_bloco["uso_lote"] == "Residencial"])
        st.metric("Residencial", residenciais)
        
    with col3:
        comerciais = len(df_lotes_bloco[df_lotes_bloco["uso_lote"].str.contains("Empresarial", na=False)])
        st.metric("Empresarial", comerciais)

    # Gráfico de pizza reduzido para o bloco
    exibir_estatisticas_lotes(df_lotes_bloco)
