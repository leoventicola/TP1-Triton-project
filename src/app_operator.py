"""Punto de entrada CLI de TritonMonitor."""

import argparse
import asyncio
import traceback

from triton_telemetry import (
    CorruptedPayloadError, 
    NetworkPeeringError, 
    ProviderTimeoutError,
    TritonError,
    parse_cluster_id,
    parse_timeout,
    scan_all_providers,
    setup_triton_logging    
)

# Constantes del dominio (PEP 8 : MAYUS)
PROVIDERS = ("AWS", "Azure", "GCP")
OPERATING_MODES = ("nominal", "debug", "emergency")


def build_cli_parser() -> argparse.ArgumentParser:
    """Construye y configura el parser oficial de TritonMonitor."""
    parser = argparse.ArgumentParser(
        prog="TritonMonitor",
        description=(
            "Monitor de telemetría asíncrona para clústeres "
            "distribuidos en AWS, Azure y GCP. "
        ),
    )

    parser.add_argument(
        "providers",
        nargs="+",
        choices=PROVIDERS,
        metavar="PROVIDER",
        help=("Proveedores que se deben monitorear: AWS, Azure o GCP. "
        ),
    )

    # ID del clúster con sanitizador
    parser.add_argument(
        "-c",
        "--cluster-id",
        type=parse_cluster_id,
        required=True,
        metavar="ID",
        help=(
            "Identificador del clúster. "
            "Ejemplo: cluster-us-east-01. "
        ),
        
    )

    # IMEOUT con sanitizador
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

    # Inyeccion del caos
    parser.add_argument(
        "--chaos",
        action="store_true",
        help=("Activa los endpoints destinados a probar fallos de red.",
        ),
    )

    # Modos operativos
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

    # GRUPO MUTUAMENTE EXCLUYENTE
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--quiet",
        action="store_true",
        help=("Muestra únicamente resultados y anomalías importantes.",
        ),
    )
    output_group.add_argument(
        "--verbose",
        action="store_true",
        help=("Muestra información detallada de la operación.",
        ),
    )

    return parser


# Registro forense estructurado de excepciones
def log_forensic_exception(logger, exc):
    logger.error(
        "Registro forense estructurado de la excepción",
        extra={
            "exception_tree": {
                "class": type(exc).__name__,
                "message": str(exc),
                "notes": getattr(exc, "__notes__", []),
            },
            "stack_trace": "".join(
                traceback.format_exception(
                    type(exc),
                    exc,
                    exc.__traceback__,
                )
            ),
        },
    )


async def async_main() -> None:
    parser = build_cli_parser()
    args = parser.parse_args()

    # Inicialización de logging dinámico
    logger = setup_triton_logging()

    logger.info("=" * 60)
    logger.info("Iniciando TritonMonitor...")
    logger.info("=" * 60)

    try:
        results = await scan_all_providers(
            providers=args.providers,
            timeout=args.timeout,
            use_chaos=args.chaos,
        )

        logger.info("\n ESCANEO COMPLETADO CON ÉXITO SIN ANOMALÍAS:")
        for r in results:
            logger.info(
                "  • %s -> Latencia: %.3fs | ID: %s | Estatus: %s",
                r["provider"],
                r["latency_sec"],
                r["payload_id"],
                r["status"],
            )     

    except* ProviderTimeoutError as group:
        logger.error(
            "\n ANOMALÍA: DETECTADOS TIMEOUTS EN PROVEEDORES (%d incidentes):",
            len(group.exceptions),
        )
        for exc in group.exceptions:
            logger.error("   Fallo: %s", exc)
            for note in getattr(exc, "__notes__", []):
                logger.error("     └─ [FORENSE TRITÓN] %s", note)

            log_forensic_exception(logger, exc)


    except* NetworkPeeringError as group:
        logger.error(
            "\n ANOMALÍA: DETECTADOS FALLOS FÍSICOS DE CONEXIÓN (%d incidentes):",
            len(group.exceptions),
        )
        for exc in group.exceptions:
            logger.error("   Fallo: %s", exc)
            for note in getattr(exc, "__notes__", []):
                logger.error("     └─ [FORENSE TRITÓN] %s", note)

            log_forensic_exception(logger, exc)

    except* CorruptedPayloadError as group:
        logger.error(
            "\n ADVERTENCIA: PAYLOADS CORRUPTOS (%d incidentes):",
            len(group.exceptions),
        )
        for exc in group.exceptions:
            logger.error("   Fallo: %s", exc)

            for note in getattr(exc, "__notes__", []):
                logger.error("     └─ [FORENSE TRITÓN] %s", note)

            log_forensic_exception(logger, exc)

    except* TritonError as group:
        logger.error("\n DETECTADO ERROR OPERACIONAL IMPREVISTO:")
        for exc in group.exceptions:
            logger.error("   Fallo: %s", exc)
        log_forensic_exception(logger, exc)

    finally:
        # PEP 765: Limpieza sin return, break o continue
        logger.info("\n" + "=" * 64)
        logger.info("  [FIN DE CICLO] Recursos liberados de la Operación Tritón.")
        logger.info("=" * 64)

        if hasattr(logger, "listener") and logger.listener:
            logger.listener.stop()


if __name__ == "__main__":
    asyncio.run(async_main())