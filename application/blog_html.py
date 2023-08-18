from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, length, Email , Regexp
from wtforms.widgets import TextArea
#from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileAllowed
from application.models import *

class BlogForm(FlaskForm):
    choices = [('Travel','Travel'),('Food','Food'),('Health','Health'),('Fashion','Fashion'),
						('Personal','Personal'),('Movies','Movies'),('Sports','Sports')]
    blog_title = StringField("Blog Title", validators=[DataRequired()])
    blog_category = SelectField(label='Category', choices=choices , validators=[DataRequired()])
    blog_text = StringField(u'Text', widget=TextArea())
    blog_img = FileField("Upload Blog Picture", validators=[FileAllowed(["jpg", "png","jpeg","gif"]),DataRequired()])
    blog_submit_btn = SubmitField("Submit")

    def validate(self):
        initial_validation = super(BlogForm, self).validate()
        if not initial_validation:
            return False
        blog = Blog.query.filter_by(blog_title=self.blog_title.data).first()
        if blog is not None:
            self.blog_title.errors.append('Blog title already exists')
            return False
        return True

class EditBlogForm(FlaskForm):
    choices = [('Travel','Travel'),('Food','Food'),('Health','Health'),('Fashion','Fashion'),
						('Personal','Personal'),('Movies','Movies'),('Sports','Sports')]
    blog_title = StringField("Blog Title", validators=[DataRequired()])
    blog_category = SelectField(label='Category', choices=choices , validators=[DataRequired()])
    blog_text = StringField(u'Text', widget=TextArea())
    blog_img = FileField("Upload Blog Picture", validators=[FileAllowed(["jpg", "png","jpeg","gif"])])
    blog_submit_btn = SubmitField("Submit")

    # def validate(self):
    #     initial_validation = super(EditBlogForm, self).validate()
    #     if not initial_validation:
    #         return False
    #     blog = Blog.query.filter_by(blog_title=self.blog_title.data).first()
    #     if blog is not None:
    #         self.blog_title.errors.append('Blog title already exists')
    #         return False
    #     return True

class AddComment(FlaskForm):
    comment_text = StringField(u'Text', widget=TextArea(),validators=[DataRequired()])
    comment_submit_btn = SubmitField("Leave Comment")

class FilterBlog(FlaskForm):
    choices = [('Clear','Clear'),('Travel','Travel'),('Food','Food'),('Health','Health'),('Fashion','Fashion'),
						('Personal','Personal'),('Movies','Movies'),('Sports','Sports')]
    blog_category = SelectField(label='Category', choices=choices , validators=[DataRequired()])
    search_btn = SubmitField("Filter")