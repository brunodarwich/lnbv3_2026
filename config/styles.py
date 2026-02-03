DARK_THEME_CSS = """
<style>
    /* Tema principal */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #e8e8e8;
    }
    
    /* Títulos */
    h1 {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: #a8b2d1 !important;
        font-weight: 600 !important;
    }
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255,255,255,0.03);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 8px;
        color: #8892b0;
        font-size: 14px;
        font-weight: 500;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.1);
        color: #ccd6f6;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Botões e Selectbox */
    .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        color: #ccd6f6;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #667eea;
    }
    
    /* Mensagens de sucesso */
    .stSuccess {
        background-color: rgba(39, 174, 96, 0.1) !important;
        border: 1px solid rgba(39, 174, 96, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Cards e containers */
    .stMarkdown {
        color: #a8b2d1;
    }
    
    hr {
        border-color: rgba(255,255,255,0.1) !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Iframe do mapa */
    iframe {
        border-radius: 12px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3) !important;
        aspect-ratio: 1 / 1;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    
    /* Animação suave para elementos */
    .element-container {
        transition: opacity 0.3s ease;
    }
    
    /* Plotly chart container */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
"""
