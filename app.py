import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

conn = psycopg2.connect(dbname='usermgt', user='postgres', password='postgres', host='localhost')

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
        active BOOLEAN NOT NULL DEFAULT True,
        org_id INT
    );
    ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS organizations(
    org_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    phone VARCHAR,
    city VARCHAR,
    state VARCHAR,
    active BOOLEAN NOT NULL DEFAULT True,
    type VARCHAR
    );
''')

conn.commit()

def get_user_from_list(user_feilds):
    return {
        'user_id':user_feilds[0],
        'first_name':user_feilds[1],
        'last_name':user_feilds[2],
        'email':user_feilds[3],
        'phone':user_feilds[4],
        'city':user_feilds[5],
        'state':user_feilds[6],
        'organization':{
            'ord_id':user_feilds[9],
            'name':user_feilds[10],
            'phone':user_feilds[11],
            'city':user_feilds[12],
            'state':user_feilds[13],
            'active':user_feilds[14],
            'type':user_feilds[15],
        },
        'active':user_feilds[8]
            } 

def get_org_from_list(org_feilds):
    return {
        'ord_id':org_feilds[0],
        'name':org_feilds[1],
        'phone':org_feilds[2],
        'city':org_feilds[3],
        'state':org_feilds[4],
        'active':org_feilds[5],
        'type':org_feilds[6],
    }

def user_exists(user_id):
    if not user_id.isnumeric():
        return False
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, org_id, active FROM users WHERE user_id=%s;", (user_id,))
    results = cursor.fetchone()
    
    return results is not None

def org_exists(org_id):
    if not org_id.isnumeric():
        return False
    cursor.execute("SELECT org_id, name, phone, city, state, active, type FROM organizations WHERE org_id=%s;", (org_id,))
    results = cursor.fetchone()
    
    return results is not None

@app.route('/org/add', methods=['POST'])
def add_organization():
    data = request.json

    name = data.get('name')
    phone = data.get('phone')
    city = data.get('city')
    state = data.get('state')
    active = True
    if 'active' in data:
        active = (data.get('active') != 'false')
    type = data.get('type')
    
    cursor.execute(
        '''
        INSERT INTO organizations (name, phone, city, state, active, type)
        VALUES (%s, %s, %s, %s, %s, %s);
        ''', (name, phone, city, state, active, type))
    conn.commit()

    return 'Organization added', 201

@app.route('/orgs/get', methods=['GET'])
def get_all_active_orgs():
    cursor.execute("""
        SELECT org_id, name, phone, city, state, active, type
        FROM organizations 
        WHERE active='t';""")
    results = cursor.fetchall()

    if results:
        orgs = []
        for o in results:
            org_record = get_org_from_list(o)
            orgs.append(org_record)
        return jsonify(orgs), 200
    
    return 'No organizations found', 404

@app.route('/org/get/<org_id>', methods=['GET'])
def get_org_by_id(org_id):
    if not org_id.isnumeric():
        return (f"Invalid org_id: {org_id}"), 400
    
    cursor.execute('''
    SELECT org_id, name, phone, city, state, active, type
    FROM organizations WHERE org_id=%s;''', (org_id,))
    
    o = cursor.fetchone()

    if o:
        org_record = get_org_from_list(o)
        return jsonify(org_record), 200
    
    return 'No organizastion found', 404

@app.route('/org/update/<org_id>', methods=['POST', 'PUT', 'PATCH'])
def update_org(org_id):
    if not org_exists(org_id):
        return jsonify(f"User {org_id} not found!"), 404

    request_params = request.json

    feilds = ['org_id','name', 'phone', 'city', 'state','active', 'type']

    update_feilds = []
    feild_values = []
    
    for feild in feilds:
        if feild in request_params.keys():
            update_feilds.append(f'{feild} = %s')
            feild_values.append(request_params[feild])
    feild_values.append(org_id)

    update_query = 'UPDATE organizations SET ' + ','.join(update_feilds) + ' WHERE org_id=%s;'
    cursor.execute(update_query, feild_values)
    conn.commit()

    return get_org_by_id(org_id)

@app.route('/org/delete/<org_id>', methods=['DELETE'])
def delete_org_by_id(org_id):
    if not org_exists(org_id):
        return (f"User {org_id} not found!"), 404

    cursor.execute("DELETE FROM organizations WHERE org_id=%s;", (org_id,))
    conn.commit()
    return("Organization Deleted"), 200

@app.route('/org/deactivate/<org_id>', methods=['POST','PATCH','PUT'])
def deactivate_org_by_id(org_id):
    return activate_org_by_id(org_id, False)

@app.route('/org/activate/<org_id>', methods=['POST','PATCH','PUT'])
def activate_org_by_id(org_id, set_active = True):    
    if not org_exists(org_id):
        return jsonify(f"Organization {org_id} not found!"), 404

    cursor.execute("UPDATE organizations SET active=%s WHERE org_id=%s;", (set_active, org_id))
    conn.commit()

    return(f"Organization active set to {set_active}"), 200

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
        "state":"Utah",
        "org_id":3
    }
    '''
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    city = data.get('city')
    state = data.get('state')
    org_id = data.get('org_id')

    try:    
        cursor.execute(
            '''
            INSERT INTO users (first_name, last_name, email, phone, city, state, org_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            ''', (first_name, last_name, email, phone, city, state, org_id))
    except: 
        cursor.execute("ROLLBACK")
        return jsonify("Error adding user!")
    
    conn.commit()

    return 'User added', 201

@app.route('/users/get', methods=['GET'])
def get_all_active_users():
    cursor.execute("""
        SELECT 
            u.user_id, u.first_name, u.last_name, u.email, u.phone, u.city, u.state, u.org_id, u.active, 
            o.org_id, o.name, o.phone, o.city, o.state, o.active, o.type
        FROM users u
            LEFT OUTER JOIN organizations o
                ON u.org_id = o.org_id 
        WHERE u.active='t';""")
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
    
    cursor.execute('''
    SELECT u.user_id, u.first_name, u.last_name, u.email, u.phone, u.city, u.state, u.org_id, u.active, 
            o.org_id, o.name, o.phone, o.city, o.state, o.active, o.type
    FROM users u
        LEFT OUTER JOIN organizations o
            ON u.org_id = o.org_id
            WHERE user_id=%s;''', (user_id,))
    
    u = cursor.fetchone()

    if u:
        user_record = get_user_from_list(u)
        return jsonify(user_record), 200
    
    return 'No user found', 404

@app.route('/user/update/<user_id>', methods=['POST', 'PUT', 'PATCH'])
def update_user(user_id):
    if not user_exists(user_id):
        return jsonify(f"User {user_id} not found!"), 404

    request_params = request.json

    feilds = ['user_id','first_name', 'last_name', 'email', 'phone', 'city', 'state','org_id','active']

    update_feilds = []
    feild_values = []
    
    # for feild in feilds:
    #     if feild in request_params.keys():
    #         update_feilds.append(f'{feild} = %s')
    #         feild_values.append(request_params[feild])
    # This will ignore invalid feilds
    for feild in request_params.keys():
        if feild in feilds:
            update_feilds.append(f'{feild} = %s')
            feild_values.append(request_params[feild])
        else:
            return jsonify(f'Feild {feild} is invalid'), 400    
        # this doesn;t ignore, it gives an error instead
    feild_values.append(user_id)

    update_query = 'UPDATE users SET ' + ','.join(update_feilds) + ' WHERE user_id=%s;'
    cursor.execute(update_query, feild_values)
    conn.commit()

    return get_user_by_id(user_id) 

@app.route('/user/delete/<user_id>', methods=['DELETE'])
def delete_user_by_id(user_id):
    if not user_exists(user_id):
        return (f"User {user_id} not found!"), 404

    cursor.execute("DELETE FROM users WHERE user_id=%s;", (user_id,))
    conn.commit()
    return("User Deleted"), 200

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8086 )