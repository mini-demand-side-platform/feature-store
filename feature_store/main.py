from data_templates import (
    CreateFeatureStoreInput,
    CreateScaleFeatureInput,
    CreateStringMappingFeatureInput,
    GetFeatureStoreOutput,
    ListFeatureStoreOutput,
    OnlineFeaturesInputs,
    OnlineFeaturesOutputs,
)
from fastapi import FastAPI

from .config import cache_server_info, olap_server_info
from .dbs import Postgresql
from .feature_store import FeatureStore, Scale, StringMapping
from .logger import get_logger

log = get_logger(logger_name="main")

app = FastAPI()
offline_database = Postgresql(olap_server_info)
online_database = Postgresql(cache_server_info)
fs = FeatureStore()


@app.get("/health")
def health_check() -> bool:
    return True


@app.get("/feature_store", response_model=ListFeatureStoreOutput)
def list_feature_store():
    return offline_database.read(
        table="feature_store",
        columns=[
            "feature_store_id",
            "feature_store_name",
        ],
    )


@app.get("/feature_store/{feature_store_id}", response_model=GetFeatureStoreOutput)
def get_feature_store(feature_store_id: str):
    return offline_database.read(
        table="feature_store",
        columns=[
            "feature_store_id",
            "feature_store_name",
            "description",
            "offline_table_name",
        ],
        condiction="WHERE feature_store_id = {feature_store_id}".format(
            feature_store_id=feature_store_id
        ),
    )


@app.post("/feature_store")
async def create_feature_store(
    create_feature_store_input: CreateFeatureStoreInput,
) -> bool:
    offline_database.write(
        table_name="feature_store",
        data={
            "feature_store_name": [create_feature_store_input.feature_store_name],
            "description": [create_feature_store_input.description],
            "offline_table_name": [create_feature_store_input.offline_table_name],
        },
    )

    return True


@app.delete("/feature_store")
async def delete_feature_store(feature_store_id: str) -> bool:
    offline_table_name = offline_database.read(
        table_name="feature_store",
        columns=["offline_table_name"],
        condiction="WHERE feature_store_id = {feature_store_id}".format(
            feature_store_id=feature_store_id
        ),
    )["offline_table_name"][0]

    offline_database.delete_table(table_name=offline_table_name)
    feature_ids = offline_database.read(
        table_name="feature",
        columns=["feature_id"],
        condiction="WHERE feature_store_id = {feature_store_id}".format(
            feature_store_id=feature_store_id
        ),
    )["feature_id"]
    offline_database.delete_row(
        table_name="feature_store",
        column_name="feature_store_id",
        target_value=feature_store_id,
    )

    for feature_id in feature_ids:
        fs.delete_offline_feature(
            offline_database=offline_database, feature_id=feature_id
        )
        fs.delete_online_feature(online_database=online_database, feature_id=feature_id)

    return True


@app.get("/feature_store/{feature_store_id}/feature")
def list_feature(feature_store_id: str):
    return offline_database.read(
        table="feature",
        columns=["feature_id", "feature_name", "description", "function_name"],
        condiction="WHERE feature_store_id = {feature_store_id}".format(
            feature_store_id=feature_store_id
        ),
    )


@app.post("/online_features")
def get_online_feature(
    online_features_inputs: OnlineFeaturesInputs,
) -> OnlineFeaturesOutputs:
    return fs.get_online_feature(
        online_database=online_database,
        feature_store_function_types=online_features_inputs.feature_store_function_types,
        feature_ids=online_features_inputs.feature_ids,
        inputs=online_features_inputs.inputs,
    )


@app.post("/feature_store/{feature_store_id}/feature/string_mapping")
async def create_string_mapping_feature(
    feature_store_id: str,
    create_string_mapping_feature_input=CreateStringMappingFeatureInput,
) -> bool:
    feature_id = offline_database.write(
        table_name="feature",
        data={
            "feature_store_id": [feature_store_id],
            "feature_name": [create_string_mapping_feature_input.feature_name],
            "source_table_name": [
                create_string_mapping_feature_input.source_table_name
            ],
            "source_column_name": [
                create_string_mapping_feature_input.source_column_name
            ],
            "feature_function_type": ["string_mapping"],
            "description": [create_string_mapping_feature_input.description],
            "function_name": [create_string_mapping_feature_input.function_name],
        },
        returning_columns=["feature_id"],
    )["feature_id"][0]

    sm = StringMapping()
    sm.set_online_feature_function(
        online_database=online_database,
        feature_id=feature_id,
        mapping_rules=create_string_mapping_feature_input.mapping_rules,
    )
    sm.set_offline_feature_function(
        offline_database=offline_database,
        function_name=create_string_mapping_feature_input.feature_name,
        mapping_rules=create_string_mapping_feature_input.mapping_rules,
    )
    return True


@app.post("/feature_store/{feature_store_id}/feature/scale")
async def create_scale_feature(
    feature_store_id: str, create_scale_feature_input=CreateScaleFeatureInput
):
    feature_id = offline_database.write(
        table_name="feature",
        data={
            "feature_store_id": [feature_store_id],
            "feature_name": [create_scale_feature_input.feature_name],
            "source_table_name": [create_scale_feature_input.source_table_name],
            "source_column_name": [create_scale_feature_input.source_column_name],
            "feature_function_type": ["scale"],
            "description": [create_scale_feature_input.description],
            "function_name": [create_scale_feature_input.function_name],
        },
        returning_columns=["feature_id"],
    )["feature_id"][0]
    sc = Scale()
    sc.set_online_feature_function(
        online_database=online_database,
        feature_id=feature_id,
        math_operation=create_scale_feature_input.math_operation,
    )
    sc.set_offline_feature_function(
        online_database=online_database,
        function_name=create_scale_feature_input.function_name,
        math_operation=create_scale_feature_input.math_operation,
    )
    return True


@app.delete("/feature_store/{feature_store_id}/feature/{feature_id}")
def delete_feature(feature_id: str) -> bool:
    fs.delete_online_feature(online_database=online_database, feature_id=feature_id)
    fs.delete_offline_feature(offline_database=offline_database, feature_id=feature_id)
    return True


@app.post("/feature_store/{feature_store_id}/offline_table")
async def generate_offline_table(feature_store_id: str) -> bool:
    fs.generate_offline_table(
        offline_database=offline_database, feature_store_id=feature_store_id
    )
    return True
