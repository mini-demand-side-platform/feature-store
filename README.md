# feature-store

## structure
CREATE TABLE feature_store (
    feature_store_id SERIAL PRIMARY KEY,
    feature_store_name text,
    description text,
    offline_table_name text
);
CREATE TABLE feature (
    feature_store_id INTEGER REFERENCES feature_store 
    feature_id SERIAL PRIMARY KEY,
    feature_name text,
    feature_function_type text,
    description text,
    function_name text
);


## usage

### 0. list feature store

### 1. get feature store info by name

### 2. set/update feature store

### 3. delete feature store

### 4. get online features 

### 5. get offline features