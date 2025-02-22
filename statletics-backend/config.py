import httpx
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend


def init_http_client(app):
    """
    Initialise le client HTTP asynchrone et le stocke dans l'état de l'application.
    """
    app.state.http_client = httpx.AsyncClient()


def init_cache():
    """
    Initialise le cache en mémoire avec un prefix pour éviter les collisions.
    """
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
