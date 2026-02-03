import pandas as pd
from urllib3.exceptions import NameResolutionError

from config.settings import SPREADSHEET_ID
from services.google_sheets import GoogleSheetsService
from services.exceptions import DataConnectionError, DataValidationError
from config.constants import (
    REQUIRED_COLUMNS_BLOCOS, 
    REQUIRED_COLUMNS_LOTES,
    COL_LATITUDE,
    COL_LONGITUDE,
    RAW_COL_COORD_BLOCOS,
    RAW_COL_COORD_LOTES
)
from utils.coordinates import extrair_latitude_longitude


class DataLoader:
    """Classe para carregar dados das planilhas."""
    
    def __init__(self, sheets_service: GoogleSheetsService):
        self.sheets_service = sheets_service
    
    def _validar_colunas(self, df: pd.DataFrame, colunas_obrigatorias: list[str]) -> None:
        """Valida se as colunas obrigatórias estão presentes no DataFrame."""
        if df is None or df.empty:
            raise DataValidationError("O DataFrame retornado está vazio.")
            
        faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        if faltantes:
            raise DataValidationError(f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")

    def _normalizar_coordenadas(self, df: pd.DataFrame, coluna_bruta: str) -> pd.DataFrame:
        """Extrai latitude e longitude de uma coluna combinada se as colunas padrão não existirem."""
        if COL_LATITUDE not in df.columns or COL_LONGITUDE not in df.columns:
            if coluna_bruta in df.columns:
                coords = df[coluna_bruta].apply(extrair_latitude_longitude)
                df[COL_LATITUDE] = coords.apply(lambda x: x[0])
                df[COL_LONGITUDE] = coords.apply(lambda x: x[1])
        return df

    def carregar_dados_blocos(self) -> pd.DataFrame:
        """Carrega dados da aba 'Bloco' da planilha."""
        data = self.sheets_service.get_worksheet_data(SPREADSHEET_ID, worksheet_name="Bloco")
        df = pd.DataFrame(data)
        
        # Normalização (Adapter para o contrato interno)
        df = self._normalizar_coordenadas(df, RAW_COL_COORD_BLOCOS)
        
        # Validar colunas (Fail Fast)
        self._validar_colunas(df, REQUIRED_COLUMNS_BLOCOS)
        
        return df
    
    def carregar_dados_lotes(self) -> pd.DataFrame:
        """Carrega dados da primeira aba (Lotes)."""
        data = self.sheets_service.get_worksheet_data(SPREADSHEET_ID, worksheet_index=0)
        df = pd.DataFrame(data)
        
        # Normalização (Adapter para o contrato interno)
        df = self._normalizar_coordenadas(df, RAW_COL_COORD_LOTES)
        
        # Validar colunas (Fail Fast)
        self._validar_colunas(df, REQUIRED_COLUMNS_LOTES)
        
        return df
