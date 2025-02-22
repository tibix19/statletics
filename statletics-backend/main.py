from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import init_http_client, init_cache
from routes import router  # Import absolu

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize HTTP client and cache
    init_http_client(app)
    init_cache()
    yield
    # Shutdown: close the HTTP client
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)
app.include_router(router)

# Pour lancer l'application, depuis le dossier "statletics-backend", utilisez :
# python -m uvicorn main:app --reload --workers 4

