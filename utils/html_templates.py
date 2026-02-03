from config.constants import CORES_USO_LOTE

def generate_bloco_popup_html(row: dict) -> str:
    """Gera o HTML do popup para um bloco."""
    
    id_bloco = row.get('id_bloco', row.get('ID', 'N/A'))
    lat = row.get("latitude", 0)
    lon = row.get("longitude", 0)
    
    total_lotes = row.get('total_lotes', 0)
    
    # Se total_lotes for 0, retornar popup básico
    if total_lotes == 0:
        return f"""
        <div style="font-family: Arial; min-width: 150px; color: #333;">
            <h4 style="margin: 0 0 5px 0; color: #1a1a2e; border-bottom: 2px solid #667eea; padding-bottom: 3px;">{id_bloco}</h4>
            <p style="margin: 0; color: #999; font-size: 9px;">Lat: {lat:.6f} | Lon: {lon:.6f}</p>
            <p style="margin-top: 5px; font-size: 11px; color: #666;">Sem dados de lotes.</p>
        </div>
        """

    uso_predominante = row.get('uso_predominante', 'N/A')
    tipologia_pred = row.get('tipologia_pred', 'N/A')
    usos_counts = row.get('usos_counts', {})
    
    # Gerar badges
    badges_html = ""
    if isinstance(usos_counts, dict):
        badges_html = "".join([
            f'<span style="background: {CORES_USO_LOTE.get(uso, "#ccc")}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 9px; margin-right: 4px; margin-bottom: 4px; display: inline-block;">{uso}: {count}</span>'
            for uso, count in usos_counts.items()
        ])

    stats_html = f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px;">
        <div style="background: #f0f2f6; padding: 8px; border-radius: 6px; text-align: center; grid-column: span 2;">
            <span style="display: block; font-size: 9px; color: #666; text-transform: uppercase;">Total de Lotes</span>
            <span style="font-size: 18px; font-weight: bold; color: #667eea;">{total_lotes}</span>
        </div>
        <div style="font-size: 11px;">
            <b style="color: #444;">Uso Predom.:</b><br>
            <span style="color: #666;">{uso_predominante}</span>
        </div>
        <div style="font-size: 11px;">
            <b style="color: #444;">Tipologia:</b><br>
            <span style="color: #666;">{tipologia_pred}</span>
        </div>
    </div>
    <div style="margin-top: 10px; border-top: 1px solid #eee; padding-top: 8px;">
        <b style="font-size: 11px; color: #444;">Distribuição de Usos:</b>
        <div style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px;">
            {badges_html}
        </div>
    </div>
    """
    
    popup_html = f"""
    <div style="font-family: Arial; min-width: 220px; color: #333;">
        <h4 style="margin: 0 0 5px 0; color: #1a1a2e; border-bottom: 2px solid #667eea; padding-bottom: 3px;">{id_bloco}</h4>
        <p style="margin: 0; color: #999; font-size: 9px;">Lat: {lat:.6f} | Lon: {lon:.6f}</p>
        {stats_html}
    </div>
    """
    return popup_html
