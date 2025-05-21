from db import get_connection

def search_articles(keyword):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, summary FROM articles 
        WHERE LOWER(title) LIKE :1 OR LOWER(summary) LIKE :1
        FETCH FIRST 20 ROWS ONLY
    """, ('%' + keyword.lower() + '%',))
    results = cur.fetchall()
    conn.close()
    return results

def create_post(user_id, article_id, comment):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO posts (user_id, article_id, comment, created_at)
        VALUES (:1, :2, :3, SYSDATE)
    """, (user_id, article_id, comment))
    conn.commit()
    conn.close()

def get_posts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, a.title, a.id AS article_id, p.comment, u.username
        FROM posts p
        JOIN articles a ON p.article_id = a.id
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
    """)
    posts = cur.fetchall()
    conn.close()
    return posts

def create_reply(post_id, user_id, comment, article_id=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO replies (post_id, user_id, comment, article_id, created_at)
        VALUES (:1, :2, :3, :4, SYSDATE)
    """, (post_id, user_id, comment, article_id))
    conn.commit()
    conn.close()

def get_replies(post_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.comment, u.username, a.title
        FROM replies r
        LEFT JOIN users u ON r.user_id = u.id
        LEFT JOIN articles a ON r.article_id = a.id
        WHERE r.post_id = :1
        ORDER BY r.created_at ASC
    """, (post_id,))
    replies = cur.fetchall()
    conn.close()
    return replies