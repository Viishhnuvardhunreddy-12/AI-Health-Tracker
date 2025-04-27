from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, SelectField, SubmitField, StringField, PasswordField, BooleanField, TelField
from wtforms.validators import DataRequired, NumberRange, Length, Regexp, Email, EqualTo, ValidationError, Optional
from app.models import User

class VitalsForm(FlaskForm):
    name = StringField('Your Name', 
                      validators=[DataRequired(), 
                                 Length(min=2, max=50, 
                                       message="Name should be between 2-50 characters")])
    
    email = StringField('Email Address',
                        validators=[DataRequired(),
                                   Email(message="Please enter a valid email address")])
    
    phone = TelField('Phone Number (for SMS notifications)',
                    validators=[Optional(),
                               Regexp(r'^\+?[0-9]{10,15}$', 
                                     message="Please enter a valid phone number")])                                   
    
    heart_rate = IntegerField('Heart Rate (BPM)', 
                             validators=[DataRequired(), 
                                        NumberRange(min=40, max=220, 
                                                   message="Heart rate should be between 40-220 BPM")])
    
    sleep_hours = FloatField('Sleep Hours', 
                            validators=[DataRequired(), 
                                       NumberRange(min=0, max=24, 
                                                  message="Sleep hours should be between 0-24")])
    
    steps = IntegerField('Steps Today', 
                        validators=[DataRequired(), 
                                   NumberRange(min=0, max=100000, 
                                              message="Steps should be between 0-100,000")])
    
    mood = SelectField('Current Mood', 
                      choices=[
                          ('1', 'Very Poor'),
                          ('2', 'Poor'),
                          ('3', 'Neutral'),
                          ('4', 'Good'),
                          ('5', 'Excellent')
                      ],
                      validators=[DataRequired()])
    
    submit = SubmitField('Record Vitals')

# Login form
class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# Registration form
class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                         validators=[DataRequired(), 
                                    Length(min=3, max=64),
                                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must start with a letter and can only contain letters, numbers, dots or underscores')])
    
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    name = StringField('Full Name', 
                      validators=[DataRequired(), 
                                 Length(min=2, max=64)])
    
    phone = TelField('Phone Number (for SMS notifications)',
                    validators=[Optional(),
                               Regexp(r'^\+?[0-9]{10,15}$', 
                                     message="Please enter a valid phone number")])
    
    password = PasswordField('Password', 
                            validators=[DataRequired(), 
                                       Length(min=8, message='Password must be at least 8 characters long')])
    
    password2 = PasswordField('Confirm Password', 
                             validators=[DataRequired(), 
                                        EqualTo('password', message='Passwords must match')])
    
    submit = SubmitField('Register')
    
    # Custom validators
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken. Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered. Please use a different email address.')

# Profile form
class ProfileForm(FlaskForm):
    name = StringField('Full Name', 
                      validators=[DataRequired(), 
                                 Length(min=2, max=64)])
    
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    phone = TelField('Phone Number (for SMS notifications)',
                    validators=[Optional(),
                               Regexp(r'^\+?[0-9]{10,15}$', 
                                     message="Please enter a valid phone number")])
    
    password = PasswordField('New Password (leave blank to keep current)', 
                            validators=[Optional(), 
                                       Length(min=8, message='Password must be at least 8 characters long')])
    
    password2 = PasswordField('Confirm New Password', 
                             validators=[EqualTo('password', message='Passwords must match')])
    
    submit = SubmitField('Update Profile')