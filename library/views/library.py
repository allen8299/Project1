import re
from typing_extensions import Self
from flask import Flask, request, template_rendered, Blueprint
from flask import url_for, redirect, flash
from flask import render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from numpy import identity, product
import random
import string
from sqlalchemy import null
from link import *
import math
from base64 import b64encode
from api.sql import Member, Order_List, Book, Record, Cart, Recommend_Book, Theme, Categories, Book_Record

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
        book_is_borrowed = False
        book_is_reserved = False

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

        # 確認借閱狀態
        bb_data = Book_Record.check_book_is_borrowed(bid)
        print('bb_data:')
        print(bb_data)
        if bb_data is not None:
            book_is_borrowed = True
        # 確認預約狀態
        br_data = Book_Record.check_book_is_reserved(bid)
        print('br_data:')
        print(br_data)
        if br_data is not None:
            book_is_reserved = True

        theme_data = Theme.get_theme(themeid)
        category_data = Categories.get_categories(categoryid)
        book = {
            '書籍編號': bid,
            '書籍名稱': bname,
            '作者': author,
            '出版社': press,
            '出版日期': pdate,
            '入庫日期': idate,
            '書籍類別': theme_data[1],
            '書籍主題': category_data[1]
        }

        return render_template('book.html', data=book, user=current_user.name, book_is_borrowed=book_is_borrowed, book_is_reserved=book_is_reserved)

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

# 圖書推薦


@store.route('/book_recommend', methods=['GET', 'POST'])
def book_recommend():
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

    return render_template('book_recommend.html', user=current_user.name)

# 預約清單
# 懶得想名字，就用cart


@store.route('/book_cart', methods=['GET', 'POST'])
def book_cart():
    # 以防管理者誤闖
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    if request.method == 'POST':
        if "cancel" in request.form:
            # 取消預約，狀態改為D
            bid = request.values.get('cancel')
            Book_Record.delete_user_borrow_record(
                {'mid': current_user.id, 'bid': bid})
            flash('Cancel Success')
        elif "borrow" in request.form:
            bid = request.values.get('borrow')
            # 借閱書籍，狀態改為B，寫入預約紀錄
            print('借閱書籍')
            
            # 取得當天日期
            today_data = datetime.now().date()
            future_date = today_data + timedelta(days=14)
            print('當天日期：', today_data)
            print('14 天後的日期：', future_date)
            Book_Record.update_user_borrow_record_status(
                {'mid': current_user.id, 'bid': bid, 'reservestatus': 'B'})
            Book_Record.insert_borrow_record(
                {'mid': current_user.id, 'bid': bid, 'borrowdate': today_data, 'limitdate': future_date})
            flash('Borrow Success')

    book_data = only_cart()
    # book_data = 0
    if book_data == 0:
        return render_template('empty.html', user=current_user.name)
    else:
        return render_template('book_cart.html', data=book_data, user=current_user.name)


def only_cart():
    count = Book_Record.get_user_borrow_record(current_user.id)

    if (count == None):
        return 0

    # 圖書不一定會預約再借閱，也可能直接借閱
    record_row = Book_Record.get_user_borrow_record(current_user.id)

    # 取得當天日期
    today_date = datetime.today().strftime('%Y-%m-%d')

    book_data = []

    for row in record_row:
        # reserve_status_str = ''
        bid = row[1]
        reserve_date = row[2]
        reserve_date = str(reserve_date)[0:10]
        print(today_date, reserve_date)
        reserve_status = row[3]
        book_row = Book.get_book(bid)

        if today_date > reserve_date and reserve_status != 'B':
            # 當前日期超過預約日期，也沒有借閱完成(B)，預約狀態改為C(預約過期)
            print('當前日期超過預約日期，預約狀態改為C(預約過期)')
            Book_Record.update_user_borrow_record_status(
                {'mid': current_user.id, 'bid': bid, 'reservestatus': 'C'})
            reserve_status = 'C'
        # elif today_date == reserve_date:
        #     print('借閱')
        #     Book_Record.update_user_borrow_record_status(
        #         {'mid': current_user.id, 'bid': bid, 'reservestatus': 'B'})
        #     reserve_status = 'B'

        # if reserve_status == 'A':
        #     reserve_status_str = '預約中'
        # elif reserve_status == 'B':
        #     reserve_status_str = '借閱完成'
        # elif reserve_status == 'C':
        #     reserve_status_str = '預約過期'
        # elif reserve_status == 'D':
        #     reserve_status_str = '預約取消'

        bname = book_row[1]

        book = {
            '書籍編號': bid,
            '書籍名稱': bname,
            '預約日期': reserve_date,
            '今天日期': today_date,
            '預約狀態': reserve_status
        }
        book_data.append(book)

    return book_data

# 歷史預約


def book_orderlist():
    # 以防管理者誤闖
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    # if request.method == 'POST':
    #     if "recommend" in request.form:
    #         r_isbn = request.values.get('r_isbn')  # ISBN
    #         r_bname = request.values.get('r_bname')  # 書名
    #         # 寫入書籍預約
    #         Recommend_Book.recommend_book(
    #             {'r_isbn': r_isbn, 'r_bname': r_bname, 'mid': current_user.id})

    return render_template('book_record.html', user=current_user.name)


@ store.route('/book', methods=['GET', 'POST'])
def book_reserve():
    # 以防管理者誤闖
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))
    # 取得當天日期
    today_date = datetime.today().strftime('%Y-%m-%d')
    today = datetime.now().date()
    future_date = today + timedelta(days=14)

    print('當天日期：', today)
    print('14 天後的日期：', future_date)

    if request.method == 'POST':
        if "reserve" in request.form:
            book_is_borrowed = False
            book_is_reserved = False
            # 取得bid
            bid = request.values.get('reserve')
            tmp_reserve_date = request.values.get('reserve_date')

            # 不知道為何datepicker format沒有用
            # 將日期字串轉換為 datetime 物件
            date_obj = datetime.strptime(tmp_reserve_date, "%m/%d/%Y")
            # 將 datetime 物件轉換為字串
            reserve_date = date_obj.strftime("%Y-%m-%d")
            print(today_date, reserve_date)

            data = Book.get_book(bid)
            bname = data[1]
            press = data[2]
            pdate = data[3]
            idate = data[4]
            author = data[5]
            themeid = data[6]
            categoryid = data[7]
            image = 'sdg.jpg'

            theme_data = Theme.get_theme(themeid)
            category_data = Categories.get_categories(categoryid)
            book = {
                '書籍編號': bid,
                '書籍名稱': bname,
                '作者': author,
                '出版社': press,
                '出版日期': pdate,
                '入庫日期': idate,
                '書籍類別': theme_data[1],
                '書籍主題': category_data[1]
            }
            if reserve_date <= today_date:
                flash('Reserve Error')
            else:
                # 寫入預約
                reserve_status = 'A'
                book_is_reserved = True
                print(current_user.id, bid, reserve_date, reserve_status)
                Book_Record.insert_reservation_record(
                    {'mid': current_user.id, 'bid': bid, 'reservedate': reserve_date, 'reservestatus': reserve_status})
                flash('Reserve Success')

    # FIXME 改成bid去get_book可能比較好
    return render_template('book.html', data=book, user=current_user.name, book_is_borrowed=book_is_borrowed, book_is_reserved=book_is_reserved)


@store.route('/', methods=['GET', 'POST'])
@store.errorhandler(ValueError)
def handle_value_error(error):
    return render_template('error.html', message=error), 400
