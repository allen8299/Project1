from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
import imp
import random
import os
import string
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import current_app

UPLOAD_FOLDER = 'static/product'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

manager = Blueprint('manager', __name__, template_folder='../templates')


def config():
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config = current_app.config['UPLOAD_FOLDER']
    return config


@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('manager.bookManager'))


@manager.route('/bookManager', methods=['GET', 'POST'])
@login_required
def bookManager():
    if request.method == 'GET':
        if (current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))

    if 'delete' in request.values:
        bid = request.values.get('delete')
        data = Record.delete_check(bid)

        if (data != None):
            flash('failed')
        else:
            data = Product.get_product(bid)
            Product.delete_product(bid)

    elif 'edit' in request.values:
        bid = request.values.get('edit')
        return redirect(url_for('manager.edit', bid=bid))

    book_data = book()
    return render_template('bookManager.html', book_data=book_data, user=current_user.name)


def book():
    book_row = Book.get_all_book()
    book_data = []
    for i in book_row:
        theme_data = Theme.get_theme(i[6])
        category_data = Categories.get_categories(i[7])
        book = {
            '書籍編號': i[0],
            '書籍名稱': i[1],
            '出版社': i[2],
            '出版日期': i[3],
            '入庫日期': i[4],
            '作者': i[5],
            '書籍類別': category_data[1],
            '書籍主題': theme_data[1]
        }
        book_data.append(book)
    return book_data


@manager.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = ""
        while data != None:
            now = datetime.now()
            date_string = now.strftime("%Y%m%d%H%M%S")
            bid = 'B' + date_string
            data = Book.get_book(bid)

        bname = request.values.get('book_name')
        author = request.values.get('book_author')
        press = request.values.get('book_press')
        tmp_pdate = request.values.get('book_pdate')
        tmp_idate = request.values.get('book_idate')
        categoryid = request.values.get('book_category')
        themeid = request.values.get('book_theme')

        if (len(bname) < 1):
            return redirect(url_for('manager.bookManager'))

        # 不知道為何datepicker format沒有用
        # 將日期字串轉換為 datetime 物件
        date_obj = datetime.strptime(tmp_pdate, "%m/%d/%Y")
        # 將 datetime 物件轉換為字串
        pdate = date_obj.strftime("%Y-%m-%d")
        # 將日期字串轉換為 datetime 物件
        date_obj = datetime.strptime(tmp_idate, "%m/%d/%Y")
        # 將 datetime 物件轉換為字串
        idate = date_obj.strftime("%Y-%m-%d")

        print(bid, pdate, idate)
        Book.add_book(
            {'bid': bid,
             'bname': bname,
             'author': author,
             'press': press,
             'pdate': pdate,
             'idate': idate,
             'categoryid': categoryid,
             'themeid': themeid,
             }
        )

        return redirect(url_for('manager.bookManager'))

    return render_template('bookManager.html')


@manager.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        if (current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('library'))

    if request.method == 'POST':
        Book.update_book(
            {
                'bname': request.values.get('book_name'),
                'author': request.values.get('book_author'),
                'press': request.values.get('book_press'),
            }
        )
        print('test')

        return redirect(url_for('manager.bookManager'))

    else:
        book = show_info()
        return render_template('edit.html', data=book)


def show_info():
    bid = request.args['bid']
    data = Book.get_book(bid)
    pname = data[1]
    price = data[2]
    category = data[3]
    description = data[4]

    book = {
        '書籍編號': data[0],
        '書籍名稱': data[1],
        '出版社': data[2],
        '出版日期': data[3],
        '入庫日期': data[4],
        '作者': data[5],
        '書籍類別': data[6],
        '書籍主題': data[7]
    }
    return book


@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'POST':
        pass
    else:
        order_row = Order_List.get_order()
        order_data = []
        for i in order_row:
            order = {
                '訂單編號': i[0],
                '訂購人': i[1],
                '訂單總價': i[2],
                '訂單時間': i[3]
            }
            order_data.append(order)

        orderdetail_row = Order_List.get_orderdetail()
        order_detail = []

        for j in orderdetail_row:
            orderdetail = {
                '訂單編號': j[0],
                '商品名稱': j[1],
                '商品單價': j[2],
                '訂購數量': j[3]
            }
            order_detail.append(orderdetail)

    return render_template('orderManager.html', orderData=order_data, orderDetail=order_detail, user=current_user.name)
