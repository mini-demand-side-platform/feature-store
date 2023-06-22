from typing import Any, List, Dict, Optional

from pydantic import BaseModel


class ListFeatureStoreOutput(BaseModel):
    feature_store_ids: List[str]
    feature_store_names: List[str]


class GetFeatureStoreOutput(BaseModel):
    feature_store_ids: List[str]
    feature_store_names: List[str]
    descriptions: List[str]
    offline_table_ids: List[str]


class OnlineFeaturesInputs(BaseModel):
    feature_ids: List[str]
    feature_store_function_types: List[str]
    inputs: List[Any]


class OnlineFeaturesOutputs(BaseModel):
    outputs: List[Any]


class CreateStringMappingFeatureInput(BaseModel):
    feature_name: str
    function_name: str
    mapping_rules: Dict[str, float]
    description: Optional[str]
