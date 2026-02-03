import streamlit as st

from config.constants import CORES_USO_LOTE


def exibir_legenda():
    """Exibe a legenda de cores por tipo de uso usando colunas do Streamlit."""
    cols = st.columns(len(CORES_USO_LOTE))
    
    for i, (uso, cor) in enumerate(CORES_USO_LOTE.items()):
        with cols[i]:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:6px;">'
                f'<div style="width:12px;height:12px;background:{cor};border-radius:50%;"></div>'
                f'<span style="font-size:12px;color:#8892b0;">{uso}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
