import sqlite3
from flask import Flask, jsonify, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    connection.close()
    return post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        return render_template('404.html'), 404
    else:
        return render_template('post.html', post=post)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            connection.commit()
            connection.close()
            return redirect(url_for('index'))

    return render_template('create.html')

# Health check endpoint
@app.route('/healthz')
def healthz():
    response = {'status': 'OK'}
    return jsonify(response), 200

# Status endpoint
@app.route('/status')
def status():
    posts_count = len(get_db_connection().execute('SELECT * FROM posts').fetchall())
    response = {
        'status': 'OK',
        'posts_count': posts_count
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3111')
