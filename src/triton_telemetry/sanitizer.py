import argparse
import re

def parse_timeout(value: str) -> float:
    """
    Valida entradas de timeout
    para salidas HTTP.
    Soporta flotantes de 0.1 a 5.0.
    """
    try:
        val = float(value)
        if not (0.1 <= val <= 5.0):
            raise argparse.ArgumentTypeError(f"Timeout invalido, solo se permiten flotantes entre 0.1 y 5.0")
        return val
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Timeout invalido -{value}-\n"
            "Solo se permiten numeros decimales entre 0.1 y 5.0"
        )

def parse_cluster_id(value:str) -> str:
    """
    Valida que el cluster siga la norma:
    cluster-[a-z]{2,10}-[a-z]+-\d{2} (e.g., cluster-us-east-01).
    """
    pattern = r"^cluster-[a-z]{2,10}-[a-z]+-\d{2}$"
    if re.match(pattern, value):
        return value
    raise argparse.ArgumentTypeError(
        f"Cluster ID invalido: {value}\n"
        "Debe seguir el formato estricto: cluster-us-east-01"
    )
