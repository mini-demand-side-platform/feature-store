# table_schema

## feature_store
|Column       |         Type          | Collation | Nullable |                          Default|
---|---|---|---|---|
 |feature_store_id   | character(8)          |           | not null | "substring"(uuid_generate_v4()::character(8)::text, 1, 8)
 |feature_store_name | character varying(50) |           |          |
 |description        | character varying(50) |           |          |
 |offline_table_name | character varying(50) |           |          |

 ## feature
 |Column|Type|Collation|Nullable|Default|
|---|---|---|---|---|
|feature_store_id      | character(8)          |           |          |
|feature_id            | character(8)          |           | not null | "substring"(uuid_generate_v4()::character(8)::text, 1, 8)
|feature_name          | character varying(50) |           |          |
|source_table_name     | character varying(50) |           |          |
|source_column_name    | character varying(50) |           |          |
|feature_function_type | character varying(50) |           |          |
|description           | character varying(50) |           |          |
|function_name         | character varying(50) |           |          |
