# TODO(integración): exponer setup_triton_logging cuando esté
# implementado en logging_engine.py.


"""API pública del paquete de telemetría de TritonMonitor."""

from .core import scan_all_providers
from .exceptions import (
    CorruptedPayloadError,
    NetworkPeeringError,
    ProviderTimeoutError,
    TritonError,
)
from .sanitizer import parse_cluster_id, parse_timeout


__all__ = [
    "CorruptedPayloadError",
    "NetworkPeeringError",
    "ProviderTimeoutError",
    "TritonError",
    "parse_cluster_id",
    "parse_timeout",
    "scan_all_providers",
]



"""prueba parcial solo por 24hs

PYTHONPATH=src python -c \
"import triton_telemetry; print(triton_telemetry.__all__)"
"""