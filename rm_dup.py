import pandas as pd

CSV_FILE = "item_custody.csv"          # Your CSV file
TABLE_NAME = "item_custodies"            # SQL table name
OUTPUT_SQL = "item_custodies.sql"       # Output SQL file

def csv_to_sql():
    # Load CSV
    df = pd.read_csv(CSV_FILE)

    # Drop duplicates
    df = df.drop_duplicates()

    # Generate SQL insert statements
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            values = []
            for v in row:
                if pd.isna(v):
                    values.append("NULL")
                elif isinstance(v, (int, float)):
                    values.append(str(v))
                else:
                    # Escape single quotes
                    values.append(f"'{str(v).replace("'", "''")}'")
            sql = f"INSERT INTO {TABLE_NAME} VALUES ({', '.join(values)});"
            f.write(sql + "\n")

    print(f" SQL file generated: {OUTPUT_SQL}")

if __name__ == "__main__":
    csv_to_sql()
