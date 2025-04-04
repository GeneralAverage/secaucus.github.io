from flask import Flask, render_template, redirect, url_for, request, jsonify, send_from_directory, make_response
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

database = {}
history = [{'username': 'ADMIN', 'msg': 'Posts go here',
            'title': 'Posts go here', 'timestamp': None, 'filename': None, 'comments': []}]


def filterChat(msg):
    msg = ''.join(msg)
    msg = msg.lower()

    msg = msg.replace("1", "i")
    msg = msg.replace("3", "e")
    msg = msg.replace("8", "g")
    msg = msg.replace("0", "o")
    msg = msg.replace("!", "i")
    msg = msg.replace("@", "a")
    msg = msg.replace("|", "i")
    msg = msg.replace("$", "s")
    bannedwordslist = ["fuc", "fuk", "fck", "shit",
                       "nga", "nigg", "bitc", "btch", "retar"]
    for i in range(0, len(bannedwordslist)):
        if bannedwordslist[i] in msg:
            return True
    return False


@app.route("/", methods=['GET', 'POST'])
def mainpage():
    return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = str(request.form['username'])
        password = str(request.form['password'])
        if username not in database or password != database[username]:
            return render_template("invalidinfo.html")
        elif filterChat(username):
            return render_template("cmonbro.html")
        else:
            response = make_response(redirect("/"))
            response.set_cookie('currentuser', username)

            return response
    return render_template('login.html')


@app.route("/signup", methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        username = str(request.form['username'])
        password = str(request.form['password'])
        if username in database or len(password) < 1:
            return render_template('invalidinfo.html')
        elif filterChat(username):
            return render_template("cmonbro.html")
        else:
            database.update({username: password})
            response = make_response(redirect("/"))
            response.set_cookie('currentuser', username)

            return response
    return render_template('signup.html')


@app.route("/get_history", methods=['GET'])
def get_history():
    global history
    return history


@app.route("/update_history", methods=['POST'])
def change_history(msg):
    global history
    if history == None:
        history = []
    history.append(msg)
    return jsonify({"message": "history updated"})


@app.route("/get_commenthistory", methods=['GET'])
def get_commenthistory(post_id):
    global history
    return history[post_id]['comments']


@app.route("/update_commenthistory", methods=['POST'])
def change_commenthistory(post_id, msg):
    global history
    commenthistory = history[post_id]['comments']
    if commenthistory == None:
        commenthistory = []
    commenthistory.append(msg)
    return jsonify({"message": "history updated"})


@app.route("/submitmsg", methods=['GET', 'POST'])
def submitmsg():
    global history
    if request.method == 'POST':
        try:
            msg = str(request.form['msg'])
            title = str(request.form['title'])
            file = request.files['file']
            username = None
            name = request.cookies.get('currentuser')
            if ('currentuser' in request.cookies) and name != "":
                username = name
            else:
                return render_template('notloggedin.html')
            if filterChat(msg) == True or filterChat(title) == True:
                return render_template("cmonbro.html")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                change_history({'username': username, 'msg': msg, 'title': title,
                               'timestamp': timestamp, 'filename': filename, 'comments': []})
            else:
                change_history({'username': username, 'msg': msg, 'title': title,
                               'timestamp': timestamp, 'filename': None, 'comments': []})
            return redirect(url_for('viewposts'))
        except PermissionError:
            raise PermissionError('Insufficient Permissions!')
    else:
        return render_template('submitmsg.html')


@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/viewposts", methods=['GET', 'POST'])
def viewposts():
    global history
    name = request.cookies.get('currentuser')
    if ('currentuser' in request.cookies) and name != "":
        username = name
    else:
        return render_template('notloggedin.html')
    return render_template('viewposts.html', history=history)


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def viewpost(post_id):
    post = history[post_id]
    username = request.cookies.get('currentuser')
    if request.method == 'POST':
        comment_text = str(request.form['comment'])
        commenter_name = username
        # cookie stuff here
        change_commenthistory(post_id, {'username': commenter_name, 'comment': comment_text,
                              'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    return render_template('viewpost.html', post=post, post_id=post_id)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global username
    username = None
    response = make_response('Success!')
    response.set_cookie('currentuser', "", expires=0)
    return response
@app.route('/credits',methods=['GET','POST'])
def credits():
    return render_template('credits.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8081)
