# encoding: utf-8

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class NewPivotForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create Pivot')

class NewGenericConsumerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create Consumer')


class NewGenericProducerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create Producer')

class NewGithubProducerForm(NewGenericProducerForm):
    # no differences yet with generic producer
    pass

class SignUpWithEmailForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=200)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(min=3, max=1000)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=1000)
        ])
    submit = SubmitField('Sign up for APIPivot')

class LoginWithEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[Optional(), Length(min=3, max=200)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[Optional(), Length(min=8, max=1000)])
    password2 = PasswordField('Password (confirm)', validators=[Optional(), EqualTo(password1)])
    submit = SubmitField('Update your account')
