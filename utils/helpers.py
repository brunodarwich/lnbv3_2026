from config.constants import CORES_USO_LOTE


def get_color(uso_lote: str) -> str:
    """Retorna a cor correspondente ao tipo de uso do lote."""
    return CORES_USO_LOTE.get(uso_lote, "black")


def hex_to_rgb(hex_color: str) -> list:
    """Converte uma cor hexadecimal para RGB (0-255)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
