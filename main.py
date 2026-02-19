from flask import Flask, render_template_string, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)


BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

INDEX_TEMPLATE = '''
<h1 class="mb-4">Последние статьи</h1>
{% if articles %}
    {% for article in articles %}
    <div class="card mb-3">
        <div class="card-body">
            <h5 class="card-title">
                <a href="/article/{{ article[0] }}" class="text-decoration-none">{{ article[1] }}</a>
            </h5>
            <p class="card-text">{{ article[2][:150] }}{% if article[2]|length > 150 %}...{% endif %}</p>
            <div class="d-flex justify-content-between">
                <small class="text-muted">Автор: {{ article[3] }}</small>
                <small class="text-muted">{{ article[4][:16] }}</small>
            </div>
            <a href="/article/{{ article[0] }}" class="btn btn-primary btn-sm mt-2">Читать полностью</a>
        </div>
    </div>
    {% endfor %}
{% else %}
    <div class="alert alert-info">
        Статей пока нет. <a href="/create">Напишите первую!</a>
    </div>
{% endif %}
'''

CREATE_TEMPLATE = '''
<h2 class="mb-4">Создать статью</h2>
<form method="POST">
    <div class="mb-3">
        <label class="form-label">Заголовок</label>
        <input type="text" name="title" class="form-control" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Автор</label>
        <input type="text" name="author" class="form-control" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Текст статьи</label>
        <textarea name="content" class="form-control" rows="8" required></textarea>
    </div>
    <button type="submit" class="btn btn-primary">Опубликовать</button>
    <a href="/" class="btn btn-secondary">Отмена</a>
</form>
'''

ARTICLE_TEMPLATE = '''
<div class="row">
    <div class="col-md-8">
        <a href="/" class="btn btn-secondary mb-3">← Назад к списку</a>
        
        <article class="card">
            <div class="card-body">
                <h1 class="card-title">{{ article[1] }}</h1>
                
                <div class="article-meta text-muted mb-4">
                    <div class="d-flex justify-content-between">
                        <div>
                            <strong>Автор:</strong> {{ article[3] }} | 
                            <strong>Опубликовано:</strong> {{ article[4][:16] }}
                        </div>
                    </div>
                </div>

                <div class="article-content">
                    {{ article[2] | replace('\n', '<br>') | safe }}
                </div>
            </div>
        </article>

        <div class="mt-4">
            <a href="/" class="btn btn-secondary">← Назад к списку</a>
        </div>
    </div>
</div>
'''

def init_db():
    conn = sqlite3.connect('articles.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  content TEXT NOT NULL,
                  author TEXT NOT NULL,
                  created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

def render_base(content, title="Мини-Статьи"):
    return render_template_string(BASE_TEMPLATE, content=content, title=title)

@app.route('/')
def index():
    conn = sqlite3.connect('articles.db')
    c = conn.cursor()
    c.execute("SELECT * FROM articles ORDER BY created_at DESC")
    articles = c.fetchall()
    conn.close()
    
    content = render_template_string(INDEX_TEMPLATE, articles=articles)
    return render_base(content)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']
        
        conn = sqlite3.connect('articles.db')
        c = conn.cursor()
        c.execute("INSERT INTO articles (title, content, author, created_at) VALUES (?, ?, ?, ?)",
                  (title, content, author, datetime.now()))
        conn.commit()
        conn.close()
        
        return redirect('/')
    
    content = render_template_string(CREATE_TEMPLATE)
    return render_base(content, "Создать статью")

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    conn = sqlite3.connect('articles.db')
    c = conn.cursor()
    c.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
    article = c.fetchone()
    conn.close()
    
    if not article:
        return "Статья не найдена", 404
    
    content = render_template_string(ARTICLE_TEMPLATE, article=article)
    return render_base(content, article[1])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)