from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, insert, inspect, text, Engine
from smolagents import CodeAgent, LiteLLMModel, tool

DATABASE_URL = "sqlite:///:memory:"
TABLE_NAME = "receipts"
ROWS = [
    {"receipt_id": 1, "customer_name": "Alan Payne", "price": 12.06, "tip": 1.20},
    {"receipt_id": 2, "customer_name": "Alex Mason", "price": 23.86, "tip": 0.24},
    {"receipt_id": 3, "customer_name": "Woodrow Wilson", "price": 53.43, "tip": 5.43},
    {"receipt_id": 4, "customer_name": "Margaret James", "price": 21.11, "tip": 1.00},
]

def setup_database() -> Engine:
    engine = create_engine(DATABASE_URL)
    metadata_obj = MetaData()
    table = Table(
        TABLE_NAME,
        metadata_obj,
        Column("receipt_id", Integer, primary_key=True),
        Column("customer_name", String(16), primary_key=True),
        Column("price", Float),
        Column("tip", Float),
    )
    metadata_obj.create_all(engine)
    for row in ROWS:
        stmt = insert(table).values(**row)
        with engine.begin() as connection:
            connection.execute(stmt)
    return engine


def print_table_description(engine: Engine) -> None:
    inspector = inspect(engine)
    columns_info = [(col["name"], col["type"]) for col in inspector.get_columns(TABLE_NAME)]
    table_description = "Columns:\n" + "\n".join([f"  - {name}: {col_type}" for name, col_type in columns_info])
    print(table_description)


def main():

    engine = setup_database()
    print_table_description(engine)

    @tool
    def sql_engine(query: str) -> str:
        """
        Allows you to perform SQL queries on the table. Returns a string representation of the result.
        The table is named 'receipts'. Its description is as follows:
            Columns:
            - receipt_id: INTEGER
            - customer_name: VARCHAR(16)
            - price: FLOAT
            - tip: FLOAT

        Args:
            query: The query to perform. This should be correct SQL.
        """
        output = ""
        try:
            with engine.connect() as con:
                rows = con.execute(text(query))
                for row in rows:
                    output += "\n" + str(row)
        except Exception as e:
            output = f"Error executing query: {e}"
        return output

    model = LiteLLMModel(model_id="ollama_chat/qwen2:7b", api_base="http://127.0.0.1:11434", num_ctx=8192)
    agent = CodeAgent(tools=[sql_engine], model=model)

    instruction = "Can you give me the name of the client who got the most expensive receipt?"
    result = agent.run(instruction)
    print("Agent result:", result)


if __name__ == "__main__":
    main()
