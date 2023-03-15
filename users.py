from sqlalchemy.dialects.postgresql import UUID
import uuid

from db import db
import marshmallow as ma

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String())
    email = db.Column(db.String(), nullable=False, unique=True)
    phone = db.Column(db.String())
    city = db.Column(db.String())
    state = db.Column(db.String())
    active = db.Column(db.Boolean(), nullable=False, default=True)
    org_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organizations.org_id'))

    organization = db.relationship('Organizations', back_populates ='users')

    def __init__(self, first_name='', last_name='', email='', phone='', city='', state='', org_id=uuid.uuid4, active=True):

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.city = city
        self.state = state
        self.active = active
        self.org_id = org_id

class UsersSchema(ma.Schema):
    class Meta:
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone', 'city', 'state', 'age', 'org_id','organization', 'active']

    organization = ma.fields.Nested('OrganizationsSchema', only=['org_id', 'name'])

user_schema = UsersSchema()
users_schema = UsersSchema(many=True)
