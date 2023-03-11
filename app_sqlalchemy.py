from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from db import db, init_db
import uuid

from users import Users, user_schema, users_schema
from organizations import Organizations, org_schema, orgs_schema


app = Flask(__name__)

database_host = "127.0.0.1:5432" 
database_name = "usermgt2"
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:postgres@{database_host}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app, db)

def create_all():
    with app.app_context():
        db.create_all()

        # TODO: Fill in stuff later

def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))

        return True
    except ValueError:
        return False
    

@app.route('/org/add', methods=['POST'])
def add_organization():
    data = request.json

    name = data.get('name')
    if not name or len(name) < 1:
        return "Organization name cannot be empty", 400
    phone = data.get('phone')
    if len(phone) > 20:
        return "Phone number cannot be longer than 20 characters", 400
    city = data.get('city')
    state = data.get('state')
    active = True
    if 'active' in data:
        active = (data.get('active') != 'false')
    type = data.get('type')

    new_org_record = Organizations(name, phone, city, state, type, active)
    db.session.add(new_org_record)
    db.session.commit()

    return jsonify(org_schema.dump(new_org_record)), 201


@app.route('/orgs/get', methods=['GET'])
def get_all_active_orgs():
    org_records = db.session.query(Organizations).filter(Organizations.active==True).all()

    if org_records:
        return jsonify(orgs_schema.dump(org_records)), 200
    
    return 'No organizations found', 404

@app.route('/org/get/<org_id>', methods=['GET'])
def get_org_by_id(org_id):
    if not is_valid_uuid(org_id):
        return (f"Invalid org_id: {org_id}"), 400
    
    org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
    
    if org_record:
        return jsonify(org_schema.dump(org_record)), 200
                
    return 'No organization found', 404

@app.route('/org/update/<org_id>', methods=['POST', 'PUT', 'PATCH'])
def update_org(org_id):
    if not is_valid_uuid(org_id):
        return jsonify(f"Invalid org_id: {org_id}"), 404

    # feilds = ['org_id','name', 'phone', 'city', 'state', 'active', 'type']

    org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
    
    if not org_record:
        return jsonify(f"Organization {org_id} not found!"), 404

    request_params = request.json
    
    if 'name' in request_params:
        org_record.name = request_params['name']
    if 'phone' in request_params:
        org_record.phone = request_params['phone']
    if 'city' in request_params:
        org_record.city = request_params['city']
    if'state' in request_params:
        org_record.state = request_params['state']
    if 'active' in request_params:
        org_record.active = request_params.get('active')
    if 'type' in request_params:
        org_record.type = request_params['type']

    db.session.commit()

    return get_org_by_id(org_id)

@app.route('/org/delete/<org_id>', methods=['DELETE'])
def delete_org_by_id(org_id):
    if not is_valid_uuid(org_id):
        return jsonify(f"Invalid org_id: {org_id}"), 404
    
    org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

    if not org_record:
        return jsonify(f"Organization {org_id} not found!"), 404

    db.session.delete(org_record)
    db.session.commit()
    return("Organization Deleted"), 200

@app.route('/org/deactivate/<org_id>', methods=['POST','PATCH','PUT'])
def deactivate_org_by_id(org_id):
    return activate_org_by_id(org_id, False)

@app.route('/org/activate/<org_id>', methods=['POST','PATCH','PUT'])
def activate_org_by_id(org_id, set_active = True):    
    if not is_valid_uuid(org_id):
        return jsonify(f"Invalid org_id: {org_id}"), 404
    
    org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

    if not org_record:
        return jsonify(f"Organization {org_id} not found!"), 404
    
    org_record.active = set_active
    db.session.commit()

    return jsonify(org_schema.dump(org_record)), 200

@app.route('/user/add', methods=['POST'])
def add_user():
    data = request.json
 
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    if not email:
        return "Email must be a non-empty string", 400
    phone = data.get('phone')
    if len(phone) > 20:
        return "Phone number cannot be longer than 20 characters", 400
    city = data.get('city')
    state = data.get('state')
    org_id = data.get('org_id')

    new_user_record = Users(first_name, last_name, email, phone, city, state, org_id)
    db.session.add(new_user_record)
    db.session.commit()

    return jsonify(user_schema.dump(new_user_record)), 201

@app.route('/users/get', methods=['GET'])
def get_all_active_users():
    user_records = db.session.query(Users).filter(Users.active==True).all()

    if user_records:
        return jsonify(users_schema.dump(user_records)), 200
    
    return 'No users found', 404

@app.route('/user/get/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    if not is_valid_uuid(user_id):
        return (f"Invalid user_id: {user_id}"), 400
    
    user_record = db.session.query(Users).filter(Users.user_id == user_id).first()
    
    if not user_record:
        return 'No user found', 404
        
    return jsonify(user_schema.dump(user_record)), 200

@app.route('/user/update/<user_id>', methods=['POST', 'PUT', 'PATCH'])
def update_user(user_id):
    if not is_valid_uuid(user_id):
        return (f"Invalid user_id: {user_id}"), 400

    request_params = request.json

    # feilds = ['user_id','first_name', 'last_name', 'email', 'phone', 'city', 'state','org_id','active']

    user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

    if not user_record:
        return jsonify(f"User {user_id} not found!"), 404
        
    if 'first_name' in request_params:
        user_record.first_name = request_params['first_name']
    if 'last_name' in request_params:
        user_record.last_name = request_params['last_name']
    if 'email' in request_params:
        user_record.email = request_params['email']
    if 'phone' in request_params:
        user_record.phone = request_params['phone']
    if 'city' in request_params:
        user_record.city = request_params['city']
    if 'state' in request_params:
        user_record.state = request_params['state']   
    if 'org_id' in request_params: 
        user_record.org_id = request_params['org_id']
    if 'active' in request_params:
        user_record.active = request_params.get('active')
    
    db.session.commit()

    return get_user_by_id(user_id)

@app.route('/user/delete/<user_id>', methods=['DELETE'])
def delete_user_by_id(user_id):
    if not is_valid_uuid(user_id):
        return (f"Invalid user_id: {user_id}"), 400

    user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

    if not user_record:
        return jsonify(f"User {user_id} not found!"), 404
    
    db.session.delete(user_record)
    db.session.commit()
    
    return("User Deleted"), 200

@app.route('/user/deactivate/<user_id>', methods=['POST','PATCH','PUT'])
def deactivate_user_by_id(user_id):
    return activate_user_by_id(user_id, False)

@app.route('/user/activate/<user_id>', methods=['POST','PATCH','PUT'])
def activate_user_by_id(user_id, set_active = True):  
    if not is_valid_uuid(user_id):
        return (f"Invalid user_id: {user_id}"), 400

    user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

    if not user_record:
        return jsonify(f"User {user_id} not found!"), 404
    
    user_record.active = set_active

    db.session.commit()

    return jsonify(user_schema.dump(user_record)), 200  


if __name__ == '__main__':
    create_all()
    app.run(host='0.0.0.0', port=8086 )