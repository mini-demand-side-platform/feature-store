from fastapi import FastAPI

from .config import HealthCheckOutput
from .logger import get_logger

log = get_logger(logger_name="main")

app = FastAPI()


@app.get("/health", response_model=HealthCheckOutput)
def health_check():
    return {"health": "True"}


@app.get("/feature_store")
def list_feature_store():
    pass


@app.get("/feature_store/{feature_store_name}")
def get_feature_store(feature_store_name: str):
    pass


@app.post("/feature_store")
def create_feature_store():
    pass


@app.delete("/feature_store")
def delete_feature_store():
    pass


@app.get("/feature_store/{feature_store_name}/feature")
def list_feature(feature_store_name: str):
    pass


@app.get("/feature_store/{feature_store_name}/feature/{feature_name}")
def get_online_feature(feature_store_name: str, feature_name: str):
    pass


@app.post("/feature_store/{feature_store_name}/feature")
def create_feature():
    pass


@app.delete("/feature_store/{feature_store_name}/feature/{feature_name}")
def delete_feature(feature_name: str):
    pass
