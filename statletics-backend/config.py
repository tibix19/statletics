import httpx
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from datetime import timedelta


def init_http_client(app):
    """
    Initialise le client HTTP asynchrone avec des timeouts configurés et le stocke dans l'état de l'application.
    """
    # Configure des timeouts plus longs pour éviter les erreurs ReadTimeout
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
    app.state.http_client = httpx.AsyncClient(timeout=timeout)


def init_cache():
    """
    Initialise le cache en mémoire avec un prefix pour éviter les collisions.
    Configure une durée de cache de 48 heures pour optimiser les performances.
    """
    FastAPICache.init(InMemoryBackend(), 
                     prefix="fastapi-cache",
                     expire=timedelta(hours=48))