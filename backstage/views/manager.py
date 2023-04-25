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
        # data = Record.delete_check(bid)

        # if data is not None:
        #     flash('failed')
        # else:
        #     # 刪除
        #     Product.delete_product(bid)
        #     # 重新取data
        #     data = Product.get_product(bid)
        # bid = request.values.get('delete')
        borrow_data = Book_Record.check_book_is_borrowed(bid)
        reserve_data = Book_Record.check_book_is_reserved(bid)
        if borrow_data is not None or reserve_data is not None:
            flash('failed')
        else:
            Book.delete_book(bid)

    elif 'edit' in request.values:
        bid = request.values.get('edit')
        return redirect(url_for('manager.edit', bid=bid))

    book_data = book()
    categories = dict(Categories.get_all_categories())
    themes = dict(Theme.get_all_theme())
    # print(type(categories))
    # print(categories)
    return render_template('bookManager.html', book_data=book_data, categories=categories, themes=themes, user=current_user.name)


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
        while data is not None:
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
                'bid': request.values.get('bid'),
                'bname': request.values.get('book_name'),
                'author': request.values.get('book_author'),
                'press': request.values.get('book_press'),
                'categoryid': request.values.get('book_category'),
                'themeid': request.values.get('book_theme'),
            }
        )
        print('test')

        return redirect(url_for('manager.bookManager'))

    else:
        book = show_book_info()
        print(book)
        # categories = Theme.get_all_theme()
        categories = dict(Categories.get_all_categories())
        themes = dict(Theme.get_all_theme())
        print(categories)
        print(themes)
        return render_template('edit.html', data=book, categories=categories, themes=themes)


def show_book_info():
    bid = request.args['bid']
    data = Book.get_book(bid)
    pname = data[1]
    price = data[2]
    category = data[3]
    description = data[4]
    print(data[6])
    print(data[7])
    book = {
        '書籍編號': data[0],
        '書籍名稱': data[1],
        '出版社': data[2],
        '出版日期': data[3],
        '入庫日期': data[4],
        '作者': data[5],
        '書籍類別': data[7],
        '書籍主題': data[6]
    }
    return book

# 借閱管理(懶得改名)


@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'GET':
        if (current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('library'))
    if request.method == 'POST':
        if "return_book" in request.form:
            print("return_book")
            return_book_list = request.values.get('return_book').split('|||')
            bid = return_book_list[0]
            mid = return_book_list[1]
            today_date = datetime.now().date()
            today_date = today_date.strftime('%Y-%m-%d')
            print(bid, mid, today_date)
            Book_Record.update_user_borrow_record_returndate(
            {
                'bid': bid,
                'mid': mid,
                'returndate': today_date
            }
        )

    order_row = Order_List.get_borrowing_record_not_return()
    order_data = []
    for i in order_row:
        # 無法理解oracle的date怎麼存的
        borrow_date = i[2]
        borrow_date = borrow_date.strftime('%Y-%m-%d')

        return_date = i[3]
        if return_date is not None:
            return_date = return_date.strftime('%Y-%m-%d')
        else:
            return_date = ''

        limit_date = i[4]
        limit_date = limit_date.strftime('%Y-%m-%d')

        mid = i[5]
        # 根據mid取user姓名
        member_row = Member.get_role(mid)
        user_name = member_row[1]

        order = {
            '書籍編號': i[0],
            '書籍名稱': i[1],
            '借閱日期': borrow_date,
            '實際歸還日期': return_date,
            '應歸還日期': limit_date,
            '借閱人名稱': user_name,
            '借閱人編號': mid
        }
        order_data.append(order)

    return render_template('orderManager.html', orderData=order_data, user=current_user.name)

# 讀者推薦書單管理


@manager.route('/recommendManager', methods=['GET', 'POST'])
@login_required
def recommendManager():
    if request.method == 'POST':
        pass
    else:
        recommend_row = Recommend_Book.get_all_recommend_book()
        recommend_data = []
        for i in recommend_row:
            r_isbn = i[0]
            r_bname = i[1]
            mid = i[2]

            recommend = {
                'ISBN': r_isbn,
                '書籍名稱': r_bname,
                '推薦人編號': mid
            }
            recommend_data.append(recommend)

        # orderdetail_row = Order_List.get_orderdetail()
        # order_detail = []

        # for j in orderdetail_row:
        #     orderdetail = {
        #         '訂單編號': j[0],
        #         '商品名稱': j[1],
        #         '商品單價': j[2],
        #         '訂購數量': j[3]
        #     }
        #     order_detail.append(orderdetail)

    return render_template('recommendManager.html', recommend_data=recommend_data, user=current_user.name)
