from flask import Flask, request ,session,flash,jsonify
from flask import render_template,redirect, url_for
from flask import current_app as app
from application.models import *
from sqlalchemy import exc,select,or_
from werkzeug.utils import secure_filename
from application.input_html import *
from application.blog_html import *
from flask_security import login_required,logout_user
from application.config import *
from flask_login import *
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from sqlalchemy.exc import IntegrityError

login_manager = LoginManager()
login_manager.login_view = 'index'
login_manager.init_app(app)

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500

@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))


@app.context_processor
def common():
    filter_form=FilterBlog()
    return dict(filter_form=filter_form)

def photo_handler(img_name,folder):
    img_extensions =  ["JPG","JPEG","PNG","GIF"]
    upl_img_ext= img_name.split('.')[1]
    if(upl_img_ext.upper() in img_extensions):
        dest_path='static/'+folder+'/'+img_name
    return dest_path

@app.route("/signup", methods=["GET","POST"])
def signup():
    form=SignUpForm()
    if form.validate_on_submit():
        passwd=generate_password_hash(form.password.data)
        img=form.profile_img.data
        if img is None:
            dest_path=f'../static/uploads/default.png'
        else:
            dest_path=photo_handler(img.filename,'uploads')
            img.save(dest_path)
            dest_path=f'../static/uploads/{img.filename}'    
        insert_user=User(username=form.username.data,first_name=form.fname.data,last_name=form.lname.data,email=form.email.data,password=passwd,
                        photo=dest_path,profile_description=form.profile_description.data)
        try:
            db.session.add(insert_user)
            db.session.commit()
            flash('You have created your account successfully!!!!!')
        except exc.IntegrityError:
            return "Error"
        return redirect(url_for('index'))
    return render_template('signup.html',form=form)



@app.route("/", methods=["GET","POST"])
def index():
    form=LoginForm()
    if form.validate_on_submit():
        if '@' in form.login_id.data: # fetching username if email was passed in login
            u_name=select(User.username).where(User.email==form.login_id.data)
            user_= db.session.execute(u_name).first()
            username=user_[0]
        else:
            username=form.login_id.data
        session['username']=username
        uid=User.query.filter_by(username=username).first()
        login_user(uid)
        flash("you are successfuly logged in") 
        return redirect(url_for('news_feed',username=username))
    else:
        error="Either username or password is incorrect"
        return render_template('login.html',form=form)
    
@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index')) 

@app.route("/reset_password", methods=["GET","POST"])
def reset_password():
    form=ForgotPassword()
    if form.validate_on_submit():
        print(form.validate_on_submit())
        return redirect(url_for('new_password',username=form.username.data))
    return render_template('forget_password.html',form=form)

@app.route("/new_password/<username>", methods=["GET","POST"])
def new_password(username):
    form1=ResetPassword()

    if form1.validate_on_submit():
        print(form1.password.data)
        uid=User.query.filter_by(username=username).first()
        uid.password= generate_password_hash(form1.password.data)
        db.session.add(uid)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('password.html',form1=form1)

@app.route("/edit_user/<username>", methods=["GET","POST"])
@login_required
def edit_user(username):
    form= EditUserForm()
    if form.validate_on_submit() and session['username']==current_user.username:
        print('In post')
        current_user.first_name=form.fname.data
        current_user.last_name=form.lname.data
        current_user.email=form.email.data
        if form.password.data != '':
            current_user.password= form.password.data
        current_user.profile_description=form.profile_description.data
        if form.profile_img.data is not None:
            img=form.profile_img.data
            dest_path=photo_handler(img.filename,'uploads')
            img.save(dest_path)
            dest_path=f'../static/uploads/{img.filename}'
            current_user.photo=dest_path
        try:
            db.session.add(current_user)
            db.session.commit()
        except IntegrityError:
            flash('Invalid updation')
        flash('Your profile has been updated.')
        return redirect(url_for('my_profile', username=session['username']))
    form.fname.data=current_user.first_name
    form.lname.data=current_user.last_name
    form.email.data=current_user.email
    form.profile_description.data=current_user.profile_description
    return render_template('edit_user.html',form=form,username=username)

@app.route("/delete_user/<username>", methods=["GET","POST"])
@login_required
def delete_user(username):
    if request.method=="GET" and session['username']==username:
        user = User.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()
        session.pop('username',None)
        return redirect(url_for('logout'))

@app.route("/feeds/<username>", methods=["GET","POST"])
@login_required
def news_feed(username):
    if request.method=="GET" and session['username']==username:
        form=AddComment()
        blogs= current_user.followed_posts().all()
        comment = Comment.query.all()
        return render_template('feed.html',blogs=blogs,now=datetime.datetime.now(),form=form,comments=comment)
    else:
        return redirect(url_for('index'))

@app.route("/my_profile/<username>", methods=["GET","POST"])
#@login_required
def my_profile(username):
    if request.method=="GET":
        form=AddComment()
        user = User.query.filter_by(username=username).first()
        blogs= Blog.query.filter_by(author_id=user.id).order_by(Blog.blog_post_time.desc()).all()
        comment = Comment.query.all()
        return render_template('my_blog.html',user=user,blogs=blogs,now=datetime.datetime.now(),comments=comment,form=form)

@app.route("/filter_feeds/<username>", methods=["GET","POST"])
@login_required
def filter_feed(username):
    if request.method=="POST" and session['username']==username:
        filter_form=FilterBlog()
        form=AddComment()
        cat=filter_form.blog_category.data
        if cat == 'Clear':
            blogs= current_user.followed_posts().all()
        else:
            blogs= current_user.followed_posts()
            blogs= blogs.filter(Blog.blog_category==cat).all()
        comment = Comment.query.all()
        return render_template('feed.html',blogs=blogs,now=datetime.datetime.now(),form=form,comments=comment)

@app.route("/add_blog/<id>",methods=["GET","POST"])
@login_required
def add_blog(id):
    form=BlogForm()
    user = User.query.filter_by(id=id).first()
    
    if form.validate_on_submit() and session['username']==current_user.username:
        blog_img=form.blog_img.data
        if blog_img is None:
            dest_path=None
        else:
            dest_path=photo_handler(blog_img.filename,'blog')
            blog_img.save(dest_path)
            dest_path=f'../static/blog/{blog_img.filename}'
        u=User.query.filter_by(id=id).first()    
        insert_blog=Blog(author_id=id,blog_post_time=datetime.datetime.now(),blog_title=form.blog_title.data,
        blog_category=form.blog_category.data,blog_text=form.blog_text.data,blog_img=dest_path,users=u)
        try:
            db.session.add(insert_blog)
            db.session.commit()
        except exc.IntegrityError:
            error='Error occured'
            return redirect(url_for('my_profile',username=session['username']))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('my_profile',username=session['username']))
    return render_template('add_blog.html',form=form,id=id,user=user)

@app.route("/edit_blog/<int:blog_id>",methods=["GET","POST"])
@login_required
def edit_blog(blog_id):
    form=EditBlogForm()
    blog = Blog.query.filter_by(blog_id=blog_id).first()
    if request.method=='GET':
        form.blog_title.data = blog.blog_title
        form.blog_category.data = blog.blog_category
        form.blog_text.data = blog.blog_text 
    elif request.method=='POST' and session['username']==current_user.username:
        blog_img=form.blog_img.data
        if blog_img is None:
            dest_path=None
        else:
            dest_path=photo_handler(blog_img.filename,'blog')
            blog_img.save(dest_path)
            dest_path=f'../static/blog/{blog_img.filename}'
            blog.blog_img=dest_path
        blog.blog_title = form.blog_title.data
        blog.blog_category = form.blog_category.data
        blog.blog_text = form.blog_text.data     
        try:
            db.session.add(blog)
            db.session.commit()
        except exc.IntegrityError:
            err = "Error"
        return redirect(url_for('my_profile',username=session['username']))
    return render_template('edit_post.html',form=form,blog=blog,user=current_user)
    
@app.route("/delete_blog/<int:blog_id>", methods=["GET","POST"])
@login_required
def delete_blog(blog_id):
    if request.method=="GET" and session['username']==current_user.username:
        blog = Blog.query.filter_by(blog_id=blog_id).first()
        try:
            db.session.delete(blog)
            db.session.commit()
        except: 
            db.session.rollback()
    return redirect(url_for('my_profile',username=current_user.username))

@app.route("/like_blog/<int:blog_id>", methods=['POST'])
@login_required
def like(blog_id):
    
    blog = Blog.query.filter_by(blog_id=blog_id).first()
    like = Like.query.filter_by(id=current_user.id, blog_id=blog_id).first()
    if not blog:
        return jsonify({'error': 'Blog does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(id=current_user.id, blog_id=blog_id,blogs=blog)
        db.session.add(like)
        db.session.commit()

    return jsonify({"liked": len(blog.liked), "liked_user": current_user.id in map(lambda x: x.id, blog.liked)})

@app.route("/add_comment/<int:blog_id>", methods=["GET","POST"])
@login_required
def add_comment(blog_id):
    form= AddComment()
    if form.validate_on_submit() and session['username']==current_user.username:
        blog= Blog.query.filter_by(blog_id=blog_id).first()
        comment=Comment(id=current_user.id,blog_id=blog_id,comment_text=form.comment_text.data,comment_time=datetime.datetime.now(),blogs=blog)
        try:
            db.session.add(comment)
            db.session.commit()
        except:
            flash('Comment not added')
        if blog.author_id == current_user.id:
            return redirect(url_for('my_profile',username=current_user.username))
    return redirect(url_for('news_feed',username=current_user.username))


@app.route("/delete_comment/<int:comment_id>", methods=["GET","POST"])
@login_required
def delete_comment(comment_id):
    comment= Comment.query.filter_by(comment_id=comment_id).first()
    blog= Blog.query.filter_by(blog_id=comment.blog_id).first()
    try:
        db.session.delete(comment)
        db.session.commit()
    except:
        db.session.rollback()
        flash('error')
    if blog.author_id == current_user.id:
        return redirect(url_for('my_profile',username=current_user.username))
    return redirect(url_for('news_feed',username=current_user.username))

@app.route("/user_search/<username>", methods=["POST"])
@login_required
def user_search(username):
    if request.method=="POST" and session['username']==current_user.username:
        search_nm="%{}%".format(request.form['search_name'])
        results= User.query.filter(or_(User.username.like(search_nm),User.first_name.like(search_nm),User.last_name.like(search_nm))).all()
        return render_template('search_results.html',user=current_user,results=results)
    return redirect(url_for('news_feed',username=current_user.username))

@app.route("/connection_list/<username>", methods=["GET","POST"])
@login_required
def connection_list(username):
    if request.method=="GET" and session['username']==username:
        f=current_user.followers.filter_by(followed_id=current_user.id).all()
        f1=current_user.followed.filter_by(follower_id=current_user.id).all()
        return render_template('connection.html',user=current_user,fow=f,fow1=f1)


@app.route('/following/<string:username>', methods=['GET', 'POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()

    if current_user.followed.filter_by(followed_id=user.id).first() is None:
        f = Follow(follower=current_user, followed=user, follow_time=datetime.datetime.now())
        db.session.add(f)
        db.session.commit()
    return redirect(url_for('news_feed',username=current_user.username))   


@app.route('/followers/<string:username>', methods=['GET', 'POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    f = current_user.followed.filter_by(followed_id=user.id).first()
    if f:
        db.session.delete(f)
        db.session.commit()
    return redirect(url_for('news_feed',username=current_user.username))