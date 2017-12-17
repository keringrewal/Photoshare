######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Baichuan Zhou (baichuan@bu.edu) and Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
import time

# for image uploading
# from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'kgnm'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'werdo3000'
app.config['MYSQL_DATABASE_DB'] = 'PHOTOSHARESOLUTION'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config['DEBUG'] = True
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM User")
users = cursor.fetchall()


# returns a list of all of the users
def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM User")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    query = "SELECT password FROM User WHERE email = email"
    cursor.execute(query)
    data = cursor.fetchall()
    pwd = str(data[0][0])
    return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@app.route('/login', methods=['GET', 'POST'])
# login page for existing users
def login():
    if flask.request.method == 'GET':
        return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM User WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')


@app.route("/register", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        # ADD FIRST and LAST NAME
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        dob = request.form.get('dob')
        # ADD hometown
        hometown = request.form.get('hometown')
        # ADD gender
        gender = request.form.get('gender')
    except:
        print("couldn't find all tokens")
        # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO User (email, password, fname, lname, hometown, gender, dob)"
                             "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password, fname,
                                                                                               lname, hometown, gender,
                                                                                               dob)))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('hello.html', name=fname, message='Account Created')
    else:
        print("couldn't find all tokens")
        return render_template('register.html', message="Please fill out all the fields")



# end login code

@app.route('/profile')
@flask_login.login_required
def protected():
    uid = flask_login.current_user.id
    name = getName(uid)
    return render_template('profile.html', name=name, message="Here's your profile")


def getName(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT fname FROM User WHERE email = '{0}'".format(uid))
    return cursor.fetchall()


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/createalbum', methods=['GET', 'POST'])
@flask_login.login_required
def createAlbum():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        name = request.form.get('name')
        if uniqueAlbumName(name, uid) == True:
            cursor = conn.cursor()
            date = time.strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO Album (name, uid, doc) VALUES('{0}', '{1}', '{2}')".format(name, uid, date))
            conn.commit()
            return render_template('profile.html', name=getfname(uid), message='Album Created')
        else:
            return render_template('createalbum.html', message='That name is in use, please choose a new name')

    else:
        return render_template('createalbum.html')


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def uploadPhoto():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':
        imgfile = request.files['photo']
        aname = request.form.get('aname')
        aid = getAlbumId(aname)
        print(aid)

        caption = request.form.get('caption')
        tags = (request.form.get('tags'))

        tags = tags.split(" ")

        data = base64.standard_b64encode(imgfile.read())

        if uniqueAlbumName(aname, uid) == False:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Photo (data, caption, aid, uid) VALUES ('{0}', '{1}', '{2}', '{3}')".format(data, caption, aid, uid))
            conn.commit()
            pid = cursor.lastrowid

            for tag in tags:
                if tagNotCreated(tag):
                    cursor.execute("INSERT INTO Tag(hashtag, pid) VALUES ('{0}', '{1}')".format(tag, pid))
            conn.commit()

            return render_template('hello.html', photos=getUserPhotos(uid), message='Photo uploaded')
        else:
            return render_template('upload.html', message="The album does not exist.")
    else:
        return render_template('upload.html')
        # The method is GET so we return a  HTML form to upload the a photo.


def tagNotCreated(tag):
    if cursor.execute("SELECT Hashtag FROM Tag WHERE hashtag = '{0}'".format(tag)):
        return False
    else:
        return True


@app.route('/photos', methods=['GET', 'POST'])
@flask_login.login_required
def myPhotos():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    photos = []
    if request.method == 'GET':
        for photo in getMyPhotos(uid):  # P.data, P.pid, P.caption, A.name
            photos += [getPhotoActivity(photo)]

        return render_template('photos.html', photos=photos)
    else:
        return render_template('photos.html')


@app.route('/likePhoto', methods=['GET', 'POST'])
@flask_login.login_required
def likePhoto():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    photos = []
    if request.method == 'POST':
        pid = request.form.get("pid")
        doc = time.strftime("%Y-%m-%d")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO liketable(uid, pid, doc) VALUES ('{0}', '{1}', '{2}')".format(uid, pid, doc))
        conn.commit()

        for photo in getAllPhotos():
            photos += [getPhotoActivity(photo)]

        return render_template("allpix.html", photos=photos, message="Photo liked")
    else:
        for photo in getAllPhotos():
            photos += [getPhotoActivity(photo)]
        return render_template("allpix.html", photos=photos)


@app.route('/commentPhoto', methods=['GET', 'POST'])
@flask_login.login_required
def commentPhoto():
    uid = getUserIdFromEmail(flask_login.current_user.id)

    if request.method == 'POST':
        content = request.form.get('comment')
        pid = request.form.get("pid")
        doc = time.strftime("%Y-%m-%d")

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO comment(content, uid, pid, doc) VALUES ('{0}', '{1}', '{2}', '{3}')".format(content, uid, pid,
                                                                                                     doc))
        conn.commit()
        cid = cursor.lastrowid
        cursor.execute("INSERT INTO associate(pid, cid) VALUES ('{0}', '{1}')".format(pid, cid))
        conn.commit()

        photos = []
        for photo in getAllPhotos():
            photos += [getPhotoActivity(photo)]

        return render_template("allpix.html", photos=photos, message="Comment added")
    else:
        photos = []
        for photo in getAllPhotos():
            photos += [getPhotoActivity(photo)]
        return render_template("allpix.html", photos=photos)


@app.route('/deletePhoto', methods=['POST'])
@flask_login.login_required
def deleteAPhoto():
    uid = getUserIdFromEmail(flask_login.current_user.id)

    if request.method == 'POST':

        if request.form.get("uid") == str(uid):
            pid = request.form.get("pid")
            deletePhoto(pid)

            photos = []
            for photo in getMyPhotos(uid):
                photos += [getPhotoActivity(photo)]
            return render_template("photos.html", photos=photos, message="Photo deleted")
        else:
            photos = []
            for photo in getMyPhotos(uid):
                photos += [getPhotoActivity(photo)]
            return render_template("photos.html", photos=photos, message="Not your photo")
    else:
        photos = []
        for photo in getMyPhotos(uid):
            photos += [getPhotoActivity(photo)]
        return render_template("photos.html", photos=photos)

@app.route('/allpix', methods=['GET', 'POST'])
def allPhotos():
    photos = []
    if request.method == 'GET':
        for photo in getAllPhotos():
            photos += [getPhotoActivity(photo)]
        for i in photos:
            print(photos[1][4])
        return render_template('allpix.html', photos=photos)
    else:
        return render_template('allpix.html')


def getPhotoActivity(photo):
    return [photo] + [getLikes(photo[1])] + [getLikers(photo[1])] + [getComments(photo[1])] + [getTags(photo[1])]

@app.route('/friends', methods=['GET', 'POST'])
@flask_login.login_required
def friends():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    friends = getFriends(uid)
    fnames = []

    friends += getOtherFriends(uid)
    for friend in friends:
        fnames += [getfname(friend[0])]

    if request.method == 'GET':
        print(fnames)
        return render_template('friends.html', friendslist=fnames)

    elif request.method == 'POST':
        email = request.form.get('searchemail')
        friendid = getUserIdFromEmail(email)
        if notFriendsYet(uid, friendid):
            # cursor.execute("SELECT uid FROM User WHERE uid = '{0}'".format(friendid))
            cursor.execute("INSERT INTO Friendship(uid1, uid2) VALUES('{0}','{1}')".format(uid, friendid))
            conn.commit()

            fnames += [getfname(friendid)]

            return render_template('friends.html', friendslist=fnames, message="Added")
        else:
            return render_template('friends.html', friendslist=fnames, message="You are already friends")
    else:
        return render_template('friends.html')


@app.route('/albums', methods=['GET'])

def showAlbums():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'GET':
        albums = getAlbums(uid)
        return render_template("album.html", albums=albums)
    else:
        return render_template("album.html")


@app.route('/deletealbum', methods=['POST'])
@flask_login.login_required
def deleteAlbum():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':

        aname = request.form.get('name')

        aid = getaidFromAlbum(aname, uid)

        photos = getPhotosFromAlbum(uid, aid)
        print(photos)

        for photo in photos:
            deletePhoto(photo)

        cursor = conn.cursor()
        cursor.execute("DELETE FROM Album WHERE aid = '{0}'".format(aid))
        conn.commit()

        albums = getAlbums(uid)
        print(albums)
        return render_template('album.html', albums=albums, message="Album deleted")
    else:
        albums = getAlbums(uid)
        print(albums)
        return render_template('album.html', albums=albums)

@app.route('/tags', methods=['GET', 'POST'])
def searchTags():
    tags = []
    if request.method == 'POST':
        hashtag = request.form.get('tag')
        for photo in getPhotosWTag(hashtag):
            tags += [getPhotoActivity(photo)]

        return render_template('searchTags.html', photos=tags, message="Here are the photos with that tag!")
    else:
        toptags = findTopTags()
        return render_template('searchTags.html', toptags=toptags, message="Here the top tags!")





'''BEGIN SQL QUERIES'''

def findTopUsers():
    cursor = conn.cursor()
    comments = "SELECT uid, count(cid) AS count FROM Comment GROUP BY uid"
    photos = "SELECT uid, count(pid) AS count FROM Photo GROUP BY uid"
    total = "SELECT U.fname, U.lname FROM User U, (SELECT uid, SUM(count) as count FROM (" + photos + " UNION " + comments + " ) AS sum GROUP BY uid) AS userAct WHERE U.uid = userAct.uid ORDER BY usrAct.count DESC LIMIT 10"
    cursor.execute(total)
    print(total)
    return cursor.fetchall()


def getPhotosWTag(tag):
    cursor = conn.cursor()
    query = "SELECT P.data, P.pid, P.caption, A.name FROM Photo P, Album A, Tag T WHERE T.pid = P.pid AND P.aid = A.aid AND T.hashtag = '{0}'".format(tag)
    cursor.execute(query)
    return cursor.fetchall()


def getPhotoTagged(tag):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT P.data, P.pid, P.caption, A.name FROM Photo P, Album A, Tag T WHERE T.pid = P.pid AND P.aid = A.aid AND T.hashtag = '{0}'").format(
        tag)


def findTopTags():
    cursor = conn.cursor()
    total = "SELECT T.hashtag, COUNT(T.hashtag) FROM Tag T GROUP BY hashtag ORDER BY COUNT(hashtag) DESC LIMIT 10"
    cursor.execute(total)
    print(total)
    return cursor.fetchall()


def getUserPhotos(uid):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT P.data, P.caption, A.name FROM Photo P INNER JOIN Album A ON P.aid=A.aid WHERE P.uid = '{0}'".format(
            uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT uid  FROM User WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def getEmailFromUserID(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM User WHERE uid = '{0}'".format(uid))
    return cursor.fetchone()[0]


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM User WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True


def uniqueAlbumName(name, uid):
    cursor = conn.cursor()
    if cursor.execute(
            "SELECT A.name, U.uid FROM Album A, User U WHERE A.name = '{0}' AND U.uid = '{1}'".format(name, uid)):
        return False
    else:
        return True


def getAlbums(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Album WHERE uid='{0}'".format(uid))
    return cursor.fetchall()


def getAlbumName(aid):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Album WHERE aid = '{0}'".format(aid))
    return cursor.commit()


def getAlbumId(aname):
    cursor = conn.cursor()
    print("SELECT aid FROM Album WHERE name = '{0}'".format(aname))
    cursor.execute("SELECT aid FROM Album WHERE name = '{0}'".format(aname))
    return cursor.fetchone()[0]


def getMyPhotos(uid):
    cursor = conn.cursor()
    # print("SELECT P.data, P.pid, P.caption, A.name FROM Photo P, Album A WHERE P.aid = A.aid AND P.uid = '{0}'".format(uid)))
    cursor.execute(
        "SELECT P.data, P.pid, P.caption, A.name, P.uid FROM Photo P, Album A WHERE P.aid = A.aid AND P.uid = '{0}'".format(
            uid))
    return cursor.fetchall()

def getAllPhotos():
    cursor = conn.cursor()
    cursor.execute("SELECT P.data, P.pid, P.caption, A.name FROM Photo P, Album A WHERE P.aid = A.aid")
    return cursor.fetchall()


def getLikes(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(pid) FROM liketable WHERE pid = '{0}'".format(pid))
    return cursor.fetchall()


def getComments(pid):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT C.content, U.fname, U.lname from Associate A, Comment C, User U WHERE C.uid = U.uid AND A.pid = C.pid AND A.pid = '{0}'".format(
            pid))
    return cursor.fetchall()


def getTags(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT hashtag FROM Tag WHERE pid = '{0}'".format(pid))
    return cursor.fetchall()


def getLikers(pid):
    cursors = conn.cursor()
    cursor.execute("SELECT U.fname, U.lname FROM Liketable L, User U WHERE U.uid = L.uid AND L.pid = '{0}'".format(pid))
    return cursor.fetchall()


def getaidFromAlbum(name, uid):
    cursor = conn.cursor()
    query = "SELECT A.aid FROM Album A WHERE A.name = '{0}' AND A.uid ='{1}'".format(name, uid)
    print(query)
    cursor.execute(query)
    return cursor.fetchall()[0][0]


def notFriendsYet(uid1, uid2):
    cursor = conn.cursor()
    if cursor.execute("SELECT * FROM Friendship WHERE uid1 = '{0}' AND uid2 = '{1}'".format(uid1, uid2)):
        return False
    elif cursor.execute("SELECT * FROM Friendship WHERE uid2 = '{0}' AND uid1 = '{1}'".format(uid1, uid2)):
        return False
    else:
        return True


def getFriends(uid):
    cursor = conn.cursor()
    query = ("SELECT uid2 FROM Friendship WHERE uid1 = '{0}'".format(uid))
    cursor.execute(query)
    return cursor.fetchall()


def getOtherFriends(uid):
    cursor = conn.cursor()
    query = ("SELECT uid1 FROM Friendship WHERE uid2 = '{0}'".format(uid))
    cursor.execute(query)
    return cursor.fetchall()


def getfname(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT fname, lname FROM User WHERE uid = '{0}'".format(uid))
    return cursor.fetchall()


def tagPhoto(tags, pid):
    cursor = conn.cursor()
    for tag in tags:
        cursor.execute("INSERT INTO tag (hashtag, pid) VALUES ('{0}', '{1}')".format(tag, pid))
    conn.commit()


def getAlbums(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT name, aid FROM Album WHERE uid = '{0}'".format(uid))
    return cursor.fetchall()


def deletePhoto(pid):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Photo WHERE pid='{0}'".format(pid))
    conn.commit()


def getPhotosFromAlbum(aid, uid):
    cursor = conn.cursor()
    query = "SELECT P.pid FROM Photo P, Album A WHERE A.aid = P.aid AND A.aid = '{0}' AND P.uid = '{1}'".format(aid,
                                                                                                                uid)
    cursor.execute(query.format(aid, uid))
    return cursor.fetchall()

# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
