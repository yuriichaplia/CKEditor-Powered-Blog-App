from datetime import date
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)

try:
    ckeditor.init_app(app)
except ValueError:
    pass

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

class PostForm(FlaskForm):
    title = StringField('Blog Post Title', validators=[DataRequired()])
    subtitle = StringField('Blog Post Subtitle', validators=[DataRequired()])
    author_name = StringField("Blog Post's Author Name", validators=[DataRequired()])
    url = StringField('URL for Background Image', validators=[URL()])
    body = CKEditorField('Main Content', validators=[DataRequired()])
    submit = SubmitField('Submit Post', validators=[DataRequired()])

with app.app_context():
    db.create_all()

@app.route('/')
def get_all_posts():
    posts_database = db.session.execute(db.select(BlogPost)).scalars().all()
    posts = []
    for post in posts_database:
        posts.append(post)
    return render_template("index.html", all_posts=posts)

@app.route('/read')
def show_post():
    post_id = request.args.get('post_id')
    requested_post = (db.session.execute(db.select(BlogPost).where(BlogPost.id == int(post_id)))
                      .scalar_one())
    return render_template("post.html", post=requested_post)

@app.route('/new-post', methods=["GET", "POST"])
def add_new_post():
    post_form = PostForm()
    if post_form.validate_on_submit():
        title = post_form.title.data
        subtitle = post_form.subtitle.data
        author = post_form.author_name.data
        image = post_form.url.data
        date_variable = f"{date.today().strftime('%B')} {date.today().day}, {date.today().year}"
        body = request.form.get('body')

        post = BlogPost(title=title, subtitle=subtitle, date=date_variable,
                        body=body, author=author, img_url=image)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('get_all_posts'))

    return render_template('make-post.html', form=post_form, edit=False)

@app.route('/edit-post/<post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    post = (db.session.execute(db.select(BlogPost).where(BlogPost.id == int(post_id)))
            .scalar_one())
    post_form = PostForm(title=post.title,
                         subtitle=post.subtitle,
                         author_name=post.author,
                         url=post.img_url,
                         body=post.body
                         )
    if post_form.validate_on_submit():
        post.title = post_form.title.data
        post.subtitle = post_form.subtitle.data
        post.author = post_form.author_name.data
        post.img_url = post_form.url.data
        post.body = request.form.get('body')
        db.session.commit()

        return redirect(url_for('show_post', post_id=post_id))

    return render_template('make-post.html', form=post_form, edit=True)

@app.route('/delete/<post_id>')
def delete(post_id):
    post = (db.session.execute(db.select(BlogPost).where(BlogPost.id == int(post_id)))
            .scalar_one())
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True, port=5003)