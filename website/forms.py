from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from website.models import user_tbl
import re


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()],
                           render_kw={'class': 'inputLine', 'autocomplete': 'off', 'id': 'ru7_input'})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={'id': 'ru11_input'})
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired()], render_kw={'id': 'c_u11_input'})
    email = StringField('Email address', validators=[Email()], render_kw={'id': 'email_u11_input'})
    age = IntegerField('Age', validators=[InputRequired()], render_kw={'id': 'age_u11_input'})
    location = StringField('Location', render_kw={'id': 'location_u11_input'})
    submit = SubmitField('Register')

    def run_validation(self, username, email, password, confirm_password, age):
        def checkfor_username(username):
            user = user_tbl.query.filter_by(username=username.data).first()
            if user is not None:
                return False
            else:
                return True

        def checkfor_email(email):
            user = user_tbl.query.filter_by(email=email.data).first()
            if user is not None:
                return False
            else:
                return True

        def check_passwordlength(password):
            if len(password.data) >= 8 and len(password.data) <= 64:
                return True
            else:
                return False

        def validate_password(password):
            regex_options = '^(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[@$!%*?&#^()])[A-Za-z\d@$!%*?&#^()]{8,}$'
            if re.search(regex_options, password.data):
                return True
            else:
                return False

        def check_confirmpassword(password, confirm_password):
            if confirm_password.data == password.data:
                return True
            else:
                return False

        def validate_age(age):
            if age.data < 13:
                return False
            else:
                return True

        errormsg = 'False'
        if checkfor_username(username):
            if checkfor_email(email):
                if check_passwordlength(password):
                    if validate_password(password):
                        if check_confirmpassword(password, confirm_password):
                            if validate_age(age):
                                error = False
                            else:
                                errormsg = "Must be at least 13 to register!"
                        else:
                            errormsg = "Confirm password does not match with password!"
                    else:
                        errormsg = "Password must have at least an upper, a lower and a special character!"
                else:
                    errormsg = "Password must be between 8 and 45 characters!"
            else:
                errormsg = "Email already registered!"
        else:
            errormsg = "Username already taken!"

        if errormsg != 'False':
            return errormsg
        else:
            return "No error"


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()], render_kw={'id': 'u7_input'})
    password = PasswordField('Password', validators=[InputRequired()], render_kw={'id': 'u11_input'})
    submit = SubmitField('Login')


class SearchForm(FlaskForm):
    search_username = StringField('Search_username', validators=[InputRequired()])
    search = SubmitField('Search')
    add = SubmitField('Add')


class RecordUpdateForm(FlaskForm):
    """
    Form for updating the user details
    """
    username_up = StringField('Update_Up', validators=[InputRequired()],
                              render_kw={'class': 'inputLine', 'autocomplete': 'off', 'placeholder': 'Username'})
    password = PasswordField('Password',
                             validators=[InputRequired()],
                             render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm_Password', validators=[InputRequired(), EqualTo('password')],
                                     render_kw={'placeholder': 'Confirm Password'})
    email = StringField('Email', validators=[InputRequired()],
                        render_kw={'class': 'inputLine', 'autocomplete': 'off', 'placeholder': 'Email'})
    age = StringField('Age', validators=[InputRequired()],
                      render_kw={'class': 'inputLine', 'autocomplete': 'off', 'placeholder': 'Age'})
    location = StringField('Location', validators=[InputRequired()],
                           render_kw={'class': 'inputLine', 'autocomplete': 'off', 'placeholder': 'Location'})
    submit2 = SubmitField('Update')

    def checkfor_username(self, username):
        if current_user.username == username.data:
            return True
        else:
            user = user_tbl.query.filter_by(username=username.data).first()
            if user is not None:
                return False
            else:
                return True

    def password_length_settings(self, password):
        if len(password.data) > 8:
            return True
        else:
            return False
