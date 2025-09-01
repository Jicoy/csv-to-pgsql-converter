import pandas as pd
import sys
import html
from decimal import Decimal, InvalidOperation

FIELD_MAX_LENGTHS = {
    "status": 50,
    "remarks": 255,
    "condition": 50,
}

DECIMAL_FIELDS = {"unit_val"}
INTEGER_FIELDS = {"estimated_life", "qty_property_card", "qty_physical_count"}
BOOLEAN_FIELDS = {"is_prop_upowned"}
HTML_FIELDS = {"description"} 

def format_description(value: str) -> str:
    """
    Format description as HTML:
    - Escape HTML special chars
    - Convert newlines to <br>
    - Wrap in <p> by default
    """
    if value is None or pd.isna(value) or str(value).strip() == "":
        return "NULL"

    safe_val = html.escape(str(value))
    safe_val = safe_val.replace("\r\n", "\n").replace("\r", "\n").strip()
    safe_val = safe_val.replace("\n", "<br>")
    return f"'<p>{safe_val}</p>'"

def trim_value(column: str, value: str) -> str:
    """
    Trim the value according to FIELD_MAX_LENGTHS, if defined.
    Also cleans up newlines and escapes single quotes.
    """
    
    col = column.lower()

    if col == "condition" and (value is None or pd.isna(value) or str(value).strip() == ""):
        return "'SERVICEABLE'"


    if col in DECIMAL_FIELDS:
        if value is None or pd.isna(value) or str(value).strip() == "":
            return "0"
        try:
            # Normalize commas, convert to Decimal
            cleaned = str(value).replace(",", "")
            return str(Decimal(cleaned))
        except InvalidOperation:
            return "0"

    if col in INTEGER_FIELDS:
        if value is None or pd.isna(value) or str(value).strip() == "":
            return "NULL"
        try:
            return str(int(float(value)))
        except ValueError:
            return "NULL"

    if col in BOOLEAN_FIELDS:
        if value is None or pd.isna(value) or str(value).strip() == "":
            return "FALSE"
        val_str = str(value).strip().lower()
        if val_str in {"1", "true", "yes", "y"}:
            return "TRUE"
        return "FALSE"

    if col in HTML_FIELDS:
        return format_description(value)

    if value is None or pd.isna(value):
        return "NULL"

    safe_val = str(value).replace("'", "''").replace("\n", " ").replace("\r", " ")

    if col in FIELD_MAX_LENGTHS:
        max_len = FIELD_MAX_LENGTHS[col]
        if len(safe_val) > max_len:
            safe_val = safe_val[:max_len]

    return f"'{safe_val}'"

def parse_extra_arg(arg, num_rows):
    """
    Parse extra CLI arg like:
      registry_id:start=1:end=20
    Returns (column_name, [values]) or (None, None) if invalid.
    """
    if ":" not in arg:
        return None, None

    col, defn = arg.split(":", 1)
    parts = dict(part.split("=") for part in defn.split(":") if "=" in part)

    if "start" in parts:
        try:
            start = int(parts["start"])
            return col, list(range(start, start + num_rows))
        except ValueError:
            return None, None
    return None, None

def csv_to_pgsql(csv_file, table_name, output_sql, extra_col=None, extra_values=None):
    df = pd.read_csv(csv_file)

    with open(output_sql, "w", encoding="utf-8") as f:
        for i, row in df.iterrows():
            values = []
            columns = []

            # Add extra_col first
            if extra_col and extra_values:
                columns.append(extra_col)
                val = extra_values[i]
                if isinstance(val, (int, float)):
                    values.append(str(int(val)))
                else:
                    values.append(trim_value(extra_col, val))

            # Then the CSV columns
            for col, val in row.items():
                columns.append(col)
                values.append(trim_value(col, val))

            insert_stmt = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
            f.write(insert_stmt)

    print(f"SQL script written to {output_sql}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python csv_to_pgsql.py <csv_file> <table_name> <output_sql> [extra_arg]")
        sys.exit(1)

    csv_file = sys.argv[1]
    table_name = sys.argv[2]
    output_sql = sys.argv[3]
    
    extra_col, extra_values = None, None
    if len(sys.argv) > 4:
        df_tmp = pd.read_csv(csv_file)
        extra_col, extra_values = parse_extra_arg(sys.argv[4], len(df_tmp))

    csv_to_pgsql(csv_file, table_name, output_sql, extra_col, extra_values)
