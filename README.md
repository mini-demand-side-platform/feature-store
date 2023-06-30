# feature-store

## structure
CREATE TABLE feature_store (
    feature_store_id char(8) PRIMARY KEY DEFAULT substring(uuid_generate_v4()::char(8), 1, 8),
    feature_store_name varchar(50),
    description varchar(50),
    offline_table_name varchar(50)
);
CREATE TABLE feature (
    feature_store_id char(8) REFERENCES feature_store (feature_store_id),
    feature_id char(8) PRIMARY KEY DEFAULT substring(uuid_generate_v4()::char(8), 1, 8),
    feature_name varchar(50),
    source_table_name varchar(50),
    source_column_name varchar(50),
    feature_function_type varchar(50),
    description varchar(50),
    function_name varchar(50)
);

INSERT INTO feature (feature_store_id,feature_name,source_table_name,source_column_name,feature_function_type,description,function_name)
            VALUES ('a5b56fdf', 'layout_style_mapping', 'olap', 'layout_style', 'string_mapping', 'map layout_style AB to 1', 'layout_style_mapping') RETURNING feature_id;
## usage

### 0. list feature store

### 1. get feature store info by name

### 2. set/update feature store

### 3. delete feature store

### 4. get online features 

### 5. get offline features