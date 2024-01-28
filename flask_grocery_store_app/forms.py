from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileField, FileRequired

class LoginForm(FlaskForm):
    username = StringField(label='Username: ',validators=[DataRequired()])
    password = PasswordField(label='Password: ',validators=[DataRequired()])
    submit = SubmitField(label='Login')

class Image_upload(FlaskForm):
    img_field = FileField(label='Image Field',validators=[FileRequired()])
    img_submit = SubmitField(label='Submit Image')

class cart_buy(FlaskForm):
    buy = SubmitField(label = "Buy")

class edit_product_form(FlaskForm):
    name = StringField(label='Product Name')
    unit = StringField(label='Product Unit')
    qty_avail = IntegerField(label='Quantity in Stock',validators=[NumberRange(0)])
    price = IntegerField(label='Price Per Unit',validators=[NumberRange(0)])
    max_units = IntegerField(label='Maximum Units Purchasable Per Customer',validators=[NumberRange(0)])
    desc = StringField(label='Description')
    submit = SubmitField(label='Save Changes')

class edit_category_name(FlaskForm):
    name = StringField(label='Edit Category Name',validators=[DataRequired()])
    submit = SubmitField(label='Save Changes')

class new_categoryForm(FlaskForm):
    category_name = StringField(label='Category Name', validators=[DataRequired()])
    submit = SubmitField(label='Create Category')

class new_productForm(FlaskForm):
    name = StringField(label = 'Product Name', validators=[DataRequired()])
    qty_avail = IntegerField(label='Choose quantity in stock', validators=[DataRequired(),NumberRange(0)])
    unit = StringField(label='Enter product unit', validators=[DataRequired()])
    price = IntegerField(label='Product price', validators=[DataRequired(), NumberRange(0)])
    max_units = IntegerField(label='Max units purchasable by customer', validators=[DataRequired(),NumberRange(0)])
    desc = TextAreaField(label="Product description")
    submit = SubmitField(label='Create product and proceed to choose image')

class searchForm(FlaskForm):
    searchQ = SearchField(label='Looking for something?',validators=[DataRequired()])
    search = SubmitField(label='Search')

class SignupForm(FlaskForm):
    email = StringField(label='Email ID: ', validators=[DataRequired()])
    password = PasswordField(label='Password: ', validators=[DataRequired()])
    firstname = StringField(label='First Name: ', validators=[DataRequired()])
    midname = StringField(label='Middle Name: ')
    lastname = StringField(label='Last Name: ')
    username = StringField(label='Username: ', validators=[DataRequired()])
    city = StringField(label='City: ', validators=[DataRequired()])
    pincode = IntegerField(label='Pincode: ', validators=[DataRequired()])
    address = StringField(label='Address: ', validators=[DataRequired()])
    submit = SubmitField(label='Sign Up')