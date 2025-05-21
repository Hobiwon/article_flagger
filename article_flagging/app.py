import os
from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import search_articles, create_post, get_posts, create_reply, get_replies
from db import get_connection

app = Flask(__name__)
# app.secret_key = "supersecret"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pw_hash = generate_password_hash(request.form['password'])
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password_hash) VALUES (:1, :2)", (username, pw_hash))
            conn.commit()
            flash("Registered successfully. Please log in.")
            return redirect(url_for('login'))
        except:
            flash("Username already taken.")
        finally:
            conn.close()
    return render_template('register.html')
# Dummy login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pw = request.form['password']
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password_hash FROM users WHERE username = :1", (username,))
        row = cur.fetchone()
        conn.close()
        if row and check_password_hash(row[1], pw):
            session['user_id'] = row[0]
            session['username'] = username
            return redirect(url_for('index'))
        flash("Invalid login.")
    return render_template('login.html')

@app.route('/')
def index():
    posts = get_posts()
    return render_template('index.html', posts=posts)

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    page_size = 10
    offset = (page - 1) * page_size

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, summary FROM (
            SELECT a.*, ROWNUM rnum FROM (
                SELECT * FROM articles 
                WHERE LOWER(title) LIKE :1 OR LOWER(summary) LIKE :1
                ORDER BY uploaded_at DESC
            ) a WHERE ROWNUM <= :2
        ) WHERE rnum > :3
    """, ('%' + keyword.lower() + '%', offset + page_size, offset))
    results = cur.fetchall()
    conn.close()

    return render_template('search.html', results=results, keyword=keyword, page=page)

@app.route('/post/<int:article_id>', methods=['GET', 'POST'])
def post_article(article_id):
    if request.method == 'POST':
        comment = request.form.get('comment', '')
        create_post(session['user_id'], article_id, comment)
        return redirect(url_for('index'))
    return render_template('post.html', article_id=article_id)

@app.route('/reply/<int:post_id>', methods=['POST'])
def reply(post_id):
    comment = request.form['comment']
    article_id = request.form.get('article_id')
    if article_id:
        article_id = int(article_id)
    else:
        article_id = None
    create_reply(post_id, session['user_id'], comment, article_id)
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_article():
    if request.method == 'POST':
        title = request.form['title']
        summary = request.form['summary']
        file = request.files['file']
        filename = None

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO articles (title, summary, file_path, uploaded_by)
            VALUES (:1, :2, :3, :4)
        """, (title, summary, filename, session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('search'))

    return render_template('upload.html')