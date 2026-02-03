import pandas as pd
from config.constants import COL_LATITUDE, COL_LONGITUDE

def extrair_latitude_longitude(coord_str) -> tuple:
    """Extrai latitude e longitude de uma string formatada como 'lat, lon'."""
    try:
        if pd.isna(coord_str) or coord_str == "":
            return None, None
        
        parts = str(coord_str).split(",")
        if len(parts) >= 2:
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            
            # Validar se as coordenadas fazem sentido
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
    except:
        pass
    return None, None

def processar_coordenadas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garante que as colunas de coordenadas sejam numéricas.
    Assume que as colunas padronizadas já existem (validadas pelo DataLoader).
    """
    if df is None or df.empty:
        return df
    
    # Trabalhar em uma cópia para evitar SettingWithCopyWarning
    df = df.copy()

    # Converter para numérico, forçando colunas padronizadas
    # Erros coercing (transformando em NaN) permitem identificar dados inválidos depois
    if COL_LATITUDE in df.columns:
        df[COL_LATITUDE] = pd.to_numeric(df[COL_LATITUDE], errors='coerce')
    
    if COL_LONGITUDE in df.columns:
        df[COL_LONGITUDE] = pd.to_numeric(df[COL_LONGITUDE], errors='coerce')
    
    # Remover linhas invalidas
    df = df.dropna(subset=[COL_LATITUDE, COL_LONGITUDE])
        
    return df

