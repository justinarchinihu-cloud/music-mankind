from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

import os


app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

app.config["SECRET_KEY"] = "change-this-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///music_mankind.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


login_manager = LoginManager()

login_manager.login_view = "login"

login_manager.init_app(app)


# =========================
# MODELS
# =========================

class User(db.Model, UserMixin):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(200),
        nullable=False
    )


class Purchase(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    song_title = db.Column(
        db.String(120),
        nullable=False
    )

    price = db.Column(
        db.Integer,
        default=99
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


class ArtistUpload(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    artist_name = db.Column(
        db.String(120),
        nullable=False
    )

    artist_role = db.Column(
        db.String(120),
        nullable=False
    )

    album_name = db.Column(
        db.String(200),
        nullable=False
    )

    artist_bio = db.Column(
        db.Text,
        nullable=True
    )

    image_filename = db.Column(
        db.String(200),
        nullable=False
    )

    audio_filename = db.Column(
        db.String(200),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


# =========================
# LOGIN MANAGER
# =========================

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# =========================
# HOME
# =========================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================
# MUSIC PAGE
# =========================

@app.route("/music")
def music():

    uploads = ArtistUpload.query.all()

    return render_template(
        "music.html",
        uploads=uploads
    )


# =========================
# ARTISTS
# =========================

@app.route("/artist1")
def artist1():

    return render_template(
        "artist1.html"
    )


@app.route("/artist2")
def artist2():

    return render_template(
        "artist2.html"
    )


@app.route("/artist3")
def artist3():

    return render_template(
        "artist3.html"
    )


@app.route("/artist4")
def artist4():

    return render_template(
        "artist4.html"
    )


# =========================
# ALBUMS
# =========================

@app.route("/calvin_nook")
def calvin_nook():

    return render_template(
        "calvin_nook.html"
    )


@app.route("/half-it-all")
def half_it_all():

    return render_template(
        "half_it_all.html"
    )


@app.route("/unspoken-master")
def unspoken_master():

    return render_template(
        "unspoken_master.html"
    )


@app.route("/man-vs-machine")
def man_vs_machine():

    return render_template(
        "man_vs_machine.html"
    )


# =========================
# AUDIO VISUALIZER
# =========================

@app.route("/audio-visualizer")
def audio_visualizer():

    uploads = ArtistUpload.query.all()

    songs = []

    for upload in uploads:

        songs.append({

            "title": upload.artist_role,

            "artist": upload.artist_name,

            "album": upload.album_name,

            "file": f"Audio/{upload.audio_filename}",

            "cover": f"Images/{upload.image_filename}"

        })

    # Default built-in songs

    songs.extend([

        {
            "title": "Drum And Bass",
            "artist": "Justin.url",
            "album": "Man Vs. Machine",
            "file": "Audio/drum_and_bass.m4a",
            "cover": "Images/Man_Vs_Machine_cover.jpg"
        },

        {
            "title": "Everything I Need",
            "artist": "Justin.url",
            "album": "Man Vs. Machine",
            "file": "Audio/everything_i_need.m4a",
            "cover": "Images/Man_Vs_Machine_cover.jpg"
        }

    ])

    return render_template(
        "audio_visualizer.html",
        songs=songs
    )


# =========================
# ABOUT
# =========================

@app.route("/about")
def about():

    return render_template(
        "about_us.html"
    )


# =========================
# SIGNUP
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        email = request.form.get(
            "email"
        )

        password = request.form.get(
            "password"
        )

        existing_user = User.query.filter(
            (User.username == username)
            |
            (User.email == email)
        ).first()

        if existing_user:

            flash(
                "Username or email already exists."
            )

            return redirect(
                url_for("signup")
            )

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(new_user)

        db.session.commit()

        login_user(new_user)

        return redirect(
            url_for("home")
        )

    return render_template(
        "signup.html"
    )


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email"
        )

        password = request.form.get(
            "password"
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if (
            not user
            or
            not check_password_hash(
                user.password_hash,
                password
            )
        ):

            flash(
                "Invalid email or password."
            )

            return redirect(
                url_for("login")
            )

        login_user(user)

        return redirect(
            url_for("home")
        )

    return render_template(
        "login.html"
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("home")
    )


# =========================
# PURCHASES
# =========================

@app.route("/purchase/<song_title>")
@login_required
def purchase(song_title):

    new_purchase = Purchase(
        song_title=song_title,
        price=99,
        user_id=current_user.id
    )

    db.session.add(new_purchase)

    db.session.commit()

    flash(
        f"You purchased {song_title} for $0.99."
    )

    return redirect(
        url_for("my_library")
    )


@app.route("/my-library")
@login_required
def my_library():

    purchases = Purchase.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "my_library.html",
        purchases=purchases
    )


# =========================
# GALLERY
# =========================

@app.route("/gallery")
def gallery():

    uploads = ArtistUpload.query.all()

    return render_template(
        "gallery.html",
        uploads=uploads
    )


@app.route("/upload_artist", methods=["POST"])
@login_required
def upload_artist():

    artist_name = request.form.get(
        "artist_name"
    )

    artist_role = request.form.get(
        "artist_role"
    )

    album_name = request.form.get(
        "album_name"
    )

    artist_bio = request.form.get(
        "artist_bio"
    )

    image = request.files.get(
        "artist_image"
    )

    audio = request.files.get(
        "artist_audio"
    )

    if not image or not audio:

        flash(
            "Missing upload files."
        )

        return redirect(
            url_for("gallery")
        )

    allowed_images = [
        "png",
        "jpg",
        "jpeg"
    ]

    allowed_audio = [
        "mp3",
        "m4a"
    ]

    image_ext = image.filename.rsplit(
        ".",
        1
    )[1].lower()

    audio_ext = audio.filename.rsplit(
        ".",
        1
    )[1].lower()

    if image_ext not in allowed_images:

        flash(
            "Only JPG and PNG images allowed."
        )

        return redirect(
            url_for("gallery")
        )

    if audio_ext not in allowed_audio:

        flash(
            "Only MP3 and M4A audio allowed."
        )

        return redirect(
            url_for("gallery")
        )

    image_filename = secure_filename(
        image.filename
    )

    audio_filename = secure_filename(
        audio.filename
    )

    image.save(
        os.path.join(
            "static/Images",
            image_filename
        )
    )

    audio.save(
        os.path.join(
            "static/Audio",
            audio_filename
        )
    )

    upload = ArtistUpload(

        artist_name=artist_name,

        artist_role=artist_role,

        album_name=album_name,

        artist_bio=artist_bio,

        image_filename=image_filename,

        audio_filename=audio_filename,

        user_id=current_user.id
    )

    db.session.add(upload)

    db.session.commit()

    flash(
        "Artist uploaded successfully."
    )

    return redirect(
        url_for("gallery")
    )


# =========================
# RUN APP
# =========================

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(debug=True)