import base64

from flask import session
from website.models import user_tbl, media_tbl, friend_tbl, visibility_tbl, comment_tbl
from flask_login import current_user
from website import db
from sqlalchemy import or_, and_


def show_pic_data(posts):
    # Changed the code here in order to get posts showing up chronologically.
    # Having posts showing in media_id descending order ensures the newset post is always shown
    posts = media_tbl.query.filter(media_tbl.media_id.in_(posts)).order_by(media_tbl.media_id.desc())
    counts = posts.count()
    pic_data = []
    for i in range(counts):
        pic_data.append([])
        for j in range(4):
            pic_data[i].append(0)
    for i in range(0, counts):
        posts[i].media_image_0 = base64.b64encode(posts[i].media_image_0).decode()
        posts[i].media_image_1 = base64.b64encode(posts[i].media_image_1).decode()
        posts[i].media_image_2 = base64.b64encode(posts[i].media_image_2).decode()
        posts[i].media_image_3 = base64.b64encode(posts[i].media_image_3).decode()
        pic_data[i][0] = posts[i].media_image_0
        pic_data[i][1] = posts[i].media_image_1
        pic_data[i][2] = posts[i].media_image_2
        pic_data[i][3] = posts[i].media_image_3

    return pic_data, posts


def upload_visibility(friend_list_sort, data, post_id):
    friend_block = []
    print(friend_list_sort)
    print(data)
    print('block works')
    for i in range(0, len(data)):
        if data[i] == 1:
            friend_block.append(friend_list_sort[i])
            post = visibility_tbl(post_id=post_id, block_id=friend_list_sort[i])
            print(i)
            db.session.add(post)
            db.session.commit()
    return friend_block


def get_sort_friendlist():
    friendsList = []
    friend_is_blocked = []
    friends_id_List_sort = []
    friend_is_blocked_sort = []
    friends_records = friend_tbl.query.filter(
        or_(friend_tbl.uid == current_user.user_id, friend_tbl.fid == current_user.user_id))
    friendNum = friends_records.count()
    for num in range(0, friendNum):
        if friends_records[num].fid == current_user.user_id and friends_records[num].status != 'waited':
            friendsList.append(friends_records[num].uid)
            if ((friends_records[num].user_action == 0 and friends_records[num].status == 'blocked') or (
                    friends_records[num].user_action == 2 and friends_records[num].status == 'blocked')):
                friend_is_blocked.append(1)
            else:
                friend_is_blocked.append(0)
        if friends_records[num].uid == current_user.user_id and friends_records[num].status != 'waited':
            friendsList.append(friends_records[num].fid)
            if ((friends_records[num].user_action == 1 and friends_records[num].status == 'blocked') or (
                    friends_records[num].user_action == 2 and friends_records[num].status == 'blocked')):
                friend_is_blocked.append(1)
            else:
                friend_is_blocked.append(0)
    # Get the sorted username and user_id
    friends = user_tbl.query.filter(user_tbl.user_id.in_(friendsList)).with_entities(user_tbl.user_id,
                                                                                        user_tbl.username).order_by(
        user_tbl.username.asc())
    friendNum= len(friendsList)
    for num in range(0, friendNum):
        for index in range(0, friendNum):
            if friendsList[index] == friends[num].user_id:
                friend_is_blocked_sort.append(friend_is_blocked[index])
                break
        friends_id_List_sort.append(friends[num].user_id)
    return friends_id_List_sort, friend_is_blocked_sort, friends


def is_friend(owner_id):
    is_friend = friend_tbl.query.filter(or_(and_(friend_tbl.uid == session['user_id'], friend_tbl.fid == owner_id),
                                            and_(friend_tbl.fid == session['user_id'], friend_tbl.uid == owner_id)))
    if (is_friend.count() == 0):
        if (owner_id == session['user_id']):
            return True
        else:
            return False
    else:
        return True


def get_posts(owner_id):
    # Having posts showing in media_id descending order ensures the newset post is always shown
    posts_all = media_tbl.query.filter(media_tbl.place_owner_user_id == owner_id).order_by(media_tbl.media_id.desc())
    post_can_see = []
    post_num = posts_all.count()

    if not is_friend(owner_id):
        for i in range(0, post_num):
            post_id = posts_all[i].media_id
            if get_blocked_users(post_id):
                if len(post_can_see) < 3:
                    post_can_see.append(post_id)
                else:
                    break
    else:
        for i in range(0, post_num):
            post_id = posts_all[i].media_id
            if get_blocked_users(post_id):
                post_can_see.append(post_id)
    return post_can_see


def get_comments(post_id):
    comments_all = comment_tbl.query.filter(comment_tbl.post_id == post_id)
    return comments_all


def get_blocked_users(post_id):
    blockedUsers = visibility_tbl.query.filter(visibility_tbl.post_id == post_id)
    for i in range(0, blockedUsers.count()):
        if blockedUsers[i].block_id == session['user_id']:
            return False
    return True


def get_searched_users():
    is_friend_list = []
    search_users = user_tbl.query.filter(user_tbl.username == 'abcdefg')
    if session.get('search_username') is not None:
        search_users = user_tbl.query.filter(
            and_(user_tbl.username.contains(session['search_username']), user_tbl.username != session['username']))
        if search_users.count() > 0:
            num = search_users.count()
            for i in range(0, num):
                user_in = friend_tbl.query.filter(or_(
                    and_(friend_tbl.uid == search_users[i].user_id, friend_tbl.fid == session['user_id']),
                    and_(friend_tbl.uid == session['user_id'], friend_tbl.fid == search_users[i].user_id)))
                if user_in.count() != 0:
                    is_friend_list.append(0)
                else:
                    is_friend_list.append(1)
    return search_users, is_friend_list


def get_friend_requests():
    friend_requests = friend_tbl.query.filter(
        and_(friend_tbl.uid == current_user.user_id, friend_tbl.status == 'waited'))
    request_users = []
    for friend_request in friend_requests:
        request_user = user_tbl.query.filter(user_tbl.user_id == friend_request.fid).first()
        request_users.append(request_user)
    return friend_requests, request_users
