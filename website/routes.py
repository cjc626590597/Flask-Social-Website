from flask import render_template, url_for, request, redirect, flash, session
from werkzeug.security import generate_password_hash
from website.models import user_tbl, media_tbl, friend_tbl, comment_tbl, visibility_tbl, message_tbl
from website.forms import RegistrationForm, LoginForm, SearchForm, RecordUpdateForm
from flask_login import login_user, logout_user, login_required, current_user
from website import app, db,socketio
from flask_socketio import emit
from sqlalchemy import or_, and_
from website.functions import show_pic_data, upload_visibility, get_sort_friendlist, get_posts, get_friend_requests, \
    get_searched_users

@app.route('/')
def start():
    return render_template('start.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            validation_process = form.run_validation(form.username, form.email, form.password, form.confirm_password,
                                                     form.age)
            if validation_process == "No error":
                account = user_tbl(username=form.username.data,
                                   password=generate_password_hash(form.password.data, method='pbkdf2:sha256',
                                                                   salt_length=8), email=form.email.data,
                                   age=form.age.data, location=form.location.data, isAdmin=0)
                db.session.add(account)
                db.session.commit()
                login_user(account)
                session['username'] = account.username
                session['user_id'] = account.user_id
                session['password'] = account.password
                return redirect(url_for('login'))
            else:
                flash(validation_process)
        else:
            flash("Invalid Email Address!")
    return render_template('register.html', title='Register', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = user_tbl.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            session['username'] = user.username
            session['user_id'] = user.user_id
            session['password'] = user.password
            return redirect(url_for('home'))
        else:
            flash('Invalid Username or Password!')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('start'))


@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    username = session.get('username')
    owner_id = session['user_id']
    # Sorted friend id list, Sorted user_blocked list, friend records (id+username)
    friends_id_List_sort, friend_is_blocked_sort, friends = get_sort_friendlist()
    posts = get_posts(owner_id)
    pic_data, posts = show_pic_data(posts)
    # ID=request.form.get('comment_media')
    comms = comment_tbl
    users = user_tbl

    if request.method == 'POST':
        if 'submit_button' not in request.form:
            data = request.json
            print('block work')
            friend_is_blocked_sort = data
            session['blocked'] = friend_is_blocked_sort
        if 'submit_button' in request.form:
            count = 0
            images = [0, 0, 0, 0]
            desc = request.form['media_desc']
            for nums in range(0, len(request.files)):
                image = request.files['media_image_' + str(count)]
                image = image.read()
                images[nums] = image
                count = count + 1
            db.session.close()
            post = media_tbl(media_desc=desc, media_image_0=images[0], media_image_1=images[1],
                             media_image_2=images[2], media_image_3=images[3], media_user_id=current_user.user_id,
                             media_img_num=len(request.files), place_owner_user_id=owner_id)
            db.session.add(post)
            db.session.commit()
            post_new = media_tbl.query.filter(media_tbl.media_user_id == session['user_id']).order_by(
                media_tbl.media_post_time.desc()).first()
            post_id = post_new.media_id
            try:
                if session['blocked'] is not None:
                    friend_is_blocked_sort = session['blocked']
                    session['blocked'] = None
            except:
                print('no session')
            upload_visibility(friends_id_List_sort, friend_is_blocked_sort, post_id)
            return redirect(url_for('home'))
        if 'submit_comment' in request.form:
            comment = request.form['comment_desc']
            media_id = request.form['post_comment']
            db.session.close()
            comment_new = comment_tbl(comment_description=comment, post_id=media_id, user_id=current_user.user_id)
            db.session.add(comment_new)
            db.session.commit()
            return redirect(url_for('home'))

    return render_template('home.html', title="Other_Home", friends=friends, friend_select=friend_is_blocked_sort,
                           username=username, pic_data=pic_data, posts=posts, user_tbl=user_tbl, comms=comms,
                           users=users)


@app.route('/home/find', methods=['POST', 'GET'])
@login_required
def find():
    form = SearchForm()
    search_users = user_tbl.query.filter(user_tbl.username == '112312312312easdasdwqwewqasdwqeasq')
    is_friend_list = []
    friend_requests, request_users = get_friend_requests()
    if request.method == 'GET':
        return render_template('find.html', title="Find", search_users=search_users, form=form, friend_list=is_friend_list,
                               friend_requests=friend_requests, request_users=request_users)
    if request.method == 'POST':
        if request.form.get('search'):
            if form.validate_on_submit():
                session['search_username'] = form.search_username.data
                search_users, is_friend_list = get_searched_users()
                if search_users.count() == 0:
                    flash('No users found!')
        elif request.form.get('add'):
            is_friend = request.form['is_friend']
            if is_friend == '0':
                flash('You two are already friends or you have sent a friend request')
            elif is_friend == '1':
                add_friend_id = request.form['user_id']
                friend_request = friend_tbl(uid=add_friend_id, fid=session['user_id'], status='waited', user_action='0')
                try:
                    db.session.add(friend_request)
                    db.session.commit()
                    flash("You send a friend request successfully!")
                except:
                    flash("Add friend error!")
        elif 'confirm' in request.form:
            friend_tbl.query.filter(
                and_(friend_tbl.uid == current_user.user_id,
                     friend_tbl.fid == request.form['request_user'])).update(
                {'status': 'accepted'})
            db.session.commit()
            friend_requests, request_users = get_friend_requests()
            search_users, is_friend_list = get_searched_users()
            if search_users.count() == 0:
                flash('No users found!')
        elif 'remove' in request.form:
            request_remove = friend_tbl.query.filter(
                and_(friend_tbl.uid == current_user.user_id,
                     friend_tbl.fid == request.form['request_user'])).first()
            db.session.delete(request_remove)
            db.session.commit()
            friend_requests, request_users = get_friend_requests()
            search_users, is_friend_list = get_searched_users()
            if search_users.count() == 0:
                flash('No users found!')
    return render_template('find.html', title="Find", search_users=search_users, form=form, friend_list=is_friend_list,
                           friend_requests=friend_requests, request_users=request_users)


@app.route('/find_some/<username>', methods=['POST', 'GET'])
@login_required
def findSome(username):
    if request.method == 'GET':
        user = user_tbl.query.filter(user_tbl.username == username).first()
        return render_template('find_someone.html', title="Find_someone", user=user)
    if request.method == 'POST':
        if 'Enter home' in request.form:
            return redirect(url_for('other_home', username=username))
        elif 'Chat' in request.form:
            return redirect(url_for('chat_with', username=username))
        elif 'Delete user' in request.form:
            delete_user = user_tbl.query.filter(user_tbl.username == username).first()
            delete_user_record = friend_tbl.query.filter(
                or_(and_(friend_tbl.uid == current_user.user_id,
                         friend_tbl.fid == delete_user.user_id),
                    and_(friend_tbl.uid == delete_user.user_id,
                         friend_tbl.fid == current_user.user_id))).first()
            db.session.delete(delete_user_record)
            db.session.commit()
            return redirect(url_for("home"))


@app.route('/other_home/<username>', methods=['GET', 'POST'])
@login_required
def other_home(username):
    owner = user_tbl.query.filter(user_tbl.username == username).first()
    owner_id = owner.user_id
    # Sorted friend id list, Sorted user_blocked list, friend records (id+username)
    friends_id_List_sort, friend_is_blocked_sort, friends = get_sort_friendlist()
    posts = get_posts(owner_id)
    pic_data, posts = show_pic_data(posts)
    # ID=request.form.get('comment_media')
    comms = comment_tbl
    users = user_tbl
    if request.method == 'POST':
        if 'submit_button' not in request.form:
            data = request.json
            friend_is_blocked_sort = data
            session['blocked'] = friend_is_blocked_sort
        if 'submit_button' in request.form:
            count = 0
            images = [0, 0, 0, 0]
            desc = request.form['media_desc']
            for nums in range(0, len(request.files)):
                image = request.files['media_image_' + str(count)]
                image = image.read()
                images[nums] = image
                count = count + 1
            db.session.close()
            post = media_tbl(media_desc=desc, media_image_0=images[0], media_image_1=images[1],
                             media_image_2=images[2], media_image_3=images[3], media_user_id=current_user.user_id,
                             media_img_num=len(request.files), place_owner_user_id=owner_id)
            db.session.add(post)
            db.session.commit()
            post_new = media_tbl.query.filter(media_tbl.media_user_id == session['user_id']).order_by(
                media_tbl.media_post_time.desc()).first()
            post_id = post_new.media_id
            try:
                if session['blocked'] is not None:
                    friend_is_blocked_sort = session['blocked']
                    session['blocked'] = None
            except:
                print('no session')
            upload_visibility(friends_id_List_sort, friend_is_blocked_sort, post_id)
            return redirect(url_for('other_home', username=username))

        if 'submit_comment' in request.form:
            comment = request.form['comment_desc']
            media_id = request.form['post_comment']
            db.session.close()
            comment_new = comment_tbl(comment_description=comment, post_id=media_id, user_id=current_user.user_id)
            db.session.add(comment_new)
            db.session.commit()
            return redirect(url_for('other_home', username=username))

    return render_template('other_home.html', title="Other_Home", friends=friends, friend_select=friend_is_blocked_sort,
                           username=username, pic_data=pic_data, posts=posts, user_tbl=user_tbl, comms=comms,
                           users=users)


@app.route('/socketio')
def chat1():
    return render_template('socketio.html')

@socketio.event
def my_broadcast_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)
    print(message['data'])


@app.route('/home/chat')
@login_required
def chat():
    # Sorted friend id list, Sorted user_blocked list, friend records (id+username)
    friends_id_list_sort, friend_is_blocked_sort, friends = get_sort_friendlist()
    return render_template('chat.html', title="chat", friends=friends, friend_select=friend_is_blocked_sort)


# route for chatting with friend
@app.route('/chat_with/<username>', methods=['GET', 'POST'])
@login_required
def chat_with(username):
    users = user_tbl
    recipient_name = users.query.filter(user_tbl.username == username).order_by(user_tbl.user_id).first()
    recipient_id = recipient_name.user_id
    msgs = message_tbl
    all_msgs = msgs.query.filter(
        or_(and_(msgs.sender_id==current_user.user_id,
                 msgs.receive_id==recipient_id),
            and_(msgs.receive_id==current_user.user_id,
                 msgs.sender_id==recipient_id)))

    friends_id_list_sort, friend_is_blocked_sort, friends = get_sort_friendlist()

    if request.method == 'POST':
        message = request.form['message_desc']
        db.session.close()
        message_new = message_tbl(body=message, receive_id=recipient_id, sender_id=current_user.user_id)
        db.session.add(message_new)
        db.session.commit()
        return render_template('chat_with.html', username=username, recipient_id=recipient_id, title="chat", friends=friends, friend_select=friend_is_blocked_sort, msgs=msgs, users=users, all_msgs=all_msgs)
    return render_template('chat_with.html', title="chat", friends=friends, friend_select=friend_is_blocked_sort,
                           username=username, msgs=msgs, users=users, all_msgs=all_msgs)

# route for deleting a post
@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    # need to set the current user value into a variable
    user_id = current_user.user_id
    # query through the database in order to make sure that the id matches the media_id inside the database
    post_id = media_tbl.query.filter_by(media_id=id).first()

    vis_post_id = visibility_tbl.query.filter_by(post_id=id)

    comment_post_id = comment_tbl.query.filter_by(post_id=id)

    # Finding which user owns the post
    post_owner = post_id.media_user_id
    # finding the id for the page owner
    page_owner = post_id.place_owner_user_id

    # if statement to delete a post. Current user id need to match post owner id or the page owner id
    if user_id == post_owner or user_id == page_owner:
        #for statement iterates through the query to find the comments and delete them
        for x in comment_post_id:
            #sets the id which needs to be deleted
            id_for_deleting_comment = x.comment_id
            #gets the record from that database
            comment_object = comment_tbl.query.get_or_404(id_for_deleting_comment)
            #deleting the record from the database
            db.session.delete(comment_object)
            #commits to the database
            db.session.commit()
        # for statement iterates through the query to find the post id information and delete them from the database
        for i in vis_post_id:
            # sets the id which needs to be deleted
            vis_id_for_deleting = i.vis_id
            # gets the record from that database
            vis_oject = visibility_tbl.query.get_or_404(vis_id_for_deleting)
            # deleting the record from the database
            db.session.delete(vis_oject)
            # commits to the database
            db.session.commit()
        # getting the post from the data via id which we are given as a parameter
        deleted_post = media_tbl.query.get_or_404(id)
        # deleting the post from the database
        db.session.delete(deleted_post)

        # committing the delete to the database
        db.session.commit()
    else:
        # if the current user id does not match the post owner id they cannot delete a post
        print('You cannot delete posts that arent yours')

    # redirect the user back to the homepage.
    return redirect(request.referrer)


@app.route('/home/setting', methods=['GET', 'POST'])
@login_required
def setting():
    form = RecordUpdateForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.password_length_settings(form.password):
                if form.checkfor_username(form.username_up):
                    user_id = session['user_id']
                    db.session.query(user_tbl).filter_by(user_id=user_id).update({user_tbl.username: form.username_up.data,
                                                                                  user_tbl.password: generate_password_hash(
                                                                                      form.password.data,
                                                                                      method='pbkdf2:sha256',
                                                                                      salt_length=8), user_tbl.isAdmin: 0,
                                                                                  user_tbl.email: form.email.data,
                                                                                  user_tbl.age: form.age.data,
                                                                                  user_tbl.location: form.location.data})
                    db.session.commit()

                    return redirect(url_for('setting'))

                else:
                    flash('Username already taken!')
            else:
                flash('Password Length must be atleast 8 characters')
        else:
            flash('Passwords must match!')
    return render_template('setting.html', form=form)
