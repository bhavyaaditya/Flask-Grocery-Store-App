from flask import Flask, request, redirect, url_for, flash, send_from_directory
from flask import render_template as rt
from app import app
from app import db
import os, sys, copy
import datetime as dt
from werkzeug.utils import secure_filename
from model import *
from PIL import Image
from forms import *
import sqlite3 as sq


#*----------------------------------------- RESOURCES ----------------------------------------------------


def cats():
    #cats_returnVal = Categories.query.order_by(Categories.cat_name).all()
    return Categories.query.order_by(Categories.cat_name).all() #cats_returnVal

def items():
    #items_returnVal = Items.query.order_by(Items.item_name).all()
    return Items.query.order_by(Items.item_name).all() #items_returnVal

def item_types():
    #item_types_returnVal = Item_type.query.all()
    return Item_type.query.all() #item_types_returnVal

def orders():
    #orders_returnVal = Orders.query.all()
    return Unique_orders.query.all() #orders_returnVal

def orders_count():
    #orders_count_returnVal = Orders.query.count() if Orders.query.count() > 0 else None
    return Unique_orders.query.count() if Unique_orders.query.count() > 0 else None #orders_count_returnVal

def orders_total():
    uniqueOrders_ = Unique_orders.query.all()
    orderGrandTotal = 0
    for row in uniqueOrders_:
        orderGrandTotal += row.order_total
    return orderGrandTotal

def item_cat():
        
    cats_funcUseVal = cats()
    item_types_funcUseVal = item_types()

    item_cat_returnVal = {} # Dictionary with categories and corresponding products

    # Initializing item_cat
    for cat in cats_funcUseVal:
        item_cat_returnVal[cat.cat_id] = [cat.cat_name,{}]
    # Filling item_cat
    for cat in cats_funcUseVal:
        for it in item_types_funcUseVal:
            if it.cat_id == cat.cat_id:
                prod = Items.query.get(it.item_id)
                item_cat_returnVal[cat.cat_id][1][it.item_id] = [
                                                                    prod.item_name,
                                                                    prod.item_unit,
                                                                    prod.item_price,
                                                                    prod.item_desc,
                                                                    prod.item_max_units_per_user
                                                                ]
    
    return item_cat_returnVal

def user_display_dict():
    user_display_dict_returnVal = item_cat()
    for i in user_display_dict_returnVal.keys(): # Loop to limit no. of products to be displayed to 5
        if len(user_display_dict_returnVal[i][1].keys()) > 5: # Check if the category has more than 5 products
            keyList = []
            for k in user_display_dict_returnVal[i][1].keys():
                keyList.append(k)
            for j in keyList[5:]: # Keep just 5 products and remove the rest
                user_display_dict_returnVal[i][1].pop(j)
    return user_display_dict_returnVal


# cats, items, item_types, and item_cat look like:
'''
cats = [(1,Dairy), (2,Veggies)]

items = [(1,amul milk 200 ml packet), (2,gobhi (grams)), (3,paneer 100 grams packet)]

item_types = [(1,1), (2,2), (3,1)]

item_cat = {
    1: [
        'Dairy',
            {
                1: [
                    'amul milk 200 ml packet',      # Product Name
                    'packet of 100gm',              # Product Unit
                    5,                              # Product Price
                    'Shelf life 3 days'             # Product Description
                    ],
                3: ['paneer 100 grams packet', 'packet of 100 gm', 15, 'shelf life 10 days']
            }
        ], 
    2: [
        'Veggies', 
            {
                2: ['gobhi (grams)', '100 gm', 20, 'Organic cauliflower with 4 day shelf life']
            }
        ]
    }
item_cat = {
    cat_id: [
        'cat_name',
            {
                item_id: [
                            item_name,
                            item_unit,
                            item_price,
                            item_desc,
                            item_max_units_per_user
                            ], 
                item_id: [item_name, item_unit, item_price, item_desc, item_max_units_per_user]
            }
        ], 
    cat_id: [
        'cat_name', 
            {
                item_id: [item_name, item_unit, item_price, item_desc, item_max_units_per_user]
            }
        ]
    }
'''




#*----------------------------------------- USER ROUTES ------------------------------------------------

@app.route('/user_signup/', methods=['GET','POST'])
def user_signup():
    form = SignupForm()
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        firstname = request.form['firstname']
        midname = request.form['midname']
        lastname = request.form['lastname']
        city = request.form['city']
        pincode = request.form['pincode']
        address = request.form['address']
        user = Users(
            user_email = email,
            user_password = password,
            user_username = username,
            user_firstname = firstname,
            user_midname = midname,
            user_lastname = lastname,
            user_city = city,
            user_pincode = pincode,
            user_address = address
        )
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.rollback()
            return redirect(url_for('user_signup'))
    return rt('user_signup.html',form=form)

@app.route('/home/',methods=['GET','POST'])
@app.route('/index/', methods=['GET','POST'])
@app.route('/user_login/',methods=['GET','POST'])
@app.route('/',methods=['GET','POST'])
def index():
    form = LoginForm()
    if request.method=="POST":        
        username = request.form['username']
        password = request.form['password']
        user = Users.query.filter_by(user_username = username).first_or_404("No such username")
        #print(user.user_username)
        #print(username, password)
        if username == user.user_username and password == user.user_password:
            return redirect(url_for('user_home', userID=user.user_id))

    return rt('user_login.html', form = form)

@app.route('/user_home/<int:userID>/', methods=['GET','POST'])
def user_home(userID):
    user = Users.query.get(userID)
    user_display_dict_ = user_display_dict()

    search = searchForm()
    if request.method=='POST':
        q = request.form['searchQ']
        return redirect(url_for('search',userID=userID, q=q))

    return rt('user_home.html', userID=userID, user=user, user_display_dict=user_display_dict_, search=search)

@app.route('/view_category/<int:userID>/<int:catID>/', methods = ['GET', 'POST'])
def view_category(userID, catID):
    user = Users.query.get(userID)
    itemCat = item_cat()

    return rt('view_category.html', userID=userID, user=user, itemCat=itemCat, catID=catID)


@app.route('/buy_product/<int:userID>/<int:itemID>/', methods=['GET','POST'])
def buy_product(userID, itemID):

    user = Users.query.get(userID)

    filename = str(itemID)+'.jpg'
    product_img_path = url_for('static',filename=f'uploads/{itemID}.jpg') 
    #os.path.join('..\\'+app.config['UPLOAD_FOLDER'], filename) 
    # '../assets/uploads/'+filename 
    
    item = Items.query.get(itemID)
    
    # Maximum qty which user can buy
    max_qty=None
    if item.item_qty_avail == 0:                                # If product is out of stock
        max_qty = 0
    elif item.item_max_units_per_user <= item.item_qty_avail:   # If available stock is more than user's purchase limit
        max_qty = item.item_max_units_per_user
    else:                                                       # If available stock is less than user's purchase limit
        max_qty = item.item_qty_avail
    
    # Quantity field to add product to cart
    class Product_purchase(FlaskForm):
        qty_field = IntegerField(label='Quantity: ', validators=[NumberRange(0,max_qty)])
        add_to_cart = SubmitField(label='Add to Cart')
    form  = Product_purchase()
    
    # Proceeding to cart
    if request.method=='POST':
        qty = request.form['qty_field']
        qty = int(qty)
        alreadyCarted = False
        userCart = Carts.query.filter_by(cart_userID = userID).all()

        # Check if product is already in cart
        for row in userCart:
            if row.cart_itemID == itemID:
                alreadyCarted = True
                break
        
        if alreadyCarted==True:
            try:
                cartValue = Carts.query.filter_by(cart_userID = userID, cart_itemID = itemID).first()
                cartValue.cart_qty = qty
                db.session.commit()
                print("Item already in cart. Quantity updated")
            except Exception as e:
                db.session.rollback()
                print('error in carting: ',e)
            return redirect(url_for('cart',userID=userID))
        elif alreadyCarted==False:
            try:
                cartValue = Carts(cart_userID = userID, cart_itemID = itemID, cart_qty = qty)
                db.session.add(cartValue)
                db.session.commit()
                print('Item added to cart!')
            except Exception as e:
                db.session.rollback()
                print('Some error: ',e)
            return redirect(url_for('cart',userID=userID))

    return rt('buy_product.html', itemID = itemID, product_img_path = product_img_path, item=item, form=form, max_qty=max_qty, userID=userID, user=user)

@app.route('/search/<int:userID>/<string:q>/')
def search(userID,q):
    query = '%'+q+'%'
    searchItems = Items.query.filter(Items.item_name.like(query)).all() # List of results of items. First results are added by matching item names, then by matching description
    searchItemsDesc = Items.query.filter(Items.item_desc.like(query)).all() 

    # Loop to add products whose description matches search criteria to the results list
    for stuff in searchItemsDesc:
        if stuff not in searchItems:
            searchItems.append(stuff)

    searchCategories = Categories.query.filter(Categories.cat_name.like(query)).all() # List of search results of categories.

    searchItems_len = len(searchItems)
    searchCategories_len = len(searchCategories)

    user = Users.query.get(userID)

    return rt('search_results.html', searchItemsDesc=searchItemsDesc, searchCategories=searchCategories, userID=userID, searchItems=searchItems, searchCategories_len=searchCategories_len, searchItems_len=searchItems_len, user=user)


@app.route('/cart/<int:userID>/', methods=['GET','POST'])
def cart(userID):
    

    user = Users.query.get(userID) # Current user
    buy = cart_buy()

    cart_dict = {}          # Dictionary of products in cart
    cart_dict_keys = []

    userCart = Carts.query.filter_by(cart_userID = userID).all() # Current user's cart entries in db
    print('userCart = ',userCart, 'type = ', type(userCart), 'len = ',len(userCart))
    cart_total = 0
    for row in userCart:
        print('row = ', row, type(row))
        itemID = row.cart_itemID
        item = Items.query.get(itemID)
        cart_dict_keys.append(itemID)
        cart_dict[itemID] = [
                            item.item_name,
                            row.cart_qty,
                            item.item_unit,
                            item.item_price,
                            (row.cart_qty * item.item_price)
                            ]
        cart_total += (row.cart_qty * item.item_price)

    # Examples of cart_dict, cart_dict_keys for userID=1
    '''   
    cart_dict = {
                    item_id (cart_items[i]): [
                                                item_name,
                                                qty carted by user (cart_qty[i]),
                                                item_unit,
                                                item_price,
                                                product total (cart_qty[i] * item_price)
                    ]
    }
                
    cart_dict =  {
                    1: [
                        'amul milk 200 ml packet', 
                        12, 
                        'packet of 200 ml', 
                        15, 
                        180
                        ], 
                    2: [
                        'gobhi (grams)', 
                        4, 
                        '100 gm', 
                        50, 
                        200
                        ]
                    }
    '''

    # * Placing order from cart
    if request.method == 'POST' and len(cart_dict_keys)>0: # Check if order is being placed and the cart is not empty 
        
        orderID = Latest_order.query.get(1).order_id + 1
        timestamp = dt.datetime.now()
        timestamp = dt.datetime.timestamp(timestamp)
        date_time = dt.datetime.fromtimestamp(timestamp)
        str_date_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")
        order_grandTotal = 0
        
        try:
            # Loop to make entries in order table
            for row in userCart:
                item = Items.query.get(row.cart_itemID)
                orderRow = Orders(
                                    order_id = orderID,
                                    order_userID = userID,
                                    order_itemID = row.cart_itemID,
                                    order_qty = row.cart_qty,
                                    order_price = item.item_price,
                                    order_time = timestamp,
                                    order_total = (row.cart_qty * item.item_price),
                                    order_unit = item.item_unit,
                                    order_itemName = item.item_name
                )
                db.session.add(orderRow)
                item.item_qty_avail -= row.cart_qty # Reducing the product's stock once the order is placed
                print('row added, commit waited')
                order_grandTotal += (row.cart_qty * item.item_price)
            
            # Update unique_orders table
            uniqueOrder = Unique_orders(order_id = orderID, user_id = userID, order_total = order_grandTotal, order_time = timestamp)
            db.session.add(uniqueOrder)

            # Update latest_order
            Latest_order.query.get(1).order_id = orderID
            Latest_order.query.get(1).user_id = userID

            # Emptying the user's cart
            for row in userCart:
                db.session.delete(row)

            db.session.commit()
            print('order successfull')
            return redirect(url_for('order_summary', userID=userID, orderID = orderID))
        
        except Exception as e:
            print('error in placing order: ',e)
            return redirect(url_for('user_home', userID=userID))

    cart_dict_keys_len = len(cart_dict_keys)
    return rt('cart.html', userID=userID,
               cart_dict=cart_dict,
               cart_dict_keys=cart_dict_keys,
               cart_total=cart_total,
               buy=buy,
               user=user,
               cart_dict_keys_len=cart_dict_keys_len
               )


# Delete item from cart
@app.route('/deleteFromCart/<int:userID>/<int:itemID>/', methods=['GET','POST'])
def deleteFromCart(userID, itemID):
    user=Users.query.get(userID)
    itemName = Items.query.get(itemID).item_name
    cartEntry = Carts.query.filter(Carts.cart_userID==userID, Carts.cart_itemID==itemID).first()
    if request.method=='POST':
        try:
            db.session.delete(cartEntry)
            db.session.commit()
            print('Product deleted from cart')
        except Exception as e:
            db.session.rollback()
            print('Error: ',e)
        finally:
            return redirect(url_for('cart', userID=userID))
    return rt('deleteItemFromCart.html', user=user, userID=userID, itemID=itemID, itemName=itemName)


# Details of an order
@app.route('/order_summary/<int:userID>/<int:orderID>/')
def order_summary(userID, orderID):
    
    user = Users.query.get(userID) # Current user
    uniqueOrder = Unique_orders.query.get(orderID)
    order = Orders.query.filter_by(order_id=orderID).all()
    
    orderTime = dt.datetime.fromtimestamp(uniqueOrder.order_time)
    orderTime = orderTime.strftime("%d-%m-%Y, %H:%M:%S")
    

    return rt('order_summary.html', userID=userID, orderID=orderID, uniqueOrder=uniqueOrder, order=order, user=user, Items=Items, orderTime=orderTime)


# View list of user's orders
@app.route('/user_orders/<int:userID>/')
def user_orders(userID):
    user = Users.query.get(userID)
    uniqueOrders_query = Unique_orders.query.filter_by(user_id = userID).all()
    uniqueOrders = {}
    for row in uniqueOrders_query:
        orderTime = dt.datetime.fromtimestamp(row.order_time)
        orderTime = orderTime.strftime("%d-%m-%Y, %H:%M:%S")
        uniqueOrders[row.order_id] = [
                        orderTime,
                        row.order_total
        ]

    return rt('user_orders.html', userID=userID, user=user, uniqueOrders=uniqueOrders)



#*----------------------------------------- MANAGER ROUTES ------------------------------------------------


@app.route('/admin_login/', methods=['GET','POST'])
def admin_login():
    form = LoginForm()
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        mngr = Managers.query.filter_by(mngr_username = username).first_or_404("No such username!")
        if username==mngr.mngr_username and password==mngr.mngr_password:
            return redirect(url_for('manager_home', mngrID = mngr.mngr_id))
    return rt('admin_login.html', form = form)


# Manager/Admin dashboard
@app.route('/manager_home/<int:mngrID>',methods=['GET','POST'])
def manager_home(mngrID):
    mngr = Managers.query.get(mngrID)
    stockOver = Items.query.filter(Items.item_qty_avail==0).all()
    stockOver_len = len(stockOver)
    lowStock = Items.query.filter(Items.item_qty_avail <= Items.item_max_units_per_user).all()
    for stuff in lowStock:              # Remove out of stock items
        if stuff in stockOver:
            lowStock.remove(stuff)
    lowStock_len = len(lowStock)
    orders_= orders()
    order_count_=orders_count()
    order_total=orders_total()
    items_=items()
    cats_=cats()
    item_cat_=item_cat()
    return rt('manager_home.html', orders=orders_,
                                    order_count=order_count_,
                                    order_total=order_total,
                                    items=items_,
                                    cats=cats_,
                                    item_cat=item_cat_,
                                    mngr=mngr,
                                    mngrID=mngrID,
                                    stockOver=stockOver,
                                    lowStock=lowStock,
                                    stockOver_len=stockOver_len,
                                    lowStock_len=lowStock_len)


# Function to edit product  
@app.route('/edit_product/<int:mngrID>/<int:itemID>/',methods=['GET','POST'])
def edit_product(mngrID,itemID):
    mngr = Managers.query.get(mngrID)
    form = edit_product_form()
    product_img_path = url_for('static',filename=f'uploads/{itemID}.jpg')
    item = Items.query.get(itemID)
    img_edit_url = url_for('item_img',itemid=itemID, mngrID=mngrID )

    if request.method == "POST":
        name = request.form['name']
        unit = request.form['unit']
        qty_avail = int(request.form['qty_avail'])
        price = int(request.form['price'])
        max_units = int(request.form['max_units'])
        desc = request.form['desc'] 

        try:
            # Check for edits made via form and commit to db
            if name != item.item_name:
                item.item_name = name
            if unit != item.item_unit:
                item.item_unit = unit
            if qty_avail != item.item_qty_avail:
                item.item_qty_avail = qty_avail
            if price != item.item_price:
                item.item_price = price
            if max_units != item.item_max_units_per_user:
                item.item_max_units_per_user = max_units
            db.session.commit()
            print('Product edited successfully')
        except Exception as e:
            print('Product not edited. Error: ',e)
        
        return redirect(url_for('manager_home',mngrID=mngrID)) # todo check which manager logged in
    return rt('edit_product.html',mngrID=mngrID,itemID=itemID, form=form, product_img_path=product_img_path, item=item, img_edit_url=img_edit_url, mngr=mngr)


# Edit product image
@app.route('/item_img/<int:mngrID>/<int:itemid>/', methods=['GET','POST'])
def item_img(mngrID,itemid):
    mngr = Managers.query.get(mngrID)
    item = Items.query.get(itemid)
    form = Image_upload()
    filename = None
    if request.method=='POST':
        file = request.files['img_field']
        filename = str(itemid)+'.jpg'
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('manager_home',mngrID=mngrID))

    return rt('item_img.html',mngrID=mngrID, mngr=mngr, form=form,item=item, itemid=itemid)

# Create New Product
@app.route('/create_product/<int:mngrID>/', methods=['GET','POST'])
def create_product(mngrID):
    mngr = Managers.query.get(mngrID)
    form = new_productForm()
    if request.method == 'POST':
        # New item element to be added to db
        new_item = Items(
            item_name = request.form['name'],
            item_qty_avail = int(request.form['qty_avail']),
            item_price = int(request.form['price']),
            item_desc = request.form['desc'],
            item_unit = request.form['unit'],
            item_max_units_per_user = int(request.form['max_units'])
        )
        
        try:
            db.session.add(new_item)
            db.session.commit()
            print('product created successfully')
            return redirect(url_for('item_img', mngr=mngr, mngrID=mngrID, itemid = new_item.item_id))
        except Exception as e:
            db.session.rollback()
            print('unable to create product')
            print('error: ',e)
            return redirect(url_for('create_product',mngrID=mngrID, mngr=mngr))
        
    return rt('create_product.html',mngrID=mngrID, form=form, mngr=mngr)


# Edit category
@app.route('/edit_category/<int:mngrID>/<int:catID>/', methods=['GET','POST'])
def edit_category(mngrID,catID):
    mngr = Managers.query.get(mngrID)
    thisCat = Categories.query.get(catID)
    items_thisCat_ = Item_type.query.filter(Item_type.cat_id==catID).all()
    items_thisCat = {}
    items_thisCat_keys = []
    it = None
    
    for item in items_thisCat_: 
        it = Items.query.filter_by(item_id=item.item_id).first()
        items_thisCat_keys.append(it.item_id)
        items_thisCat[item.item_id]=[
                                it.item_name,
                                it.item_qty_avail,
                                it.item_max_units_per_user,
                                int(it.item_price)
                            ]
    print(items_thisCat)
    
    change_name = edit_category_name()

    if request.method=='POST':
        new_name = request.form['name']
        try:
            thisCat.cat_name = new_name
            db.session.commit()
            #updateResources()
            print('Category name changed')
            return redirect(url_for('manager_home',mngrID=mngrID, mngr=mngr)) # todo when login, check which manager
        except:
            db.session.rollback()
            print('Unable to change category name')


    return rt('edit_category.html',
              mngrID=mngrID, 
              catID=catID, 
              thisCat=thisCat, 
              change_name=change_name, 
              items_thisCat=items_thisCat, 
              items_thisCat_keys=items_thisCat_keys,
              mngr=mngr)


# Add Item to Category
@app.route('/add_item_to_category/<int:mngrID>/<int:catID>/', methods=['GET','POST'])
def add_item_to_category(mngrID,catID):
    mngr = Managers.query.get(mngrID)
    items_ = items()
    cat_name = Categories.query.filter_by(cat_id=catID).first().cat_name  # Name of this category
    not_inCat = {} # Products not in this category which can be added
    thisCat = Categories.query.get(catID)   # This category
    #print('thisCat = ',thisCat)
    items_thisCat_ = Item_type.query.filter(Item_type.cat_id==catID).all()  # # All item_type combos of this category
    #print('items_thisCat_ = ',items_thisCat_)
    items_thisCat_keys = [] # IDs of all items in this category
    for i in items_thisCat_:
        items_thisCat_keys.append(i.item_id)
    #print('items_thisCat_keys = ',items_thisCat_keys)
    for it in items_:    # Filling not_inCat with all items
        not_inCat[it.item_id] = [
                                it.item_name,
                                it.item_qty_avail,
                                it.item_max_units_per_user,
                                int(it.item_price)
        ]
    #print('not_inCat before = ', not_inCat)
    for i in items_thisCat_keys:    # Removing items which are already in this category
        not_inCat.pop(i)
    #print('not_inCat final = ',not_inCat)

    to_be_added = {}
    to_be_added_keys = []
    if request.method=='POST':
        checkList = request.form.getlist('addToCat')    # IDs of all items which admin wants to add to this category, received as a list of strings (to be converted to int) via form
        #print(checkList)
        #print(len(checkList))
        if len(checkList) > 0:
            for sub in checkList:
                sub = int(sub)
                to_be_added[sub] = Item_type(item_id = sub,cat_id = catID)
                #print('sub ',sub, type(sub))
                #print(Item_type(item_id = sub,cat_id = catID))
                #print(type(Item_type(item_id = sub,cat_id = catID)))
                try:
                    db.session.add(to_be_added[sub])
                    db.session.commit()
                    print('Committed ', to_be_added[sub])
                except:
                    db.session.rollback()
                    print('Could not add: ', to_be_added[sub])
                    continue

            return redirect(url_for('edit_category', mngr=mngr, mngrID=mngrID,catID=catID))

        else:
            print('Nothing submitted')
    return rt('add_item_to_category.html',
              mngr=mngr,
              mngrID=mngrID,
              catID=catID,
              not_inCat=not_inCat,
              cat_name=cat_name
              )

# Delete Item From Category
@app.route('/delete_item_from_category/<int:mngrID>/<int:catID>/<int:itemID>/', methods=['GET','POST'])
def delete_item_from_category(mngrID,catID,itemID):
    mngr = Managers.query.get(mngrID)
    item = Items.query.get(itemID)
    cat = Categories.query.get(catID)
    item_type = Item_type.query.filter_by(cat_id=catID).filter_by(item_id=itemID).first()

    if request.method=='POST':
        try:
            db.session.delete(item_type)
            db.session.commit()
            #updateResources()
            '''global cats, items, item_types
            cats = Categories.query.order_by(Categories.cat_name).all()
            items = Items.query.order_by(Items.item_name).all()
            item_types = Item_type.query.all()'''
            print('product deleted from category successfully')
        except:
            db.session.rollback()
            print('unable to delete product from category')
        return redirect(url_for('edit_category', mngr=mngr, mngrID=mngrID,catID=catID))

    return rt('delete_item_from_category.html', mngr=mngr, mngrID=mngrID, catID=catID, itemID=itemID, item=item, cat=cat, item_type=item_type)


# Delete Product
@app.route('/delete_product/<int:mngrID>/<int:itemID>/', methods=['GET','POST'])
def delete_product(mngrID,itemID):
    mngr = Managers.query.get(mngrID)
    item = Items.query.get(itemID) # Item to be deleted
    itemsCat = Item_type.query.filter_by(item_id = itemID).all() # Item_type entries to be deleted
    itemCart = Carts.query.filter_by(cart_itemID = itemID).all() 
    if request.method=="POST":
        try:
            db.session.delete(item)
            for stuff in itemsCat:              # Deleting the item from item_types
                db.session.delete(stuff)
            for rec in itemCart:                
                db.session.delete(rec)          
            db.session.commit()
            print('Product deleted successfully')
        except Exception as e:
            db.session.rollback()
            print('Unable to delete product')
            print('Error: ', e)
        return redirect(url_for('manager_home', mngr=mngr, mngrID=mngrID))

    return rt('delete_product.html', mngr=mngr,mngrID=mngrID, itemID=itemID, item=item)


# Delete Category
@app.route('/delete_category/<int:mngrID>/<int:catID>/', methods=['GET','POST'])
def delete_category(mngrID,catID):
    mngr = Managers.query.get(mngrID)
    cat = Categories.query.get(catID)
    cat_products = Item_type.query.filter_by(cat_id=catID).all()
    if request.method == 'POST':
        try:
            db.session.delete(cat)
            for stuff in cat_products:
                db.session.delete(stuff)
            db.session.commit()
            #updateResources()
            print('deleted category successfully')
        except:
            db.session.rollback()
            print('some error in delteing category')
        return redirect(url_for('manager_home',mngr=mngr, mngrID=mngrID))
    return rt('delete_category.html', mngr=mngr, mngrID=mngrID,catID=catID, cat=cat)


# Create New Category
@app.route('/create_category/<int:mngrID>/', methods=['GET','POST'])
def create_category(mngrID):
    mngr = Managers.query.get(mngrID)
    form = new_categoryForm()
    if request.method=='POST':
        new_cat = Categories(cat_name = request.form["category_name"])
        try:
            db.session.add(new_cat)
            print(new_cat.cat_id)
            db.session.commit()
            #updateResources()
            print('category created: ', new_cat, new_cat.cat_id, new_cat.cat_name)
        except:
            db.session.rollback()
            print('unable to create category')
        return redirect(url_for('manager_home',mngr=mngr, mngrID=mngrID)) # todo while login, check which manager is logging in
    return rt('create_category.html',mngrID=mngrID, mngr=mngr,form=form)

# Analytics
@app.route('/analytics/<int:mngrID>/', methods=['GET','POST'])
def analytics(mngrID):
    mngr = Managers.query.get(mngrID)
    cur = None
    labels_itemSales,data_itemSales = [],[]
    #catSalesDict = {}
    catSales = [] # Sorted list of categories with their sales as tuples like [(cat_id, cat_name, cat_sales)]
    labels_catSales, data_catSales = [],[]
    
    order_count=orders_count()
    order_total=orders_total()
    user_count = 0
    for i in Users.query.all():
        user_count += 1
    avg_orderValue = round(order_total/order_count, 2)
    avg_salePerUser = round(order_total/user_count, 2)
    avg_ordersPerUser = round(order_count/user_count, 2)
    
    try:
        conn = sq.connect('appdb.db')
        print('Connection successful')
        cur = conn.cursor()
        print('cursor established')
    except Exception as e:
        print(e)

    if cur != None:
        queryItemSales = '''
        select order_itemID, sum(order_total) as ot from orders group by order_itemID order by sum(order_total) DESC;
        '''
        cur.execute(queryItemSales)
        itemSales = cur.fetchall() # type(itemSales) = <class 'list'>
        print('itemSales type = ',type(itemSales), type(itemSales[0]))


        cur.close()
        conn.close()

        
        for i in itemSales:
            labels_itemSales.append(f'{Items.query.get(i[0]).item_name} (ID: {i[0]})')
            data_itemSales.append(i[1])

        if len(data_itemSales)>5:                       # Limit pie chart to top 5 products
            labels_itemSales = labels_itemSales[0:5]
            data_itemSales = data_itemSales[0:5]
        
        itemCat = item_cat()
        for cat in itemCat:
            '''catSalesDict[cat] = {
                                    'cat_name':itemCat[cat][0],
                                    'cat_sales':0
                                }'''
            cat_sale = 0
            
            for it in itemCat[cat][1]:   # itemCat[cat][1] iterates through all items (item_id) in category
                for ot in itemSales:
                    if it==ot[0]:
                        #catSalesDict[cat]['cat_sales'] += ot[1]
                        cat_sale += ot[1]
                        break
            tup = (cat, itemCat[cat][0],cat_sale)          # tup = (cat_id, cat_name, cat_sales)
            catSales.append(tup)
        
        catSales.sort(key = lambda tup: tup[2], reverse=True)

        for tup in catSales:
            labels_catSales.append(f'{tup[1]} (ID: {tup[0]})')
            data_catSales.append(tup[2])
        
        if len(data_catSales) > 5:          # Limit to top 5 categories
            labels_catSales = labels_catSales[0:5]
            data_catSales = data_catSales[0:5]

        '''
        # Example of itemSales:
        # itemSales = [(3, 150), (1, 90), (6, 60), (4, 20)]
        # type(itemSales[0]) = <class 'tuple'>
        
        # Example of catSales:
        # [(2, 'Dairy', 150), (1, 'Biscuits', 90), (5, 'Sweets', 60), (3, 'Vegetables', 20)]
        # type(catSales[0]) = <class 'tuple'>
        '''

    return rt('analytics.html', mngrID=mngrID, 
                                mngr=mngr, 
                                itemSales=itemSales, 
                                labels_itemSales=labels_itemSales, 
                                data_itemSales=data_itemSales, 
                                catSales=catSales, 
                                labels_catSales=labels_catSales, 
                                data_catSales=data_catSales,
                                order_count=order_count,
                                order_total=order_total,
                                user_count=user_count,
                                avg_orderValue = avg_orderValue,
                                avg_salePerUser = avg_salePerUser,
                                avg_ordersPerUser = avg_ordersPerUser)

