#! /usr/bin/env python

import json
import os
import socket

LISTEN_PORT = 8888
DB_FILE_PATH = 'db.json'

def parse_cmd(data):
    parts = data.split()
    if len(parts) < 2:
        return {'cmd': 'invalid', 'reason': 'bad formatting'}

    if parts[0] == 'get':
        return {'cmd': 'get', 'key': parts[1]}
    elif parts[0] == 'set':
        return {'cmd': 'set', 'key': parts[1], 'value': parts[2]}
    elif parts[0] == 'del':
        return {'cmd': 'del', 'key': parts[1]}
    else:
        return {'cmd': 'invalid', 'reason': 'bad command'}

def deserialize_db():
    try:
        with open(DB_FILE_PATH) as db_file:
            db_data = db_file.read()
            return json.loads(db_data)
    except:
        return {}

def serialize_db(db):
    with open(DB_FILE_PATH + '.tmp', 'w') as db_file:
        data = json.dumps(db)
        db_file.write(data)
    os.rename(DB_FILE_PATH + '.tmp', DB_FILE_PATH)

def get(key):
    db = deserialize_db()
    return db.get(key, 'not found')

def set_k(key, value):
    db = deserialize_db()
    db[key] = value
    serialize_db(db)

def del_k(key):
    db = deserialize_db()
    del db[key]
    serialize_db(db)


# Creating a new socket that is AF_INET (IP) and SOCK_STREAM (TCP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Tell kernel to listen on port LISTEN_PORT on all network interfaces (0.0.0.0, wildcard!)
server_socket.bind(('0.0.0.0', LISTEN_PORT))

# Tell kernel to start accepting sockets in the background that we can later accept (accept is a python call)
# `10` is the number of people in the waiting room (TCP backlog size)
server_socket.listen(10)

while True:
    print('waiting for client to connect . . . . ??? ')
    
    # Accepts first connected socket since listen was called (above), or blocks until a remote connects
    (client_socket, (client_address, client_port)) = server_socket.accept()

    print('client', client_address, 'connected')

    # Try to read up to 1024 bytes of information from socket
    data = client_socket.recv(1024)

    print('client sent:', data)

    cmd = parse_cmd(data)

    if cmd['cmd'] == 'invalid':
        print('client sent bad command')
        client_socket.send('):\n')
    elif cmd['cmd'] == 'get':
        value = get(cmd['key'])
        client_socket.send(value + '\n')
    elif cmd['cmd'] == 'set':
        set_k(cmd['key'], cmd['value'])
        client_socket.send('ok!\n')
    elif cmd['cmd'] == 'del':
        del_k(cmd['key'])
        client_socket.send('ok!\n')

    # Close client socket
    # Don't leak file descriptors !!
    client_socket.close()
