# Escopos do Google API
GOOGLE_SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Cores para cada tipo de uso do lote (cores profissionais)
CORES_USO_LOTE = {
    "Residencial": "#3498db",
    "Empresarial": "#27ae60",
    "Empresarial vazio": "#2ecc71",
    "Misto": "#f39c12",
    "Baldio": "#95a5a6",
    "Abandonado": "#e74c3c",
    "Religioso": "#9b59b6",
    "Institucional": "#2c3e50",
}

# Cores Folium para marcadores (nomes compatíveis com folium.Icon)
CORES_FOLIUM = {
    "Residencial": "blue",
    "Empresarial": "green",
    "Empresarial vazio": "lightgreen",
    "Misto": "orange",
    "Baldio": "gray",
    "Abandonado": "red",
    "Religioso": "purple",
    "Institucional": "darkblue",
}

# Ícones para cada tipo de uso
ICONES_USO_LOTE = {
    "Residencial": "home",
    "Empresarial": "briefcase",
    "Empresarial vazio": "building",
    "Misto": "random",
    "Baldio": "square",
    "Abandonado": "ban",
    "Religioso": "church",
    "Institucional": "university",
}

# Colunas Obrigatórias (Data Contract)
REQUIRED_COLUMNS_BLOCOS = ["id_bloco", "latitude", "longitude"]
REQUIRED_COLUMNS_LOTES = ["id_lote", "id_bloco", "uso_lote"]

# Colunas Padronizadas para uso interno
COL_LATITUDE = "latitude"
COL_LONGITUDE = "longitude"
COL_ID_BLOCO = "id_bloco"
COL_ID_LOTE = "id_lote"
COL_USO_LOTE = "uso_lote"
COL_TIPOLOGIA = "tipologia"

# Colunas brutas da planilha (para mapeamento/normalização)
RAW_COL_COORD_BLOCOS = "latitude_longitude_bloco"
RAW_COL_COORD_LOTES = "latitude_longitude"

# Cores disponíveis no Folium
FOLIUM_OK_COLORS = [
    'red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 
    'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 
    'lightblue', 'lightgreen', 'gray', 'black', 'lightgray'
]

# Ícones sugeridos (Font Awesome)
SUGGESTED_ICONS = [
    "home", "building", "briefcase", "info-sign", "map-marker", "star", 
    "user", "flag", "bookmark", "heart", "camera", "car", "bicycle", 
    "bus", "cutlery", "gift", "glass", "globe", "headphones", "music", 
    "picture", "plane", "plus", "print", "road", "shopping-cart", "tags",
    "thumbs-up", "tint", "trash", "tree", "wrench", "random", "square", 
    "ban", "church", "university"
]

# Tipos de uso para mapa de calor (Empresarial e Misto)
TIPOS_USO_COMERCIAL = [
    "Empresarial",
    "Empresarial vazio",
    "Misto",
    "Institucional"
]
