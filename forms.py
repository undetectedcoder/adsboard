from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField
from wtforms.validators import DataRequired, Length

class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=10)])
    password = PasswordField('Пароль', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])

class AdForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = StringField('Описание', validators=[DataRequired()])
    image = FileField('Фото')