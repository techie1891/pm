from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# API routes
@app.get("/api/hello")
def api_hello():
    return {"message": "hello"}

# Serve static files from frontend build
public_dir = os.path.join(os.path.dirname(__file__), "public")
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="frontend")

