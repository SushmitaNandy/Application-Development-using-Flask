from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField , RadioField
from wtforms.validators import DataRequired, EqualTo, Length, length, Email , Regexp
from wtforms.widgets import TextArea
#from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileAllowed
from application.models import *



class SignUpForm(FlaskForm):

	fname = StringField("First Name", validators=[DataRequired()])
	lname = StringField("Last Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired(),Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
'Usernames must have only letters, '
'numbers, dots or underscores')])
	email = StringField("Email", validators=[DataRequired(),Email()])
	profile_description = StringField(u'Text', widget=TextArea())
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password', message='Passwords do not match!!')])
	profile_img = FileField("Upload Profile Picture", validators=[FileAllowed(["jpg", "png","jpeg","gif"])])
	submit_btn = SubmitField("Register")
    
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Username already in use.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Email already registered.')

class ForgotPassword(FlaskForm):	
	email = StringField("Email", validators=[Email()]) #DataRequired(),
	username = StringField("Username", validators=[Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
	'Usernames must have only letters, ''numbers, dots or underscores')])
	reset_btn = SubmitField("Reset Password")

	def validate(self):
		initial_validation = super(ForgotPassword, self).validate()
		if not initial_validation:
			return False
		user = User.query.filter_by(email=self.email.data).first()
		if not user:
			self.email.errors.append('Unknown email')
			return False
		elif user.username != self.username.data:
			self.username.errors.append('Username not matching with registered email')
			return False
		else:
			return True

class ResetPassword(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password', message='Passwords do not match!!')])
	submit_btn = SubmitField("Reset")

class LoginForm(FlaskForm):

	login_id= StringField("Enter username or email", validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	login_btn = SubmitField("Login")

	def validate(self):
		initial_validation = super(LoginForm, self).validate()
		if not initial_validation:
			return False
		
		if '@' in self.login_id.data:
			user = User.query.filter_by(email=self.login_id.data).first()
			if not user:
				self.login_id.errors.append('Unknown email')
				return False
		else:
			user = User.query.filter_by(username=self.login_id.data).first()
			if not user:
				self.login_id.errors.append('Unknown username')
				return False
		if not user.verify_password(self.password.data):
			self.password.errors.append('Invalid password')
			return False
		return True

class EditUserForm(FlaskForm):

	fname = StringField("First Name", validators=[DataRequired()])
	lname = StringField("Last Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired(),Email()])
	password = PasswordField('Type Password if you wish to change!')
	password2 = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords do not match!!')])
	profile_description = StringField(u'Text', widget=TextArea())
	profile_img = FileField("Upload Profile Picture", validators=[FileAllowed(["jpg", "png","jpeg","gif"])])
	edit_btn= SubmitField("Edit")
