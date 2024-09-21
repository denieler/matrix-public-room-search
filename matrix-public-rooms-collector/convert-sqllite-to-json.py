import sqlite3
import json

def export_db_to_json(db_file='matrix_rooms.db', json_file='rooms.json'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM rooms')
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    data = []
    for row in rows:
        record = dict(zip(columns, row))
        data.append(record)

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    conn.close()
    print(f"Exported {len(data)} records to {json_file}")

if __name__ == '__main__':
    export_db_to_json()
