from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ListFeatureStoreOutput(BaseModel):
    feature_store_ids: List[str]
    feature_store_names: List[str]


class GetFeatureStoreOutput(BaseModel):
    feature_store_ids: List[str]
    feature_store_names: List[str]
    descriptions: List[str]
    offline_table_ids: List[str]


class CreateFeatureStoreInput(BaseModel):
    feature_store_name: str
    offline_table_name: str
    description: Optional[str]


class OnlineFeaturesInputs(BaseModel):
    feature_ids: List[str]
    feature_store_function_types: List[str]
    inputs: List[Any]


class OnlineFeaturesOutputs(BaseModel):
    outputs: List[Any]


class CreateFeatureInput(BaseModel):
    feature_name: str
    source_table_name: str
    source_column_name: str
    function_name: str
    description: str
    function_name: str


class CreateStringMappingFeatureInput(CreateFeatureInput):
    mapping_rules: Dict[str, float]


class CreateScaleFeatureInput(CreateFeatureInput):
    math_operation: str
