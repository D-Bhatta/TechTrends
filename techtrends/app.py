import logging
import sqlite3

from flask import (
    Flask,
    flash,
    json,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.exceptions import abort


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    log_connection("Get a post")
    connection = get_db_connection()
    post = connection.execute(
        "SELECT * FROM posts WHERE id = ?", (post_id,)
    ).fetchone()
    connection.close()
    return post


def get_num_connections():
    # Return number of connections
    connection = get_db_connection()
    num_connections_list = connection.execute(
        "SELECT COUNT(id) FROM numconnections"
    ).fetchone()
    connection.close()
    num_connections = [item for item in num_connections_list][0]
    # Since there is a logging connection for every logged connection
    return num_connections


def get_num_posts():
    # Return the number of posts
    connection = get_db_connection()
    num_posts_list = connection.execute(
        "SELECT COUNT(id) FROM posts"
    ).fetchone()
    connection.close()
    num_posts = [item for item in num_posts_list][0]
    return num_posts


def log_connection(reason: str):
    # Log everytime there is a db connection.
    connection = get_db_connection()
    connection.execute(
        "INSERT INTO numconnections (reason) VALUES (?)",
        (reason,),
    )
    connection.commit()
    connection.close()


# Define the Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = "your secret key"

# Define the main route of the web application
@app.route("/")
def index():
    log_connection("Get all posts")
    connection = get_db_connection()
    posts = connection.execute("SELECT * FROM posts").fetchall()
    connection.close()
    return render_template("index.html", posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error(f"Article not found")
        return render_template("404.html"), 404
    else:
        post_title = post["title"]
        app.logger.info(f"Article retrieved: {post_title}")
        return render_template("post.html", post=post)


# Define the About Us page
@app.route("/about")
def about():
    app.logger.info("About us page retrieved")
    return render_template("about.html")


# Define the post creation functionality
@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            log_connection("Create a post")
            connection = get_db_connection()
            connection.execute(
                "INSERT INTO posts (title, content) VALUES (?, ?)",
                (title, content),
            )
            connection.commit()
            connection.close()
            app.logger.info(f"New post created with title: {title}")
            return redirect(url_for("index"))

    return render_template("create.html")


# Return health status
@app.route("/healthz", methods=("GET", "POST"))
def healthz():
    return {"result": "OK - healthy"}, 200


# Return metrics about the application
@app.route("/metrics", methods=("GET", "POST"))
def metrics():
    num_posts = get_num_posts()
    num_connections = get_num_connections()

    return {
        "db_connection_count": num_connections,
        "post_count": num_posts,
    }, 200


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s: %(asctime)s, %(message)s",
        level=logging.DEBUG,
    )
    app.run(host="0.0.0.0", port="3111")
