from typing import Any, Dict, Optional

from fastapi import FastAPI
from output_templates import (
    GetFeatureStoreOutput,
    ListFeatureStoreOutput,
)

from .config import feature_store_server_info
from .dbs import Postgresql
from .functions import Mapping
from .logger import get_logger

log = get_logger(logger_name="main")

app = FastAPI()
feature_store_db = Postgresql(feature_store_server_info)


@app.get("/health")
def health_check() -> bool:
    return True


@app.get("/feature_store", response_model=ListFeatureStoreOutput)
def list_feature_store():
    return feature_store_db.read(
        table="feature_store",
        columns=[
            "feature_store_id",
            "feature_store_name",
        ],
    )


@app.get("/feature_store/{feature_store_id}", response_model=GetFeatureStoreOutput)
def get_feature_store(feature_store_id: str):
    return feature_store_db.read(
        table="feature_store",
        columns=[
            "feature_store_id",
            "feature_store_name",
            "description",
            "offline_table_name",
        ],
        condiction="WHERE feature_store_id = {}".format(feature_store_id),
    )


@app.post("/feature_store")
async def create_feature_store(
    feature_store_name: str, offline_table_name: str, description: Optional[str] = None
) -> bool:
    feature_store_db.write(
        table_name="feature_store",
        data={
            "feature_store_name": [feature_store_name],
            "description": [description],
            "offline_table_name": [offline_table_name],
        },
    )
    feature_store_db.create_offline_table(table_name=offline_table_name)

    return True


@app.delete("/feature_store")
async def delete_feature_store(feature_store_id: str) -> bool:
    offline_table_name = feature_store_db.read(
        "feature_store",
        columns=["offline_table_name"],
        condiction="WHERE feature_store_id = {}".format(feature_store_id),
    )["offline_table_name"][0]

    feature_store_db.delete_table(table_name=offline_table_name)
    feature_store_db.delete_row(
        table_name="feature_store",
        column_name="feature_store_id",
        target_value=feature_store_id,
    )
    return True


@app.get("/feature_store/{feature_store_id}/feature")
def list_feature(feature_store_id: str):
    return feature_store_db.read(
        table="feature",
        columns=["feature_id", "feature_name", "description", "function_name"],
        condiction="WHERE feature_store_id = {}".format(feature_store_id),
    )


@app.get("/feature_store/{feature_store_id}/feature/{feature_id}")
def get_online_feature(feature_store_id: str, feature_name: str):
    pass


@app.post("/feature_store/{feature_store_id}/feature/mapping")
async def create_mapping_feature(
    feature_store_id: str,
    feature_name: str,
    function_name: str,
    rules: Dict[str, Any],
    description: Optional[str] = None,
):
    feature_store_db.write(
        table_name="feature",
        data={
            "feature_store_id": [feature_store_id],
            "feature_name": [feature_name],
            "description": [description],
            "function_name": [function_name],
        },
    )
    m = Mapping()
    m.set_offline_feature_function(offline_database=feature_store_db, rules=rules)


@app.post("/feature_store/{feature_store_id}/feature/scale")
async def create_scale_feature():
    pass


@app.delete("/feature_store/{feature_store_id}/feature/{feature_id}")
def delete_feature(feature_name: str):
    pass


@app.post("/feature_store/{feature_store_id}/offline_table")
async def generate_offline_table(feature_store_id: str):
    pass
