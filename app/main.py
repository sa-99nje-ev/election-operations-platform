from fastapi import FastAPI
from app.routers import results

app = FastAPI(title="Election Operations Platform")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Mount results router
app.include_router(results.router)
