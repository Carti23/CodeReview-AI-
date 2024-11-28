import logging
import uvicorn
from fastapi import FastAPI
from uvicorn.config import LOGGING_CONFIG
from api.endpoints import review_router
from utils.logging_config.logging_config import logging_config

# Configure logging
logging.config.dictConfig(logging_config)
logger = logging.getLogger("CodeReviewAI")

# Initialize FastAPI app
app = FastAPI(title="CodeReviewAI", docs_url="/swagger")

# Include the review router
app.include_router(review_router, prefix="/api")


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    logger.info("Redirecting to Swagger UI")
    return {"message": "Navigate to /swagger for API documentation."}


if __name__ == "__main__":
    logger.info("Starting CodeReviewAI application")
    uvicorn.run(app, host="localhost", port=80, log_config=logging_config)
