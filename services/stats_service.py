import pandas as pd
from config.constants import COL_ID_BLOCO, COL_USO_LOTE, COL_TIPOLOGIA

class StatsService:
    """Serviço responsável por enriquecer os dados com cálculos estatísticos."""
    
    @staticmethod
    def enrich_blocos_data(df_blocos: pd.DataFrame, df_lotes: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula estatísticas de lotes (contagem, moda, distribuição) e anexa aos blocos.
        """
        if df_blocos is None or df_blocos.empty:
            return df_blocos

        if df_lotes is None or df_lotes.empty:
            df_blocos['total_lotes'] = 0
            df_blocos['uso_predominante'] = "N/A"
            df_blocos['tipologia_pred'] = "N/A"
            df_blocos['usos_counts'] = None
            return df_blocos

        # Trabalhar com cópias
        df_blocos = df_blocos.copy()
        df_lotes = df_lotes.copy()
        
        # Agrupar lotes por bloco
        grouped = df_lotes.groupby(COL_ID_BLOCO)
        
        # 1. Estatísticas Básicas
        agg_dict = {
            'total_lotes': (COL_ID_BLOCO, 'size'),
            'uso_predominante': (COL_USO_LOTE, lambda x: x.mode().iloc[0] if not x.mode().empty else "N/A")
        }
        
        if COL_TIPOLOGIA in df_lotes.columns:
             agg_dict['tipologia_pred'] = (COL_TIPOLOGIA, lambda x: x.mode().iloc[0] if not x.mode().empty else "N/A")
        
        stats = grouped.agg(**agg_dict).reset_index()
        
        # 2. Contagem de Usos (para badges)
        # Retorna dataframe onde colunas são os usos
        usos_pivot = grouped[COL_USO_LOTE].value_counts().unstack(fill_value=0)
        
        # Converter cada linha em um dicionário {uso: count}
        # Limpar chaves com valor 0 para economizar espaço
        def to_dict_clean(row):
            return {k: v for k, v in row.items() if v > 0}
            
        usos_dict = uses_series = pd.DataFrame({
            COL_ID_BLOCO: usos_pivot.index,
            'usos_counts': [to_dict_clean(row) for _, row in usos_pivot.iterrows()]
        })

        # 3. Merge com df_blocos
        # Merge stats
        df_enriched = pd.merge(df_blocos, stats, on=COL_ID_BLOCO, how='left')
        # Merge counts
        df_enriched = pd.merge(df_enriched, usos_dict, on=COL_ID_BLOCO, how='left')
        
        # Preencher NaNs resultantes do Left Join (blocos sem lotes)
        df_enriched['total_lotes'] = df_enriched['total_lotes'].fillna(0).astype(int)
        df_enriched['uso_predominante'] = df_enriched['uso_predominante'].fillna("N/A")
        if 'tipologia_pred' in df_enriched.columns:
            df_enriched['tipologia_pred'] = df_enriched['tipologia_pred'].fillna("N/A")
        else:
            df_enriched['tipologia_pred'] = "N/A"
        
        # Para usos_counts, NaN deve ser dict vazio
        df_enriched['usos_counts'] = df_enriched['usos_counts'].apply(lambda x: x if isinstance(x, dict) else {})
        
        return df_enriched
