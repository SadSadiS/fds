from flask import Flask, render_template_string, request, redirect, abort
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), 'articles.db')

# =======================
# БАЗА ДАННЫХ
# =======================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =======================
# ШАБЛОНЫ
# =======================
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-dark bg-dark">
    <div class="container">
        <a class="navbar-brand" href="/">Мини-Статьи</a>
        <a href="/create" class="btn btn-light">Новая статья</a>
    </div>
</nav>
<div class="container mt-4">
    {{ content | safe }}
</div>
</body>
</html>
"""

INDEX_TEMPLATE = """
<h1>Последние статьи</h1>

{% for article in articles %}
<div class="card mb-3">
    <div class="card-body">
        <h5>
            <a href="/article/{{ article.id }}">{{ article.title }}</a>
        </h5>
        <p>{{ article.content[:150] }}{% if article.content|length > 150 %}...{% endif %}</p>
        <small>Автор: {{ article.author }} | {{ article.created_at }}</small>
    </div>
</div>
{% else %}
<div class="alert alert-info">
    Статей нет. <a href="/create">Создать первую</a>
</div>
{% endfor %}
"""

CREATE_TEMPLATE = """
<h2>Создать статью</h2>

<form method="post">
    <input name="title" class="form-control mb-2" placeholder="Заголовок" required>
    <input name="author" class="form-control mb-2" placeholder="Автор" required>
    <textarea name="content" class="form-control mb-2" rows="6" placeholder="Текст" required></textarea>
    <button class="btn btn-primary">Опубликовать</button>
</form>
"""

ARTICLE_TEMPLATE = """
<a href="/" class="btn btn-secondary mb-3">← Назад</a>

<h1>{{ article.title }}</h1>
<p><b>Автор:</b> {{ article.author }}</p>
<p><b>Дата:</b> {{ article.created_at }}</p>
<hr>
<div>
    {{ article.content | replace('\\n', '<br>') | safe }}
</div>
"""

# =======================
# РЕНДЕР
# =======================
def render_page(content, title="Мини-Статьи"):
    return render_template_string(BASE_TEMPLATE, content=content, title=title)

# =======================
# РОУТЫ
# =======================
@app.route('/')
def index():
    conn = get_db()
    articles = conn.execute(
        "SELECT * FROM articles ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    content = render_template_string(INDEX_TEMPLATE, articles=articles)
    return render_page(content)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        conn = get_db()
        conn.execute(
            "INSERT INTO articles (title, content, author, created_at) VALUES (?, ?, ?, ?)",
            (
                request.form['title'],
                request.form['content'],
                request.form['author'],
                datetime.now().strftime('%Y-%m-%d %H:%M')
            )
        )
        conn.commit()
        conn.close()
        return redirect('/')

    return render_page(render_template_string(CREATE_TEMPLATE), "Создать статью")

@app.route('/article/<int:article_id>')
def article(article_id):
    conn = get_db()
    article = conn.execute(
        "SELECT * FROM articles WHERE id = ?", (article_id,)
    ).fetchone()
    conn.close()

    if not article:
        abort(404)

    content = render_template_string(ARTICLE_TEMPLATE, article=article)
    return render_page(content, article['title'])

# =======================
# ТОЧКА ВХОДА
# =======================
# ВАЖНО: НИКАКОГО app.run()
