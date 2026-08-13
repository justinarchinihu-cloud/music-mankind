from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

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

from datetime import datetime

import os


# =====================================
# APP CONFIG
# =====================================

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

app.config["SECRET_KEY"] = "change-this-secret-key"

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "instance",
    "music_mankind.db"
)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{DATABASE_PATH}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


# =====================================
# LOGIN MANAGER
# =====================================

login_manager = LoginManager()

login_manager.login_view = "login"

login_manager.init_app(app)


# =====================================
# USER MODEL
# =====================================

class User(
    db.Model,
    UserMixin
):

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

    is_admin = db.Column(
        db.Boolean,
        default=False
    )

    releases = db.relationship(
        "Release",
        backref="owner",
        lazy=True
    )

    videos = db.relationship(
        "Video",
        backref="owner",
        lazy=True
    )


# =====================================
# PURCHASE MODEL
# =====================================

class Purchase(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    song_title = db.Column(
        db.String(200),
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


# =====================================
# RELEASE MODEL
# =====================================

class Release(db.Model):

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

    release_type = db.Column(
        db.String(20),
        nullable=False
    )

    release_date = db.Column(
        db.Date,
        nullable=False
    )

    artist_bio = db.Column(
        db.Text,
        nullable=True
    )

    image_filename = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    tracks = db.relationship(
        "Track",
        backref="release",
        lazy=True,
        cascade="all, delete-orphan"
    )


# =====================================
# TRACK MODEL
# =====================================

class Track(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    track_number = db.Column(
        db.Integer,
        nullable=False
    )

    release_id = db.Column(
        db.Integer,
        db.ForeignKey("release.id"),
        nullable=False
    )


# =====================================
# VIDEO MODEL
# =====================================

class Video(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


# =====================================
# LOGIN LOADER
# =====================================

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# =====================================
# HOME
# =====================================

@app.route("/")
def home():

    latest_releases = Release.query.order_by(
        Release.created_at.desc()
    ).limit(12).all()

    return render_template(
        "index.html",
        uploads=latest_releases
    )


app.add_url_rule("/", endpoint="index", view_func=home)


# =====================================
# MUSIC PAGE
# =====================================

@app.route("/music")
def music():

    uploads = Release.query.order_by(
        Release.created_at.desc()
    ).all()

    return render_template(
        "music.html",
        uploads=uploads
    )


# =====================================
# GALLERY
# =====================================

@app.route("/gallery")
def gallery():

    uploads = Release.query.order_by(
        Release.created_at.desc()
    ).all()

    return render_template(
        "gallery.html",
        uploads=uploads
    )


# =====================================
# AUDIO VISUALIZER
# =====================================
@app.route("/audio-visualizer")
def audio_visualizer():

    songs = []

    releases = Release.query.order_by(
        Release.created_at.desc()
    ).all()

    for release in releases:

        for track in release.tracks:

            songs.append({

                "title": track.title,

                "artist": release.artist_name,

                "album": release.album_name,

                "release_type": release.release_type,

                "release_date": release.release_date.strftime(
                    "%B %d, %Y"
                ),

                "file": f"Audio/{track.filename}",

                "cover": f"images/{release.image_filename}"

            })

    songs.extend([

        # =====================================
        # MAN VS. MACHINE
        # =====================================

        {
            "title": "Drum And Bass",
            "artist": "Justin.url",
            "album": "Man Vs. Machine",
            "release_type": "album",
            "release_date": "January 1, 2025",
            "file": "Audio/drum_and_bass.m4a",
            "cover": "images/Man_Vs_Machine_cover.jpg"
        },

        {
            "title": "Everything I Need",
            "artist": "Justin.url",
            "album": "Man Vs. Machine",
            "release_type": "album",
            "release_date": "January 1, 2025",
            "file": "Audio/everything_i_need.m4a",
            "cover": "images/Man_Vs_Machine_cover.jpg"
        },

        {
            "title": "When I See You",
            "artist": "Justin.url",
            "album": "Man Vs. Machine",
            "release_type": "album",
            "release_date": "January 1, 2025",
            "file": "Audio/when_i_see_you.mp4",
            "cover": "images/Man_Vs_Machine_cover.jpg"
        },

        # =====================================
        # DEMO PACK EP / 2019 EP
        # =====================================

        {
            "title": "Summer In A Nutshell",
            "artist": "Justin.url",
            "album": "Demo Pack EP",
            "release_type": "ep",
            "release_date": "January 1, 2025",
            "file": "Audio/Summer in a Nutshell.mp3",
            "cover": "images/2019_EP.jpg"
        },

        {
            "title": "Sincerely",
            "artist": "Justin.url",
            "album": "Demo Pack EP",
            "release_type": "ep",
            "release_date": "January 1, 2025",
            "file": "Audio/Sincerely Me(the Hate U Give).mp3",
            "cover": "images/2019_EP.jpg"
        },

        {
            "title": "Poem For A Loved One",
            "artist": "Justin.url",
            "album": "Demo Pack EP",
            "release_type": "ep",
            "release_date": "January 1, 2025",
            "file": "Audio/Poem for a loved one _Letter to a friend.mp3",
            "cover": "images/2019_EP.jpg"
        },

        {
            "title": "Worst Time Of The Year",
            "artist": "Justin.url",
            "album": "Demo Pack EP",
            "release_type": "ep",
            "release_date": "January 1, 2025",
            "file": "Audio/Worst Time of the Year.mp3",
            "cover": "images/2019_EP.jpg"
        },

        {
            "title": "Change19",
            "artist": "Justin.url",
            "album": "Demo Pack EP",
            "release_type": "ep",
            "release_date": "January 1, 2025",
            "file": "Audio/Change19.mp3",
            "cover": "images/2019_EP.jpg"
        }

    ])

    return render_template(
        "audio_visualizer.html",
        songs=songs
    )


# =====================================
# ARTIST PAGES
# =====================================

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


# =====================================
# ALBUM PAGES
# =====================================

@app.route("/man-vs-machine")
def man_vs_machine():

    return render_template(
        "man_vs_machine.html"
    )


@app.route("/demo-pack-ep")
def demo_pack_ep():

    return render_template(
        "2019.ep.html"
    )

# =====================================
# SIGNUP
# =====================================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
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
            (
                User.username == username
            )
            |
            (
                User.email == email
            )
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

            password_hash=generate_password_hash(
                password
            )
        )

        db.session.add(
            new_user
        )

        db.session.commit()

        login_user(
            new_user
        )

        flash(
            "Account created successfully."
        )

        return redirect(
            url_for("home")
        )

    return render_template(
        "signup.html"
    )


# =====================================
# LOGIN
# =====================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
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

        login_user(
            user
        )

        flash(
            "Logged in successfully."
        )

        return redirect(
            url_for("home")
        )

    return render_template(
        "login.html"
    )


# =====================================
# LOGOUT
# =====================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Logged out."
    )

    return redirect(
        url_for("home")
    )


# =====================================
# PURCHASE
# =====================================

@app.route(
    "/purchase/<song_title>"
)
@login_required
def purchase(song_title):

    new_purchase = Purchase(

        song_title=song_title,

        price=99,

        user_id=current_user.id
    )

    db.session.add(
        new_purchase
    )

    db.session.commit()

    flash(
        f"You purchased {song_title} for $0.99"
    )

    return redirect(
        url_for("my_library")
    )


# =====================================
# MY LIBRARY
# =====================================

@app.route("/my-library")
@login_required
def my_library():

    purchases = Purchase.query.filter_by(
        user_id=current_user.id
    ).all()

    releases = Release.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Release.created_at.desc()
    ).all()

    return render_template(

        "my_library.html",

        purchases=purchases,

        releases=releases
    )


# =====================================
# UPLOAD RELEASE
# =====================================

@app.route(
    "/upload_artist",
    methods=["POST"]
)
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

    release_type = request.form.get(
        "release_type"
    )

    release_date = request.form.get(
        "release_date"
    )

    artist_bio = request.form.get(
        "artist_bio"
    )

    image = request.files.get(
        "artist_image"
    )

    audio_files = request.files.getlist(
        "artist_audio"
    )

    if not image:

        flash(
            "Cover image required."
        )

        return redirect(
            url_for("gallery")
        )

    if len(audio_files) == 0:

        flash(
            "At least one audio file required."
        )

        return redirect(
            url_for("gallery")
        )

    track_count = len(audio_files)

    if release_type == "single":

        if track_count != 1:

            flash(
                "Singles must contain exactly 1 track."
            )

            return redirect(
                url_for("gallery")
            )

    elif release_type == "ep":

        if track_count < 2 or track_count > 7:

            flash(
                "EPs must contain 2–7 tracks."
            )

            return redirect(
                url_for("gallery")
            )

    elif release_type == "album":

        if track_count < 8 or track_count > 12:

            flash(
                "Albums must contain 8–12 tracks."
            )

            return redirect(
                url_for("gallery")
            )

    else:

        flash(
            "Invalid release type."
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
        "m4a",
        "wav"
    ]

    image_ext = image.filename.rsplit(
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

    image_filename = secure_filename(
        image.filename
    )

    image.save(
        os.path.join(
            "static/images",
            image_filename
        )
    )

    release = Release(

        artist_name=artist_name,

        artist_role=artist_role,

        album_name=album_name,

        release_type=release_type,

        release_date=datetime.strptime(
            release_date,
            "%Y-%m-%d"
        ).date(),

        artist_bio=artist_bio,

        image_filename=image_filename,

        user_id=current_user.id
    )

    db.session.add(
        release
    )

    db.session.flush()

    for index, audio in enumerate(
        audio_files,
        start=1
    ):

        audio_ext = audio.filename.rsplit(
            ".",
            1
        )[1].lower()

        if audio_ext not in allowed_audio:

            flash(
                f"{audio.filename} is not a valid audio file."
            )

            return redirect(
                url_for("gallery")
            )

        audio_filename = secure_filename(
            audio.filename
        )

        audio.save(
            os.path.join(
                "static/Audio",
                audio_filename
            )
        )

        track_title = os.path.splitext(
            audio_filename
        )[0]

        track = Track(

            title=track_title,

            filename=audio_filename,

            track_number=index,

            release_id=release.id
        )

        db.session.add(
            track
        )

    db.session.commit()

    flash(
        f"{album_name} uploaded successfully."
    )

    return redirect(
        url_for("gallery")
    )


# =====================================
# UPLOAD VIDEO
# =====================================

@app.route(
    "/upload_video",
    methods=["POST"]
)
@login_required
def upload_video():

    title = request.form.get(
        "video_title"
    )

    description = request.form.get(
        "video_description"
    )

    video_file = request.files.get(
        "video_file"
    )

    if not video_file:

        flash(
            "Please select a video file."
        )

        return redirect(
            url_for("videos")
        )

    allowed_videos = [
        "mp4",
        "webm",
        "mov",
        "mkv",
        "avi"
    ]

    video_ext = video_file.filename.rsplit(
        ".",
        1
    )[-1].lower()

    if video_ext not in allowed_videos:

        flash(
            "Only MP4, WEBM, MOV, MKV, and AVI files are allowed."
        )

        return redirect(
            url_for("videos")
        )

    video_filename = secure_filename(
        video_file.filename
    )

    video_folder = os.path.join(
        app.root_path,
        "static",
        "Videos"
    )

    os.makedirs(
        video_folder,
        exist_ok=True
    )

    video_file.save(
        os.path.join(
            video_folder,
            video_filename
        )
    )

    new_video = Video(

        title=title,

        description=description,

        filename=video_filename,

        user_id=current_user.id
    )

    db.session.add(
        new_video
    )
    db.session.commit()

    flash(
        "Video uploaded successfully."
    )

    return redirect(
        url_for("videos")
    )


# =====================================
# ADMIN HELPERS
# =====================================

def _is_super_admin():

    return (
        current_user.is_authenticated
        and
        (
            current_user.username == "Admin101"
            or current_user.is_admin
        )
    )


# =====================================
# DELETE USER (ADMIN)
# =====================================

@app.route(
    "/admin/delete-user/<int:user_id>",
    methods=["POST"]
)
@login_required
def delete_user(user_id):

    if not _is_super_admin():

        flash(
            "You do not have permission."
        )

        return redirect(
            url_for("home")
        )

    user = db.session.get(
        User,
        user_id
    )

    if not user:

        flash(
            "User not found."
        )

        return redirect(
            url_for("admin_dashboard")
        )

    if user.username == "Admin101":

        flash(
            "Primary admin account cannot be deleted."
        )

        return redirect(
            url_for("admin_dashboard")
        )

    releases = Release.query.filter_by(
        user_id=user.id
    ).all()

    for release in releases:

        for track in release.tracks:

            try:

                audio_path = os.path.join(
                    app.root_path,
                    "static",
                    "Audio",
                    track.filename
                )

                if os.path.exists(audio_path):
                    os.remove(audio_path)

            except Exception:
                pass

            db.session.delete(track)

        try:

            image_path = os.path.join(
                app.root_path,
                "static",
                "images",
                release.image_filename
            )

            if os.path.exists(image_path):
                os.remove(image_path)

        except Exception:
            pass

        db.session.delete(release)

    Purchase.query.filter_by(
        user_id=user.id
    ).delete()

    Video.query.filter_by(
        user_id=user.id
    ).delete()

    db.session.delete(user)

    db.session.commit()

    flash(
        f"User {user.username} deleted successfully."
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =====================================
# ADMIN DASHBOARD
# =====================================

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if not _is_super_admin():

        flash(
            "You do not have permission."
        )

        return redirect(
            url_for("home")
        )

    users = User.query.order_by(
        User.id
    ).all()

    releases = Release.query.order_by(
        Release.created_at.desc()
    ).all()

    return render_template(
        "admin_dashboard.html",
        users=users,
        releases=releases
    )


# =====================================
# DELETE RELEASE
# =====================================

@app.route(
    "/admin/delete-release/<int:release_id>",
    methods=["POST"]
)
@login_required
def delete_release(release_id):

    if not _is_super_admin():

        return redirect(
            url_for("home")
        )

    release = Release.query.get_or_404(
        release_id
    )

    for track in release.tracks:

        try:

            audio_path = os.path.join(
                app.root_path,
                "static",
                "Audio",
                track.filename
            )

            if os.path.exists(audio_path):
                os.remove(audio_path)

        except Exception:
            pass

        db.session.delete(track)

    try:

        image_path = os.path.join(
            app.root_path,
            "static",
            "images",
            release.image_filename
        )

        if os.path.exists(image_path):
            os.remove(image_path)

    except Exception:
        pass

    db.session.delete(release)

    db.session.commit()

    flash(
        "Release deleted successfully."
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =====================================
# DELETE ALL USERS
# =====================================

@app.route(
    "/admin/delete-all-users",
    methods=["POST"]
)
@login_required
def delete_all_users():

    if not _is_super_admin():

        return redirect(
            url_for("home")
        )

    users = User.query.filter(
        User.is_admin == False
    ).all()

    for user in users:

        Purchase.query.filter_by(
            user_id=user.id
        ).delete()

        releases = Release.query.filter_by(
            user_id=user.id
        ).all()

        for release in releases:

            for track in release.tracks:

                try:

                    audio_path = os.path.join(
                        app.root_path,
                        "static",
                        "Audio",
                        track.filename
                    )

                    if os.path.exists(audio_path):
                        os.remove(audio_path)

                except Exception:
                    pass

            try:

                image_path = os.path.join(
                    app.root_path,
                    "static",
                    "images",
                    release.image_filename
                )

                if os.path.exists(image_path):
                    os.remove(image_path)

            except Exception:
                pass

            db.session.delete(release)

        db.session.delete(user)

    db.session.commit()

    flash(
        "All non-admin users deleted."
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =====================================
# DELETE ALL MEDIA
# =====================================

@app.route(
    "/admin/delete-all-media",
    methods=["POST"]
)
@login_required
def delete_all_media():

    if not _is_super_admin():

        return redirect(
            url_for("home")
        )

    releases = Release.query.all()

    for release in releases:

        for track in release.tracks:

            try:

                audio_path = os.path.join(
                    app.root_path,
                    "static",
                    "Audio",
                    track.filename
                )

                if os.path.exists(audio_path):
                    os.remove(audio_path)

            except Exception:
                pass

        try:

            image_path = os.path.join(
                app.root_path,
                "static",
                "images",
                release.image_filename
            )

            if os.path.exists(image_path):
                os.remove(image_path)

        except Exception:
            pass

    Purchase.query.delete()
    Track.query.delete()
    Release.query.delete()
    Video.query.delete()

    db.session.commit()

    flash(
        "All media deleted."
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =====================================
# DEBUG ADMIN
# =====================================

@app.route("/debug-admin")
@login_required
def debug_admin():

    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin
    }


# =====================================
# RELEASE PAGE
# =====================================

@app.route("/release/<int:release_id>")
def release_page(release_id):

    release = Release.query.get_or_404(
        release_id
    )

    return render_template(
        "release_player.html",
        release=release
    )


# =====================================
# VIDEOS PAGE
# =====================================

@app.route("/videos")
@login_required
def videos():

    videos = Video.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Video.created_at.desc()
    ).all()

    return render_template(
        "video.html",
       
        artist_name="Darvin",
        location="Jacksonville",
        latest_releases="Doomed / Kiss In The Wind MP3",
        videos=videos
    )


# =====================================
# DARVIN PAGE
# =====================================

@app.route("/darvin")
def darvin():

    songs = [
        {
            "title": "Doomed",
            "release_type": "single",
            "filename": "Audio/doomed by darvin.mp3"
        },
        {
            "title": "Kiss In The Wind",
            "release_type": "single",
            "filename": "Audio/kiss in the wind kiss in the wind.mp3"
        }
    ]

    return render_template(
        "darvin.html",
        artist_name="Darvin",
        location="Jacksonville",
        latest_releases="Doomed / Kiss In The Wind MP3",
        cover_image="images/darvin.JPG",
        profile_image="images/darvin.JPG",
        songs=songs
    )

    
@app.route("/rocklee")
def rocklee():

    songs = [
        {
            "title": "body2",
            "release_type": "single",
            "filename": "Audio/body2 by rocklee.m4a"
        },
        {
            "title": "body3",
            "release_type": "single",
            "filename": "Audio/body3 by rocklee.m4a"
        }
    ]

    return render_template(
        "rocklee.html",
        artist_name="Rocklee",
        location="Jacksonville",
        latest_releases="body2",
        cover_image="images/rocklee.jpg",
        profile_image="images/rocklee.jpg",
        songs=songs
    )
# =====================================
# RUN APP
# =====================================


    with app.app_context():
        db.create_all()

        admin_user = User.query.filter_by(
            username="Admin101"
        ).first()

        if admin_user:
            admin_user.is_admin = True
            db.session.commit()

    
@app.route("/radio")
def radio():
    return render_template("radio.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        admin_user = User.query.filter_by(username="Admin101").first()
        if admin_user:
            admin_user.is_admin = True
            db.session.commit()

    app.run(host="127.0.0.1", port=5001, debug=True)