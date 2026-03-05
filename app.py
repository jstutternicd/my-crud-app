import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = "books.db"

DUMMY_BOOKS = [
    ("The Great Gatsby", "F. Scott Fitzgerald", 1925, "A story of wealth, love, and the American Dream in the Jazz Age."),
    ("To Kill a Mockingbird", "Harper Lee", 1960, "A young girl in Alabama witnesses racial injustice and moral courage."),
    ("1984", "George Orwell", 1949, "A dystopian vision of totalitarian surveillance and thought control."),
    ("Pride and Prejudice", "Jane Austen", 1813, "A witty tale of manners, marriage, and misjudgment in Regency England."),
    ("The Catcher in the Rye", "J.D. Salinger", 1951, "A teenager wanders New York City grappling with alienation and identity."),
    ("One Hundred Years of Solitude", "Gabriel Garcia Marquez", 1967, "A multi-generational saga of the Buendia family in a mythical Colombian town."),
    ("Brave New World", "Aldous Huxley", 1932, "A future society engineered for stability through pleasure and conformity."),
    ("The Hobbit", "J.R.R. Tolkien", 1937, "A reluctant hobbit embarks on an epic adventure with dwarves and a wizard."),
    ("Fahrenheit 451", "Ray Bradbury", 1953, "In a future where books are banned, a fireman begins to question his role."),
    ("Dune", "Frank Herbert", 1965, "A young nobleman navigates politics, religion, and ecology on a desert planet."),
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER,
            description TEXT
        )"""
    )
    count = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    if count == 0:
        db.executemany(
            "INSERT INTO books (title, author, year, description) VALUES (?, ?, ?, ?)",
            DUMMY_BOOKS,
        )
    db.commit()


with app.app_context():
    init_db()


@app.route("/")
def index():
    db = get_db()
    books = db.execute("SELECT * FROM books ORDER BY title").fetchall()
    return render_template("index.html", books=books)


@app.route("/book/<int:book_id>")
def detail(book_id):
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if book is None:
        return "Book not found", 404
    return render_template("detail.html", book=book)


@app.route("/book/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form["title"].strip()
        author = request.form["author"].strip()
        year = request.form.get("year", "").strip()
        description = request.form.get("description", "").strip()
        if not title or not author:
            return render_template(
                "form.html", error="Title and Author are required.", book=request.form
            )
        db = get_db()
        db.execute(
            "INSERT INTO books (title, author, year, description) VALUES (?, ?, ?, ?)",
            (title, author, int(year) if year else None, description or None),
        )
        db.commit()
        return redirect(url_for("index"))
    return render_template("form.html", book=None)


@app.route("/book/<int:book_id>/edit", methods=["GET", "POST"])
def edit(book_id):
    db = get_db()
    if request.method == "POST":
        title = request.form["title"].strip()
        author = request.form["author"].strip()
        year = request.form.get("year", "").strip()
        description = request.form.get("description", "").strip()
        if not title or not author:
            return render_template(
                "form.html", error="Title and Author are required.", book=request.form
            )
        db.execute(
            "UPDATE books SET title=?, author=?, year=?, description=? WHERE id=?",
            (title, author, int(year) if year else None, description or None, book_id),
        )
        db.commit()
        return redirect(url_for("detail", book_id=book_id))
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if book is None:
        return "Book not found", 404
    return render_template("form.html", book=book)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete(book_id):
    db = get_db()
    db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    db.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
