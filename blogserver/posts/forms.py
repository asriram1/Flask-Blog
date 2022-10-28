from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired
from flask_login import current_user

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    documents = SelectField('Select a document to reference in your post', coerce=int)
    submit = SubmitField('Post')

    # def __init__(self, *args, **kwargs):
    #     super(PostForm, self).__init__(*args, **kwargs)
    #     #Reference db to get names of all documents uploaded
    #     # self.documents.choices = [(i, i) for i in range(1, now.day + 1)]


