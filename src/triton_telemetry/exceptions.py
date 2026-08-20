class TritonError(Exception):
    """Error general del dominio Triton."""

class ProviderTimeoutError(TritonError):
    """El proveedor no respondio dentro del tiempo permitido."""

class CorruptedPayloadError(TritonError):
    """Respuesta HTTP fallida o inesperada."""

class NetworkPeeringError(TritonError):
    """Fallo de DNS o de resolución de hosts."""
