import uvicorn
from fastapi import FastAPI

from routes.routes import main_router

# MAIN

app = FastAPI(title="cartridge_games_exchange")

app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
