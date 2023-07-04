from fastapi import FastAPI
from ix.api.chains.endpoints import router as chains_router

app = FastAPI()
app.include_router(chains_router)
