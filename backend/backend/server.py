import logging
import uvicorn

from backend.config.main import PORT

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger() 
logger.setLevel(logging.WARNING)

def start_server():
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
    )


if __name__ == "__main__":
    start_server()
