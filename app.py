import os
import sqlite3
from flask import Flask, redirect, render_template, request, session, url_for
import config, forum
from forum import add_user, get_user, verify_password, get_user_threads, get_user_messages, get_user_stats, update_profile, get_user_by_id

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    threads = forum.get_threads()
    return render_template("index.html", threads=threads)

@app.route("/thread/<int:thread_id>")
def show_thread(thread_id):
    thread = forum.get_thread(thread_id)
    messages = forum.get_messages(thread_id)
    return render_template("thread.html", thread=thread, messages=messages)

@app.route("/new_thread", methods=["POST"])
def new_thread():
    title = request.form["title"]
    content = request.form["content"]
    user_id = session["user_id"]

    thread_id = forum.add_thread(title, content, user_id)
    return redirect("/thread/" + str(thread_id))

@app.route("/new_message", methods=["POST"])
def new_message():
    content = request.form["content"]
    user_id = session["user_id"]
    thread_id = request.form["thread_id"]

    forum.add_message(content, user_id, thread_id)
    return redirect("/thread/" + str(thread_id))

@app.route("/edit/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    message = forum.get_message(message_id)

    if request.method == "GET":
        return render_template("edit.html", message=message)

    if request.method == "POST":
        content = request.form["content"]
        forum.update_message(message["id"], content)
        return redirect("/thread/" + str(message["thread_id"]))

@app.route("/remove/<int:message_id>", methods=["GET", "POST"])
def remove_message(message_id):
    message = forum.get_message(message_id)

    if request.method == "GET":
        return render_template("remove.html", message=message)

    if request.method == "POST":
        if "continue" in request.form:
            forum.remove_message(message["id"])
        return redirect("/thread/" + str(message["thread_id"]))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        if password1 != password2:
            return "Salasanat eivät täsmää"

        try:
            add_user(username, password1)
            return redirect("/") 
        except sqlite3.IntegrityError:
            return "VIRHE: tunnus on jo varattu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            user = get_user(username)
            if user and verify_password(user['password_hash'], password):
                session["user_id"] = user['id']
                return redirect("/")
            else:
                return render_template("login.html", error="Virheellinen tunnus tai salasana")
        except IndexError:
            return render_template("login.html", error="Virheellinen tunnus tai salasana")

@app.route("/logout")
def logout():
    del session["user_id"]
    return redirect("/")

@app.route("/search")
def search():
    query = request.args.get("query")
    results = forum.search(query) if query else []
    return render_template("index.html", query=query, results=results)

@app.route("/new_thread_page")
def new_thread_page():
    return render_template("new_thread.html")

@app.route("/create_thread", methods=["POST"])
def create_thread():
    title = request.form["title"]
    content = request.form["content"]
    tag_name = request.form.get("tag")
    user_id = session["user_id"]

    thread_id = forum.add_thread(title, content, user_id, tag_name)
    return redirect("/thread/" + str(thread_id))

@app.route("/view_threads")
def view_threads():
    threads = forum.get_threads()
    return render_template("view_threads.html", threads=threads)

@app.route("/profile/<int:user_id>")
def profile(user_id):
    user = get_user_by_id(user_id)
    threads = get_user_threads(user_id)
    messages = get_user_messages(user_id)
    thread_count, message_count = get_user_stats(user_id)
    return render_template("profile.html", user=user, threads=threads, messages=messages, thread_count=thread_count, message_count=message_count)

@app.route("/update_profile", methods=["POST"])
def update_profile_route():
    user_id = session["user_id"]
    profile_image = request.files.get("profile_image")
    bio = request.form.get("bio")

    if profile_image:
        profile_image_filename = f"profile_images/{user_id}_{profile_image.filename}"
        profile_image.save(os.path.join("static", profile_image_filename))
    else:
        profile_image_filename = None

    update_profile(user_id, profile_image_filename, bio)
    return redirect(url_for("profile", user_id=user_id))

@app.route("/edit_profile")
def edit_profile_page():
    user_id = session["user_id"]
    user = get_user_by_id(user_id)
    return render_template("edit_profile.html", user=user)