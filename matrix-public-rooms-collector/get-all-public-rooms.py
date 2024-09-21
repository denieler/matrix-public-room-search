import sqlite3
import requests
import time
import urllib3

# Disable SSL warnings (optional)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_server_list(filename='servers.txt'):
    """Read the list of servers from a file."""
    with open(filename, 'r') as f:
        servers = [line.strip() for line in f if line.strip()]
    return servers

def get_public_rooms(server):
    """Fetch public rooms from a Matrix server."""
    rooms = []
    url = f'https://{server}/_matrix/client/r0/publicRooms'
    headers = {
        'User-Agent': 'Matrix Public Rooms Crawler'
    }
    params = {
        'limit': 100  # Maximum number of rooms per request
    }
    session = requests.Session()
    next_batch = None
    while True:
        if next_batch:
            params['since'] = next_batch
        try:
            response = session.get(url, headers=headers, params=params, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            chunk = data.get('chunk', [])
            rooms.extend(chunk)
            next_batch = data.get('next_batch')
            if not next_batch:
                break
            # Sleep to avoid rate limiting
            time.sleep(0.5)
        except requests.exceptions.SSLError as ssl_err:
            print(f"SSL Error when connecting to {server}: {ssl_err}")
            break
        except requests.exceptions.RequestException as req_err:
            print(f"Request error when connecting to {server}: {req_err}")
            break
        except Exception as e:
            print(f"Unexpected error when connecting to {server}: {e}")
            break
    return rooms

def save_rooms_to_db(cursor, server, rooms):
    """Save rooms data to the SQLite database, updating existing rooms."""
    saved_rooms_count = 0
    for room in rooms:
        num_members = room.get('num_joined_members', 0)
        if num_members < 5:
            continue  # Skip rooms with fewer than 5 members
        cursor.execute('''
            INSERT INTO rooms (
                server,
                room_id,
                name,
                topic,
                num_joined_members,
                world_readable,
                guest_can_join,
                avatar_url,
                canonical_alias,
                aliases
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(room_id) DO UPDATE SET
                server=excluded.server,
                name=excluded.name,
                topic=excluded.topic,
                num_joined_members=excluded.num_joined_members,
                world_readable=excluded.world_readable,
                guest_can_join=excluded.guest_can_join,
                avatar_url=excluded.avatar_url,
                canonical_alias=excluded.canonical_alias,
                aliases=excluded.aliases
        ''', (
            server,
            room.get('room_id'),
            room.get('name'),
            room.get('topic'),
            num_members,
            int(room.get('world_readable', False)),
            int(room.get('guest_can_join', False)),
            room.get('avatar_url'),
            room.get('canonical_alias'),
            ','.join(room.get('aliases', []))
        ))
        saved_rooms_count += 1
    return saved_rooms_count

def main():
    # Connect to the SQLite database (or create it)
    conn = sqlite3.connect('matrix_rooms.db')
    cursor = conn.cursor()
    # Create the 'rooms' table if it doesn't exist, with UNIQUE constraint on room_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server TEXT,
            room_id TEXT UNIQUE,
            name TEXT,
            topic TEXT,
            num_joined_members INTEGER,
            world_readable INTEGER,
            guest_can_join INTEGER,
            avatar_url TEXT,
            canonical_alias TEXT,
            aliases TEXT
        )
    ''')
    # Fetch the list of servers
    servers = get_server_list()
    # Fetch and save public rooms from each server
    for server in servers:
        print(f"Fetching public rooms from {server}")
        rooms = get_public_rooms(server)
        if rooms:
            saved_rooms = save_rooms_to_db(cursor, server, rooms)
            conn.commit()
            print(f"Saved/Updated {saved_rooms} rooms from {server} (rooms with >=5 members)")
        else:
            print(f"No rooms found or error fetching from {server}")
    # Close the database connection
    conn.close()

if __name__ == '__main__':
    main()
