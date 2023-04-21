import re
from typing_extensions import Self
from flask import Flask, request, template_rendered, Blueprint
from flask import url_for, redirect, flash
from flask import render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from numpy import identity, product
import random
import string
from sqlalchemy import null
from link import *
import math
from base64 import b64encode
from api.sql import Member, Order_List, Book, Record, Cart, Recommend_Book

store = Blueprint('library', __name__, template_folder='../templates')


@store.route('/', methods=['GET', 'POST'])
@login_required
def library():
    result = Book.count()
    count = math.ceil(result[0]/9)
    flag = 0

    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    if 'keyword' in request.args and 'page' in request.args:
        total = 0
        single = 1
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9
        search = request.values.get('keyword')
        keyword = search

        cursor.prepare('SELECT * FROM BOOKS WHERE BNAME LIKE :search')
        cursor.execute(None, {'search': '%' + keyword + '%'})
        book_row = cursor.fetchall()
        book_data = []
        final_data = []

        for row in book_row:
            bid = row[0]
            bname = row[1]
            press = row[2]
            pdate = row[3]
            idate = row[4]
            author = row[5]
            themeid = row[6]
            categoryid = row[7]
            book = {
                '書籍編號': bid,
                '書籍名稱': bname,
                '出版社': press
            }
            book_data.append(book)
            total = total + 1

        if (len(book_data) < end):
            end = len(book_data)
            flag = 1

        for j in range(start, end):
            final_data.append(book_data[j])

        count = math.ceil(total/9)

        return render_template('library.html', single=single, keyword=search, book_data=book_data, user=current_user.name, page=1, flag=flag, count=count)

    elif 'bid' in request.args:
        bid = request.args['bid']
        data = Book.get_book(bid)

        bname = data[1]
        press = data[2]
        pdate = data[3]
        idate = data[4]
        author = data[5]
        themeid = data[6]
        categoryid = data[7]
        # price = data[2]
        # category = data[3]
        # description = data[4]
        image = 'sdg.jpg'

        # book = {
        #     '書籍編號': bid,
        #     '書籍名稱': pname,
        #     '單價': price,
        #     '類別': category,
        #     '商品敘述': description,
        #     '商品圖片': image
        # }
        book = {
            '書籍編號': bid,
            '書籍名稱': bname,
            '作者': author,
            '出版社': press,
            '出版日期': pdate,
            '入庫日期': idate,
            '書籍類別': categoryid,
            '書籍主題': themeid
        }

        return render_template('book.html', data=book, user=current_user.name)

    elif 'page' in request.args:
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9

        book_row = Book.get_all_book()
        book_data = []
        final_data = []

        for i in book_row:
            book = {
                '書籍編號': i[0],
                '書籍名稱': i[1]
            }
            book_data.append(book)

        if (len(book_data) < end):
            end = len(book_data)
            flag = 1

        for j in range(start, end):
            final_data.append(book_data[j])

        return render_template('library.html', book_data=final_data, user=current_user.name, page=page, flag=flag, count=count)

    elif 'keyword' in request.args:
        single = 1
        search = request.values.get('keyword')
        keyword = search
        cursor.prepare('SELECT * FROM BOOKS WHERE BNAME LIKE :search')
        cursor.execute(None, {'search': '%' + keyword + '%'})
        book_row = cursor.fetchall()
        book_data = []
        total = 0

        for row in book_row:
            bid = row[0]
            bname = row[1]
            press = row[2]
            pdate = row[3]
            idate = row[4]
            author = row[5]
            themeid = row[6]
            categoryid = row[7]
            book = {
                '書籍編號': bid,
                '書籍名稱': bname,
                '出版社': press
            }

            book_data.append(book)
            total = total + 1

        if (len(book_data) < 9):
            flag = 1

        count = math.ceil(total/9)

        return render_template('library.html', keyword=search, single=single, book_data=book_data, user=current_user.name, page=1, flag=flag, count=count)

    else:
        book_row = Book.get_all_book()
        book_data = []
        temp = 0
        for i in book_row:
            book = {
                '書籍編號': i[0],
                '書籍名稱': i[1]
            }
            if len(book_data) < 9:
                book_data.append(book)

        return render_template('library.html', book_data=book_data, user=current_user.name, page=1, flag=flag, count=count)

# 會員購物車


@store.route('/cart', methods=['GET', 'POST'])
@login_required  # 使用者登入後才可以看
def cart():

    # 以防管理者誤闖
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    # 回傳有 bid 代表要 加商品
    if request.method == 'POST':

        if "bid" in request.form:
            data = Cart.get_cart(current_user.id)

            if (data == None):  # 假如購物車裡面沒有他的資料
                time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                Cart.add_cart(current_user.id, time)  # 幫他加一台購物車
                data = Cart.get_cart(current_user.id)

            tno = data[2]  # 取得交易編號
            bid = request.values.get('bid')  # 使用者想要購買的東西
            # 檢查購物車裡面有沒有商品
            book = Record.check_book(bid, tno)
            # 取得商品價錢
            price = Book.get_book(bid)[2]

            # 如果購物車裡面沒有的話 把他加一個進去
            if (book == None):
                Record.add_book(
                    {'id': tno, 'tno': bid, 'price': price, 'total': price})
            else:
                # 假如購物車裡面有的話，就多加一個進去
                amount = Record.get_amount(tno, bid)
                total = (amount+1)*int(price)
                Record.update_book(
                    {'amount': amount+1, 'tno': tno, 'bid': bid, 'total': total})

        elif "delete" in request.form:
            bid = request.values.get('delete')
            tno = Cart.get_cart(current_user.id)[2]

            Member.delete_book(tno, bid)
            book_data = only_cart()

        elif "user_edit" in request.form:
            change_order()
            return redirect(url_for('library.library'))

        elif "buy" in request.form:
            change_order()
            return redirect(url_for('library.order'))

        elif "order" in request.form:
            tno = Cart.get_cart(current_user.id)[2]
            total = Record.get_total_money(tno)
            Cart.clear_cart(current_user.id)

            time = str(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
            format = 'yyyy/mm/dd hh24:mi:ss'
            Order_List.add_order(
                {'mid': current_user.id, 'time': time, 'total': total, 'format': format, 'tno': tno})

            return render_template('complete.html', user=current_user.name)

    book_data = only_cart()

    if book_data == 0:
        return render_template('empty.html', user=current_user.name)
    else:
        return render_template('cart.html', data=book_data, user=current_user.name)


@store.route('/order')
def order():
    data = Cart.get_cart(current_user.id)
    tno = data[2]

    book_row = Record.get_record(tno)
    book_data = []

    for i in book_row:
        pname = Book.get_name(i[1])
        book = {
            '書籍編號': i[1],
            '書籍名稱': pname,
            '商品價格': i[3],
            '數量': i[2]
        }
        book_data.append(book)

    total = Record.get_total(tno)[0]

    return render_template('order.html', data=book_data, total=total, user=current_user.name)


@store.route('/orderlist')
def orderlist():
    if "oid" in request.args:
        pass

    user_id = current_user.id

    data = Member.get_order(user_id)
    orderlist = []

    for i in data:
        temp = {
            '訂單編號': i[0],
            '訂單總價': i[3],
            '訂單時間': i[2]
        }
        orderlist.append(temp)

    orderdetail_row = Order_List.get_orderdetail()
    orderdetail = []

    for j in orderdetail_row:
        temp = {
            '訂單編號': j[0],
            '書籍名稱': j[1],
            '商品單價': j[2],
            '訂購數量': j[3]
        }
        orderdetail.append(temp)

    return render_template('orderlist.html', data=orderlist, detail=orderdetail, user=current_user.name)


def change_order():
    data = Cart.get_cart(current_user.id)
    tno = data[2]  # 使用者有購物車了，購物車的交易編號是什麼
    book_row = Record.get_record(data[2])

    for i in book_row:

        # i[0]：交易編號 / i[1]：書籍編號 / i[2]：數量 / i[3]：價格
        if int(request.form[i[1]]) != i[2]:
            Record.update_book({
                'amount': request.form[i[1]],
                'bid': i[1],
                'tno': tno,
                'total': int(request.form[i[1]])*int(i[3])
            })
            print('change')

    return 0


def only_cart():

    count = Cart.check(current_user.id)

    if (count == None):
        return 0

    data = Cart.get_cart(current_user.id)
    tno = data[2]
    book_row = Record.get_record(tno)
    book_data = []

    for i in book_row:
        bid = i[1]
        pname = Book.get_name(i[1])
        price = i[3]
        amount = i[2]

        book = {
            '書籍編號': bid,
            '書籍名稱': pname,
            '商品價格': price,
            '數量': amount
        }
        book_data.append(book)

    return book_data

# 圖書推薦#


@store.route('/bookrecommend', methods=['GET', 'POST'])
def bookrecommend():
    # 以防管理者誤闖
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    if request.method == 'POST':
        if "recommend" in request.form:
            r_isbn = request.values.get('r_isbn')  # ISBN
            r_bname = request.values.get('r_bname')  # 書名
            # 寫入書籍預約
            Recommend_Book.recommend_book(
                {'r_isbn': r_isbn, 'r_bname': r_bname, 'mid': current_user.id})

    return render_template('bookrecommend.html', user=current_user.name)
