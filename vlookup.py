import csv
import re

INPUT_T1 = "employees_data.csv"
INPUT_T2 = "cem_data.csv"
OUTPUT_SQL = "vlookup.sql"

t1_data = {}
with open(INPUT_T1, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (row["first_name"].strip().upper(), row["last_name"].strip().upper())
        t1_data[key] = row["uuid"]

def parse_name(full_name):
    """
    Example input: "DELOS REYES, JULIETA A."
    Output: ("JULIETA", "DELOS REYES")
    """
    full_name = full_name.strip().upper()
    if "," in full_name:
        last, first = full_name.split(",", 1)
        last = last.strip()
        # remove middle initials (A., O., etc.)
        first = re.sub(r"\s+[A-Z]\.?$", "", first.strip())
        return first, last
    return None, None

# Open output file
with open(OUTPUT_SQL, "w", encoding="utf-8") as out:
    with open(INPUT_T2, newline="", encoding="utf-8-sig") as f: 
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
        for row in reader:
            raw_name = row["name"].strip('"').strip()
            first, last = parse_name(raw_name)

            if (first, last) in t1_data:
                uuid = t1_data[(first, last)]
                sql = (
                    f"INSERT INTO your_table (uuid, first_name, last_name, name) "
                    f"VALUES ('{uuid}', '{first.title()}', '{last.title()}', '{raw_name}');\n"
                )
                out.write(sql)
            else:
                out.write(f"-- No match found for: {raw_name}\n")

print(f"SQL file generated: {OUTPUT_SQL}")