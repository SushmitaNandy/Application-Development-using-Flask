from flask_restful import Resource,Api,fields,marshal_with,reqparse,request
from application.database import *
from application.models import *
from werkzeug.exceptions import HTTPException
from flask import make_response

api=Api()

class DuplicationError(HTTPException):
    def __init__(self, status_code, mess):
        self.response = make_response(mess, status_code)

class NotFoundError(HTTPException):
    def __init__(self, status_code, mess):
        self.response = make_response(mess, status_code)

resource_fields = {
    'id':   fields.Integer,
    'first_name':  fields.String,
    'last_name':  fields.String,
    'email':     fields.String
}

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('username')


class UserApi(Resource):
    @marshal_with(resource_fields)
    def get(self,username):
        user=User.query.filter_by(username=username).first()
        if user is None:
            raise NotFoundError(404, "User not found")
        return user
    
    @marshal_with(resource_fields)
    def put(self):
        if "Exsisting Username" in request.form:
            uname=request.form['Exsisting Username']
            user= User.query.filter_by(username=uname).first()
            if request.form['New First Name']:
                user.first_name=request.form['New First Name']
            if request.form['New Last Name']:
                user.last_name=request.form['New Last Name']
            if request.form['New Password']:
                user.password=generate_password_hash(request.form['New Password'])
            db.session.add(user)
            db.session.commit()
        return user
    
    @marshal_with(resource_fields)
    def post(self):
        if "Username" in request.form:
            uname=request.form['Username']
            user= User.query.filter_by(username=uname).first()
            if user is not None:
                raise DuplicationError(409, "Username already exists")
            email_=request.form['Email']
            user1= User.query.filter_by(email=email_).first()
            if user1 is not None:
                raise DuplicationError(409, "Email already exists")
            fname=request.form['First Name']
            lname=request.form['Last Name']
            passwd=generate_password_hash(request.form['Password']) 
            bio=request.form['Profile Description']

            insert_user=User(username=uname,first_name=fname,last_name=lname,email=email_,password=passwd,
                        profile_description=bio)
            db.session.add(insert_user)
            db.session.commit()
            return insert_user


api.add_resource(UserApi,"/api/user/<username>", "/api/user")


