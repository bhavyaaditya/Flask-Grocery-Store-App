from app import db
from sqlalchemy import CheckConstraint
from sqlalchemy.sql import func

class Users(db.Model):
    __tablename__ = 'users'
    user_id= db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    user_email= db.Column(db.String, nullable=False, unique=True)
    user_password= db.Column(db.String, nullable=False)
    user_username= db.Column(db.String, nullable=False, unique=True)
    user_firstname= db.Column(db.String, nullable=True)
    user_midname= db.Column(db.String)
    user_lastname= db.Column(db.String)
    user_city= db.Column(db.String, nullable=False)
    user_pincode= db.Column(db.Integer, nullable=False)
    user_address= db.Column(db.String)

    #def __repr__(self):
    #    return f'({self.user_id},{self.user_firstname.join({self.user_midname},{self.user_lastname})})'

class Managers(db.Model):
    __tablename__ = 'managers'
    mngr_id= db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    mngr_email= db.Column(db.String, nullable=False, unique=True)
    mngr_password= db.Column(db.String, nullable=False)
    mngr_username= db.Column(db.String, nullable=False, unique=True)
    mngr_firstname= db.Column(db.String, nullable=True)
    mngr_midname= db.Column(db.String)
    mngr_lastname= db.Column(db.String)
    #is_admin= db.Column(db.Boolean, default=False) # Check this once

    #def __repr__(self):
    #    return f'({self.mngr_id},{self.mngr_firstname.join(self.mngr_midname,self.mngr_lastname)},{self.is_admin})'

class Items(db.Model):
    __tablename__ = 'items'
    item_id= db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    item_name= db.Column(db.String, nullable=False, unique=True)
    item_qty_avail= db.Column(db.Integer, nullable=False)
    item_price= db.Column(db.Integer, nullable=False)
    item_desc= db.Column(db.String, nullable=False)
    item_unit = db.Column(db.String, nullable=False)
    item_max_units_per_user = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'({self.item_id},{self.item_name})'

class Categories(db.Model):
    __tablename__ = 'categories'
    cat_id= db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    cat_name= db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return f'({self.cat_id},{self.cat_name})'


class Item_type(db.Model):
    __tablename__ = 'item_type'
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), primary_key=True, nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('categories.cat_id'), primary_key=True, nullable=False)

    def __repr__(self):
        return f'({self.item_id},{self.cat_id})'

class Dummy(db.Model):
    __tablename__ = 'dummy'
    pk = db.Column(db.Integer, primary_key=True, autoincrement=True)
    img = db.Column(db.LargeBinary, nullable=False)

class Carts(db.Model):
    __tablename__ = 'carts'
    cart_rowID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cart_userID = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    cart_itemID = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False, unique=True)
    cart_qty = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'{self.cart_userID}, {self.cart_itemID}, {self.cart_qty}, {self.cart_rowID}'

class Orders(db.Model):
    __tablename__ = 'orders'
    order_rowID = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    order_id = db.Column(db.Integer, nullable=False)
    order_userID = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    order_itemID = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    order_qty = db.Column(db.Integer, nullable=False)
    order_price = db.Column(db.Integer, nullable=False)
    order_unit = db.Column(db.String, nullable=False)
    order_time = db.Column(db.Float())
    order_total = db.Column(db.Integer)
    order_itemName = db.Column(db.String)

    def __repr__(self):
        return f'{self.order_rowID},{self.order_id},{self.order_userID},{self.order_itemID},{self.order_qty},{self.order_price},{self.order_total}'
    
class Latest_order(db.Model):
    __tablename__ = 'latest_order'
    lo_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    order_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'{self.lo_id},{self.user_id},{self.order_id}'
    
class Unique_orders(db.Model):
    __tablename__ = 'unique_orders'
    order_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    order_total = db.Column(db.Integer)
    order_time = db.Column(db.Float())
    
    def __repr__(self):
        return f'{self.order_id},{self.user_id},{self.order_total}'