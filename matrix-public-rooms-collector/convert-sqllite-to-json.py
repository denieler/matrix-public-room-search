import sqlite3
import json

def export_db_to_json(db_file='matrix_rooms.db'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Get all rooms
    cursor.execute('SELECT * FROM rooms')
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    # Convert to list of dictionaries
    data = []
    for row in rows:
        record = dict(zip(columns, row))
        data.append(record)

    # Filter out rooms with Russian content and less than 5 members
    filtered_data = [
        room for room in data 
        if room['num_joined_members'] >= 5 
        and not (
            (room.get('name', '') or '').lower().find('русск') >= 0
            or (room.get('name', '') or '').lower().find('russian') >= 0
            or (room.get('topic', '') or '').lower().find('русск') >= 0
            or (room.get('topic', '') or '').lower().find('russian') >= 0
        )
    ]

    # Sort rooms by number of members
    filtered_data.sort(key=lambda x: x['num_joined_members'], reverse=True)

    # Export all rooms
    with open('rooms.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)
    print(f"Exported {len(filtered_data)} records to rooms.json")

    # Export top 15 rooms
    top_15_rooms = filtered_data[:15]
    with open('rooms_15.json', 'w', encoding='utf-8') as f:
        json.dump(top_15_rooms, f, ensure_ascii=False, indent=4)
    print(f"Exported {len(top_15_rooms)} records to rooms_15.json")

    conn.close()

if __name__ == '__main__':
    export_db_to_json()
