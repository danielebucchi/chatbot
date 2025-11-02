from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.routes import router as api_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Datapizza Backend MVP",
        description="Backend modulare FastAPI con DI, file upload e cache in-memory.",
        version="0.1.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # o "*" per sviluppo
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.get("/status")
    async def status():
        return {"status": "ok"}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
