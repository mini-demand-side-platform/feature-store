from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

import psycopg2
import redis

from .config import DBServerInfo


class DatabaseValueType(Enum):
    BOOL = 1
    INTEGER = 2
    FLOAT = 3
    STR = 4


class OnlineDatabase(ABC):
    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def check_exist(self):
        pass

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def scan(self):
        pass


class OfflineDatabase(ABC):
    @abstractmethod
    def create_table(self):
        pass

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def delete_table(self):
        pass

    @abstractmethod
    def delete_row(self):
        pass

    @abstractmethod
    def create_string_mapping_function(self):
        pass

    @abstractmethod
    def delete_function(self):
        pass

    @abstractmethod
    def write_from_table(self):
        pass


class Postgresql(OfflineDatabase):
    def __init__(self, db_server_info: DBServerInfo) -> None:
        self._db_server_info = db_server_info
        self.database_value_type_mapping = {
            DatabaseValueType.BOOL: "boolean",
            DatabaseValueType.INTEGER: "integer",
            DatabaseValueType.FLOAT: "real",
            DatabaseValueType.STR: "varchar(50)",
        }

    def _get_connection(self) -> psycopg2.extensions.connection:
        """_summary_

        Returns:
            psycopg2.extensions.connection: _description_
        """
        return psycopg2.connect(
            host=self._db_server_info.host,
            port=self._db_server_info.port,
            database=self._db_server_info.database,
            user=self._db_server_info.username,
            password=self._db_server_info.password,
        )

    def create_table(
        self,
        table_name: str,
        column_names: List[str],
        column_types: List[DatabaseValueType],
    ) -> None:
        assert len(column_names) == len(column_types)
        conn = self._get_connection()
        cur = conn.cursor()
        columns = []
        for i in range(len(column_names)):
            columns.append(
                column_names[i]
                + " "
                + self.database_value_type_mapping[column_types[i]]
            )
        cur.execute(
            """
            CREATE TABLE {table_name} (
                row_id SERIAL PRIMARY KEY,
                {columns}
            );
            """.format(
                table_name=table_name, columns=",".join(columns)
            )
        )
        conn.commit()
        cur.close()
        conn.close()

    def write(
        self,
        table_name: str,
        data: Dict[str, List[Any]],
        returning_columns: Optional[List[str]] = None,
    ) -> Optional[Dict[str, List[str]]]:
        res = None
        conn = self._get_connection()
        cur = conn.cursor()
        formated_data = []
        ks = list(data.keys())
        data_len = -1
        for k in ks:
            if data_len == -1:
                data_len = len(data[k])
            else:
                if data_len != len(data[k]):
                    raise "Data length different"
        for i in range(data_len):
            row = []
            for k in ks:
                row.append(data[k][i])
            formated_data.append(tuple(row))
        insert_query = """
            INSERT INTO {table_name} ({column_names})
            VALUES ({values})""".format(
            table_name=table_name,
            column_names=",".join(ks),
            values=",".join(
                ["%s"] * len(ks),
            ),
        )
        if returning_columns is not None:
            res = {}
            returning = []
            for returning_column in returning_columns:
                res[returning_column] = []
            insert_query += " RETURNING {returning_columns};".format(
                returning_columns=",".join(returning_columns)
            )

            for row in formated_data:
                cur.execute(insert_query, row)
                returning.append(cur.fetchone())

            for row in returning:
                for i in range(len(returning_columns)):
                    res[returning_columns[i]].append(row[i])
        else:
            insert_query += ";"
            cur.executemany(insert_query, formated_data)

        # Commit the changes to the database
        conn.commit()
        cur.close()
        conn.close()
        return res

    def read(
        self, table_name: str, column_names: List[str], condiction: Optional[str] = None
    ) -> Dict[str, List[Any]]:
        """_summary_

        Args:
            table_name (str): _description_
            column_names (List[str]): _description_
            condiction (Optional[str], optional): _description_. Defaults to None.

        Returns:
            Dict[str, List[Any]]: _description_
        """
        conn = self._get_connection()
        cur = conn.cursor()
        if condiction is None:
            cur.execute(
                "SELECT {column_names} FROM {table_name};".format(
                    column_names=",".join(column_names), table_name=table_name
                )
            )
        else:
            cur.execute(
                "SELECT {column_names} FROM {table_name} {condiction};".format(
                    column_names=",".join(column_names),
                    table_name=table_name,
                    condiction=condiction,
                )
            )
        res = {}
        for column_name in column_names:
            res[column_name] = []
        rows = cur.fetchall()
        for row in rows:
            for i in range(len(row)):
                res[column_names[i]].append(row[i])
        cur.close()
        conn.close()
        return res

    def delete_table(self, table_name: str) -> None:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            DROP TABLE IF EXISTS {table_name};
            """.format(
                table_name=table_name
            )
        )

        # Commit the changes to the database
        conn.commit()
        cur.close()
        conn.close()

    def delete_row(self, table_name: str, column_name: str, target_value: str) -> None:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            DELETE FROM {table_name} WHERE {column_name}='{target_value}';
            """.format(
                table_name=table_name,
                column_name=column_name,
                target_value=target_value,
            )
        )
        conn.commit()
        cur.close()
        conn.close()

    def create_string_mapping_function(
        self,
        function_name: str,
        mapping_rules: Dict[str, float],
    ) -> None:
        conn = self._get_connection()
        cur = conn.cursor()
        mapping_function = ""
        for k, v in mapping_rules.items():
            if k != "default":
                if len(mapping_function) == 0:
                    mapping_function += (
                        "IF x='{target_value}' THEN \n\tresult := {return_value};\n"
                    ).format(target_value=k, return_value=v)
                else:
                    mapping_function += (
                        "ELSIF x='{target_value}' THEN \n\tresult := {return_value};\n"
                    ).format(target_value=k, return_value=v)
        mapping_function += (
            "ELSE\n\tresult := {default_value};\nEND IF;\nRETURN result;".format(
                default_value=mapping_rules["default"]
            )
        )
        function_query = """
            CREATE FUNCTION {function_name}(x {input_type})
            RETURNS {output_type} AS $$
            DECLARE
                result {output_type};
            BEGIN
            {function_code}
            END;
            $$ LANGUAGE plpgsql;
            """.format(
            function_name=function_name,
            input_type=self.database_value_type_mapping[DatabaseValueType.STR],
            output_type=self.database_value_type_mapping[DatabaseValueType.FLOAT],
            function_code=mapping_function,
        )

        cur.execute(function_query)
        conn.commit()
        cur.close()
        conn.close()

    def create_scale_function(
        self,
        function_name: str,
        math_operation: str,
    ) -> None:
        conn = self._get_connection()
        cur = conn.cursor()

        function_query = """
            CREATE FUNCTION {function_name}(x {input_type})
            RETURNS {output_type} AS $$
            DECLARE
                result {output_type};
            BEGIN
                result := {function_code};
                RETURN result;
            END;
            $$ LANGUAGE plpgsql;
            """.format(
            function_name=function_name,
            input_type=self.database_value_type_mapping[DatabaseValueType.FLOAT],
            output_type=self.database_value_type_mapping[DatabaseValueType.FLOAT],
            function_code=math_operation,
        )
        cur.execute(function_query)
        conn.commit()
        cur.close()
        conn.close()

    def delete_function(self, function_name: str) -> None:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            DROP FUNCTION IF EXISTS {function_name};
            """.format(
                function_name=function_name
            )
        )
        conn.commit()
        cur.close()
        conn.close()

    def write_from_table(
        self,
        target_table_name: str,
        target_column_names: List[str],
        source_table_name: str,
        source_column_names: List[str],
    ):
        conn = self._get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO {target_table_name} ({target_column_names}) 
            SELECT {source_column_names} FROM {source_table_name};
            """.format(
                target_table_name=target_table_name,
                target_column_names=",".join(target_column_names),
                source_column_names=",".join(source_column_names),
                source_table_name=source_table_name,
            )
        )
        conn.commit()
        cur.close()
        conn.close()


class Redis(OnlineDatabase):
    def __init__(self, db_server_info: DBServerInfo) -> None:
        self.conn = redis.Redis(
            host=db_server_info.host,
            port=db_server_info.port,
            password=db_server_info.password,
        )

    def read(
        self,
        key: str,
    ) -> str:
        return self.conn.get(key).decode()

    def check_exist(self, key) -> bool:
        return self.conn.exists(key)

    def write(self, key: str, value: str) -> None:
        self.conn.set(key, value)

    def delete(self, key: str) -> None:
        self.conn.delete(key)

    def scan(self, pattern: str) -> List[str]:
        keys = []
        cursor = 0
        while True:
            cursor, matched_key = self.conn.scan(cursor=cursor, match=pattern)
            keys.extend(matched_key)
            if cursor == 0:
                break
        return keys
