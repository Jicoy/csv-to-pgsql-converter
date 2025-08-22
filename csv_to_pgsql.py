import pandas as pd
import sys

FIELD_MAX_LENGTHS = {
    "status": 50,
    "description": 255,
    "remarks": 255
}

def trim_value(column: str, value: str) -> str:
    """
    Trim the value according to FIELD_MAX_LENGTHS, if defined.
    Also cleans up newlines and escapes single quotes.
    """
    if value is None or pd.isna(value):
        return "NULL"

    safe_val = str(value).replace("'", "''").replace("\n", " ").replace("\r", " ")

    if column in FIELD_MAX_LENGTHS:
        max_len = FIELD_MAX_LENGTHS[column]
        if len(safe_val) > max_len:
            safe_val = safe_val[:max_len]

    return f"'{safe_val}'"

def csv_to_pgsql(csv_file, table_name, output_sql):
    
    df = pd.read_csv(csv_file)

    with open(output_sql, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            values = []

            for col, val in row.items():
                if isinstance(val, (int, float)) and not pd.isna(val):
                        values.append(str(val))
                else:
                    values.append(trim_value(col, val))

            insert_stmt = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(values)});\n"
            f.write(insert_stmt)

    print(f"SQL script written to {output_sql}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python csv_to_pgsql.py <csv_file> <table_name> <output_sql>")
        sys.exit(1)

    csv_file = sys.argv[1]
    table_name = sys.argv[2]
    output_sql = sys.argv[3]

    csv_to_pgsql(csv_file, table_name, output_sql)