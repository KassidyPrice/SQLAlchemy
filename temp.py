import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

conn = psycopg2.connect(dbname='usermgt', user='postgres',password='postgres', host='localhost')

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        first_name VARCHAR NOT NULL,
        last_name VARCHAR,
        email VARCHAR NOT NULL UNIQUE,
        phone VARCHAR,
        city VARCHAR,
        state VARCHAR,
        active BOOLEAN NOT NULL DEFAULT True
    );
    ''')

conn.commit()

@app.route('/user/add', methods=['POST'])
def add_user():
    data = request.json
    '''
    {
        "first_name":"Billy",
        "last_name":"Jones",
        "email":"billyjones43244324@gmail.com",
        "phone":"8018018011",
        "city":"Provo",
        "state":"Utah"
    }
    '''
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    city = data.get('city')
    state = data.get('state')
    
    cursor.execute(
        '''
        INSERT INTO users (first_name, last_name, email, phone, city, state)
        VALUES (%s, %s, %s, %s, %s, %s);
        ''', (first_name, last_name, email, phone, city, state))
    conn.commit()

    return 'User added', 201

@app.route('/user/update/<user_id>', methods=['POST', 'PUT', 'PATCH'])
def update_user(user_id):
    data = request.json
    '''
    {
        "first_name":"Billy",
        "last_name":"Jones",
        "email":"billyjones5@gmail.com",
        "phone":"8018018011",
        "city":"Provo",
        "state":"Utah"
    }
    '''

    if not user_id.isnumeric():
        return (f"Invalid user_id: {user_id}"), 400
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE user_id=%s;", (user_id,))
    results = cursor.fetchone()
    
    if not results:
        return (f"User {user_id} not found!"), 404

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    city = data.get('city')
    state = data.get('state')
    
    cursor.execute(
        '''
        UPDATE users SET first_name = %s, last_name = %s, email = %s, phone = %s, city = %s, state = %s WHERE user_id=%s;
        ''', (first_name, last_name, email, phone, city, state, user_id))
    conn.commit()

    return 'User updated', 201  

def get_user_from_list(user_feilds):
    return {
        'user_id':user_feilds[0],
        'first_name':user_feilds[1],
        'last_name':user_feilds[2],
        'email':user_feilds[3],
        'phone':user_feilds[4],
        'city':user_feilds[5],
        'state':user_feilds[6],
        'active':user_feilds[7]
            } 

@app.route('/users/get', methods=['GET'])
def get_all_active_users():
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE active='t';")
    results = cursor.fetchall()

    if results:
        users = []
        for u in results:
            user_record = get_user_from_list(u)
            users.append(user_record)
        return jsonify(users), 200
    
    return 'No users found', 404

@app.route('/user/get/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    if not user_id.isnumeric():
        return (f"Invalid user_id: {user_id}"), 400
    
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE user_id=%s;", (user_id,))
    u = cursor.fetchone()

    if u:
        user_record = get_user_from_list(u)
        return jsonify(user_record), 200
    
    return 'No user found', 404

def user_exists(user_id):
    if not user_id.isnumeric():
        return False
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE user_id=%s;", (user_id,))
    results = cursor.fetchone()
    
    return results is not None

# def activate_user(user_id, set_active = True):
#     if not user_exists(user_id):
#         return jsonify(f"User {user_id} not found!"), 404

#     cursor.execute("UPDATE users SET active=%s WHERE user_id=%s;", (set_active, user_id))
#     conn.commit()

#     return(f"User active set to {set_active}"), 200

@app.route('/user/deactivate/<user_id>', methods=['POST','PATCH','PUT'])
def deactivate_user_by_id(user_id):
    # return activate_user(user_id, False)
    return activate_user_by_id(user_id, False)

@app.route('/user/activate/<user_id>', methods=['POST','PATCH','PUT'])
def activate_user_by_id(user_id, set_active = True):    
    # return activate_user(user_id)
    if not user_exists(user_id):
        return jsonify(f"User {user_id} not found!"), 404

    cursor.execute("UPDATE users SET active=%s WHERE user_id=%s;", (set_active, user_id))
    conn.commit()

    return(f"User active set to {set_active}"), 200
    
@app.route('/user/delete/<user_id>', methods=['POST','PATCH','PUT'])
def delete_user_by_id(user_id):
    if not user_exists(user_id):
        return (f"User {user_id} not found!"), 404

    cursor.execute("DELETE FROM users WHERE user_id=%s;", (user_id,))
    conn.commit()
    return("User Deleted"), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8086 )

'''Flask is a micro-framework, it is the web server and takes care of all the HTTP requests and responses, app is an instance of the Flask class, postgresql is building the CRUDDAs for the database, SQLAlchemy builds the SQL queries for us.'''