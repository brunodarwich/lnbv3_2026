import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from config.constants import GOOGLE_SCOPES
from config.settings import CREDENTIALS_FILE
from services.exceptions import DataConnectionError, DataPermissionError, DataNotFoundError


class GoogleSheetsService:
    """Serviço para conexão com Google Sheets."""
    
    def __init__(self, credentials_dict: dict = None, credentials_file: str = None):
        self.client = None
        self.credentials_dict = credentials_dict
        self.credentials_file = credentials_file or CREDENTIALS_FILE
    
    def authenticate(self):
        """Autentica e retorna cliente do Google Sheets."""
        if self.client:
            return self.client
        
        try:
            if self.credentials_dict:
                creds = ServiceAccountCredentials.from_json_keyfile_dict(
                    dict(self.credentials_dict), GOOGLE_SCOPES
                )
            elif os.path.exists(self.credentials_file):
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    self.credentials_file, GOOGLE_SCOPES
                )
            else:
                raise DataPermissionError("Credenciais não encontradas. Configure o arquivo credentials.json ou st.secrets.")
            
            self.client = gspread.authorize(creds)
            return self.client
            
        except Exception as e:
            if isinstance(e, DataPermissionError):
                raise e
            raise DataConnectionError("Falha na autenticação com Google Sheets", original_error=e)
    
    def get_spreadsheet(self, spreadsheet_id: str):
        """Retorna uma planilha pelo ID."""
        try:
            client = self.authenticate()
            return client.open_by_key(spreadsheet_id)
        except gspread.SpreadsheetNotFound:
            raise DataNotFoundError(f"Planilha não encontrada: {spreadsheet_id}")
        except Exception as e:
            if isinstance(e, (DataConnectionError, DataPermissionError)):
                raise e
            if "403" in str(e) or "permission" in str(e).lower():
                raise DataPermissionError(f"Permissão negada para acessar planilha: {spreadsheet_id}", original_error=e)
            raise DataConnectionError(f"Erro ao acessar planilha: {spreadsheet_id}", original_error=e)
    
    def get_worksheet_data(self, spreadsheet_id: str, worksheet_name: str = None, worksheet_index: int = None):
        """Retorna dados de uma aba específica."""
        try:
            spreadsheet = self.get_spreadsheet(spreadsheet_id)
            
            try:
                if worksheet_name:
                    worksheet = spreadsheet.worksheet(worksheet_name)
                elif worksheet_index is not None:
                    worksheet = spreadsheet.get_worksheet(worksheet_index)
                else:
                    worksheet = spreadsheet.get_worksheet(0)
            except gspread.WorksheetNotFound:
                raise DataNotFoundError(f"Aba não encontrada: {worksheet_name if worksheet_name else f'index {worksheet_index}'}")
            
            return worksheet.get_all_records()
            
        except Exception as e:
            if isinstance(e, (DataConnectionError, DataPermissionError, DataNotFoundError)):
                raise e
            raise DataConnectionError("Erro ao ler dados da planilha", original_error=e)
