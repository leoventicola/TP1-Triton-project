"""Punto de entrada CLI de TritonMonitor."""

import argparse

from triton_telemetry.sanitizer import parse_cluster_id, parse_timeout


PROVIDERS = ("AWS", "Azure", "GCP")
OPERATING_MODES = ("nominal", "debug", "emergency")


def build_cli_parser() -> argparse.ArgumentParser:
    """Construye y configura el parser oficial de TritonMonitor."""
    parser = argparse.ArgumentParser(
        prog="TritonMonitor",
        description=(
            "Monitor de telemetría asíncrona para clústeres "
            "distribuidos en AWS, Azure y GCP."
        ),
    )

    parser.add_argument(
        "providers",
        nargs="+",
        choices=PROVIDERS,
        metavar="PROVIDER",
        help="Proveedores que se deben monitorear: AWS, Azure o GCP.",
    )

    parser.add_argument(
        "-c",
        "--cluster-id",
        type=parse_cluster_id,
        required=True,
        help=(
            "Identificador del clúster. "
            "Ejemplo: cluster-us-east-01."
        ),
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=parse_timeout,
        default=2.5,
        metavar="SECONDS",
        help=(
            "Tiempo máximo de espera por solicitud HTTP, entre "
            "0.1 y 5.0 segundos. Valor predeterminado: 2.5."
        ),
    )

    parser.add_argument(
        "--chaos",
        action="store_true",
        help="Activa los endpoints destinados a probar fallos de red.",
    )

    parser.add_argument(
        "-m",
        "--mode",
        choices=OPERATING_MODES,
        default="nominal",
        help=(
            "Modo operativo: nominal, debug o emergency. "
            "Valor predeterminado: nominal."
        ),
    )

    output_group = parser.add_mutually_exclusive_group()

    output_group.add_argument(
        "--quiet",
        action="store_true",
        help="Muestra únicamente resultados y anomalías importantes.",
    )

    output_group.add_argument(
        "--verbose",
        action="store_true",
        help="Muestra información detallada de la operación.",
    )

    return parser


if __name__ == "__main__":
    build_cli_parser().parse_args()



"""
pruebas en consola del 21/08 (esto se autodestruye en 24hs)

python src/app_operator.py --help

python src/app_operator.py AWS Azure \
  --cluster-id cluster-us-east-01 \
  --timeout 2.5 \
  --mode nominal

python src/app_operator.py AWS \
  --cluster-id cluster-us-east-01 \
  --quiet \
  --verbose


  timeout error ----- >  python src/app_operator.py AWS \
  --cluster-id cluster-us-east-01 \
  --timeout 10
"""