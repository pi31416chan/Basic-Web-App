from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    EmailField,
    PasswordField,
    SubmitField
)
from wtforms.validators import (
    Email,
    DataRequired,
    EqualTo,
    Length
)



# Form Definition
class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(
                min=6,
                max=30,
                message="Username must be minimum 6 and " +
                        "maximum 30 characters long"
            )
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(
                min=6,
                message="Password must be at least 6 characters long"
            )
        ]
    )
    submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(
                min=6,
                max=30,
                message="Username must be minimum 6 and " +
                        "maximum 30 characters long"
            )
        ]
    )
    email = EmailField(
        'Email Address',
        validators=[Email(),DataRequired(),Length(max=50)]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(
                min=6,
                message="Password must be at least 6 characters long"
            )
        ]
    )
    cfm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password','Input does not match with password'),
            Length(
                min=6,
                message="Password must be at least 6 characters long"
            )
        ]
    )
    submit = SubmitField('Submit')