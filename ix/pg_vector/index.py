from django.db import migrations


class AddEuclideanDistanceIndex(migrations.RunSQL):
    """
    Create an index for euclidean distance on a specific column of a table.

    Example usage:
        AddEuclideanDistanceIndex('items', 'embedding', lists=150)

    Args:
        table_name (str): Name of the table.
        column_name (str): Name of the column.
        lists (int, optional): Number of lists for ivfflat. Defaults to 100.
        index_name (str, optional): Name of the index. If not provided, defaults to '{table_name}_{column_name}_l2_idx'.
    """

    def __init__(
        self,
        table_name: str,
        column_name: str,
        lists: int = 100,
        index_name: str = None,
    ):
        index_name = index_name or f"{table_name}_{column_name}_l2_idx"
        sql = f"CREATE INDEX {index_name} ON {table_name} USING ivfflat ({column_name} vector_l2_ops) WITH (lists = {lists});"
        super().__init__(sql)


class AddInnerProductIndex(migrations.RunSQL):
    """
    Create an index for inner product on a specific column of a table.

    Example usage:
        AddInnerProductIndex('items', 'embedding', lists=200)

    Args:
        table_name (str): Name of the table.
        column_name (str): Name of the column.
        lists (int, optional): Number of lists for ivfflat. Defaults to 100.
        index_name (str, optional): Name of the index. If not provided, defaults to '{table_name}_{column_name}_ip_idx'.
    """

    def __init__(
        self,
        table_name: str,
        column_name: str,
        lists: int = 100,
        index_name: str = None,
    ):
        index_name = index_name or f"{table_name}_{column_name}_ip_idx"
        sql = f"CREATE INDEX {index_name} ON {table_name} USING ivfflat ({column_name} vector_ip_ops) WITH (lists = {lists});"
        super().__init__(sql)


class AddCosineDistanceIndex(migrations.RunSQL):
    """
    Create an index for cosine distance on a specific column of a table.

    Example usage:
        AddCosineDistanceIndex('items', 'embedding', lists=250)

    Args:
        table_name (str): Name of the table.
        column_name (str): Name of the column.
        lists (int, optional): Number of lists for ivfflat. Defaults to 100.
        index_name (str, optional): Name of the index. If not provided, defaults to '{table_name}_{column_name}_cosine_idx'.
    """

    def __init__(
        self,
        table_name: str,
        column_name: str,
        lists: int = 100,
        index_name: str = None,
    ):
        index_name = index_name or f"{table_name}_{column_name}_cosine_idx"
        sql = f"CREATE INDEX {index_name} ON {table_name} USING ivfflat ({column_name} vector_cosine_ops) WITH (lists = {lists});"
        super().__init__(sql)
