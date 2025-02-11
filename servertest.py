from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os

app = FastAPI()

# Serve the React build folder
app.mount("/static", StaticFiles(directory="dist/assets"), name="static")

# Serve the index.html for all routes
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    index_path = os.path.join("dist", "index.html")
    return FileResponse(index_path)

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
