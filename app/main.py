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
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///music_mankind.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_title = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, default=99)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/artist1")
def artist1():
    return render_template("artist1.html")


@app.route("/artist2")
def artist2():
    return render_template("artist2.html")


@app.route("/artist3")
def artist3():
    return render_template("artist3.html")


@app.route("/calvin_nook")
def calvin_nook():
    return render_template("calvin_nook.html")


@app.route("/half-it-all")
def half_it_all():
    return render_template("half_it_all.html")


@app.route("/unspoken-master")
def unspoken_master():
    return render_template("unspoken_master.html")


@app.route("/man-vs-machine")
def man_vs_machine():
    return render_template("man_vs_machine.html")


@app.route("/audio-visualizer")
def audio_visualizer():
    songs = [
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
        },
        {
            "title": "Aomame",
            "artist": "Evan Anderson",
            "album": "Half It All",
            "file": "Audio/aomame.mp3",
            "cover": "Images/half_it_all_cover.jpg"
        },
        {
            "title": "Ayn",
            "artist": "Evan Anderson",
            "album": "Half It All",
            "file": "Audio/ayn.mp3",
            "cover": "Images/half_it_all_cover.jpg"
        },
        {
            "title": "Ronin",
            "artist": "Evan Anderson",
            "album": "Half It All",
            "file": "Audio/Ronin.mp3",
            "cover": "Images/half_it_all_cover.jpg"
        },
        {
            "title": "Heal",
            "artist": "Evan Anderson",
            "album": "Half It All",
            "file": "Audio/heal.mp3",
            "cover": "Images/half_it_all_cover.jpg"
        },
        {
            "title": "TownHouse",
            "artist": "Evan Anderson",
            "album": "Half It All",
            "file": "Audio/TownHouse.mp3",
            "cover": "Images/half_it_all_cover.jpg"
        },
        {
            "title": "Unspoken Master",
            "artist": "fro.nea",
            "album": "The Unspoken Master",
            "file": "Audio/unspoken master.mp3",
            "cover": "Images/artist2.jpg"
        },
        {
            "title": "Less Is More",
            "artist": "fro.nea",
            "album": "The Unspoken Master",
            "file": "Audio/less is more.wav",
            "cover": "Images/artist2.jpg"
        },
        {
            "title": "Live A Little (OG Mix)",
            "artist": "fro.nea",
            "album": "The Unspoken Master",
            "file": "Audio/Live A Little (OG Mix).mp3",
            "cover": "Images/artist2.jpg"
        }
    ]

    return render_template("audio_visualizer.html", songs=songs)


@app.route("/about")
def about():
    return render_template("about_us.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already exists.")
            return redirect(url_for("signup"))

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("home"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.")
            return redirect(url_for("login"))

        login_user(user)
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


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

    flash(f"You purchased {song_title} for $0.99.")
    return redirect(url_for("my_library"))


@app.route("/my-library")
@login_required
def my_library():
    purchases = Purchase.query.filter_by(user_id=current_user.id).all()
    return render_template("my_library.html", purchases=purchases)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)