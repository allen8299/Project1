from typing import Optional
from link import *


class DB():
    def connect():
        cursor = connection.cursor()
        return cursor

    def prepare(sql):
        cursor = DB.connect()
        cursor.prepare(sql)
        return cursor

    def execute(cursor, sql):
        cursor.execute(sql)
        return cursor

    def execute_input(cursor, input):
        cursor.execute(None, input)
        return cursor

    def fetchall(cursor):
        return cursor.fetchall()

    def fetchone(cursor):
        return cursor.fetchone()

    def commit():
        connection.commit()


class Member():
    def get_member(account):
        sql = "SELECT ACCOUNT, PASSWORD, MID, IDENTITY, NAME FROM MEMBER WHERE ACCOUNT = :id"
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'id': account}))

    def get_all_account():
        sql = "SELECT ACCOUNT FROM MEMBER"
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def create_member(input):
        sql = 'INSERT INTO MEMBER VALUES (null, :name, :account, :password, :identity)'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    def delete_product(tno, pid):
        sql = 'DELETE FROM RECORD WHERE TNO=:tno and PID=:pid '
        DB.execute_input(DB.prepare(sql), {'tno': tno, 'pid': pid})
        DB.commit()

    def get_role(userid):
        sql = 'SELECT IDENTITY, NAME FROM MEMBER WHERE MID = :id '
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': userid}))


class Cart():
    def check(user_id):
        sql = 'SELECT * FROM CART, RECORD WHERE CART.MID = :id AND CART.TNO = RECORD.TNO'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': user_id}))

    def get_cart(user_id):
        sql = 'SELECT * FROM CART WHERE MID = :id'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': user_id}))

    def add_cart(user_id, time):
        sql = 'INSERT INTO CART VALUES (:id, :time, cart_tno_seq.nextval)'
        DB.execute_input(DB.prepare(sql), {'id': user_id, 'time': time})
        DB.commit()

    def clear_cart(user_id):
        sql = 'DELETE FROM CART WHERE MID = :id '
        DB.execute_input(DB.prepare(sql), {'id': user_id})
        DB.commit()


class Product():
    def count():
        sql = 'SELECT COUNT(*) FROM PRODUCT'
        return DB.fetchone(DB.execute(DB.connect(), sql))

    def get_product(pid):
        sql = 'SELECT * FROM PRODUCT WHERE PID = :id'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': pid}))

    def get_all_product():
        sql = 'SELECT * FROM PRODUCT'
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def get_name(pid):
        sql = 'SELECT PNAME FROM PRODUCT WHERE PID = :id'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': pid}))[0]

    def add_product(input):
        sql = 'INSERT INTO PRODUCT VALUES (:pid, :name, :price, :category, :description)'

        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    def delete_product(pid):
        sql = 'DELETE FROM PRODUCT WHERE PID = :id '
        DB.execute_input(DB.prepare(sql), {'id': pid})
        DB.commit()

    def update_product(input):
        sql = 'UPDATE PRODUCT SET PNAME=:name, PRICE=:price, CATEGORY=:category, PDESC=:description WHERE PID=:pid'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()


class Record():
    def get_total_money(tno):
        sql = 'SELECT SUM(TOTAL) FROM RECORD WHERE TNO=:tno'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'tno': tno}))[0]

    def check_product(pid, tno):
        sql = 'SELECT * FROM RECORD WHERE PID = :id and TNO = :tno'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': pid, 'tno': tno}))

    def get_price(pid):
        sql = 'SELECT PRICE FROM PRODUCT WHERE PID = :id'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': pid}))[0]

    def add_product(input):
        sql = 'INSERT INTO RECORD VALUES (:id, :tno, 1, :price, :total)'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    def get_record(tno):
        sql = 'SELECT * FROM RECORD WHERE TNO = :id'
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'id': tno}))

    def get_amount(tno, pid):
        sql = 'SELECT AMOUNT FROM RECORD WHERE TNO = :id and PID=:pid'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': tno, 'pid': pid}))[0]

    def update_product(input):
        sql = 'UPDATE RECORD SET AMOUNT=:amount, TOTAL=:total WHERE PID=:pid and TNO=:tno'
        DB.execute_input(DB.prepare(sql), input)

    def delete_check(pid):
        sql = 'SELECT * FROM RECORD WHERE PID=:pid'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'pid': pid}))

    def get_total(tno):
        sql = 'SELECT SUM(TOTAL) FROM RECORD WHERE TNO = :id'
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'id': tno}))[0]


class Order_List():
    def add_order(input):
        sql = 'INSERT INTO ORDER_LIST VALUES (null, :mid, TO_DATE(:time, :format ), :total, :tno)'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    # def get_order():
    #     sql = 'SELECT OID, NAME, PRICE, ORDERTIME FROM ORDER_LIST NATURAL JOIN MEMBER ORDER BY ORDERTIME DESC'
    #     return DB.fetchall(DB.execute(DB.connect(), sql))

    # def get_orderdetail():
    #     sql = 'SELECT O.OID, P.PNAME, R.SALEPRICE, R.AMOUNT FROM ORDER_LIST O, RECORD R, PRODUCT P WHERE O.TNO = R.TNO AND R.PID = P.PID'
    #     return DB.fetchall(DB.execute(DB.connect(), sql))
    
    def get_user_borrowing_record(userid):
        sql = 'SELECT BOOKS.BID, BOOKS.BNAME, BORROWDATE, RETURNDATE, LIMITDATE, MID \
               FROM BORROWINGRECORDS, BOOKS \
               WHERE MID = :id AND BOOKS.BID = BORROWINGRECORDS.BID ORDER BY BORROWDATE DESC'
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'id': userid}))
    
    def get_borrowing_record_not_return():
        sql = 'SELECT BOOKS.BID, BOOKS.BNAME, BORROWDATE, RETURNDATE, LIMITDATE, MID \
               FROM BORROWINGRECORDS, BOOKS \
               WHERE BOOKS.BID = BORROWINGRECORDS.BID \
               AND (RETURNDATE IS NULL OR RETURNDATE = \'\' ) \
               ORDER BY BORROWDATE DESC'
        return DB.fetchall(DB.execute(DB.connect(), sql))
    
    def get_borrowing_record_all():
        sql = 'SELECT BOOKS.BID, BOOKS.BNAME, BORROWDATE, RETURNDATE, LIMITDATE, MID \
               FROM BORROWINGRECORDS, BOOKS \
               WHERE BOOKS.BID = BORROWINGRECORDS.BID \
               ORDER BY BORROWDATE DESC'
        return DB.fetchall(DB.execute(DB.connect(), sql))


class Analysis():
    def month_price(i):
        sql = 'SELECT EXTRACT(MONTH FROM ORDERTIME), SUM(PRICE) FROM ORDER_LIST WHERE EXTRACT(MONTH FROM ORDERTIME)=:mon GROUP BY EXTRACT(MONTH FROM ORDERTIME)'
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {"mon": i}))

    def month_count(i):
        sql = 'SELECT EXTRACT(MONTH FROM ORDERTIME), COUNT(OID) FROM ORDER_LIST WHERE EXTRACT(MONTH FROM ORDERTIME)=:mon GROUP BY EXTRACT(MONTH FROM ORDERTIME)'
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {"mon": i}))

    def category_sale():
        sql = 'SELECT SUM(TOTAL), CATEGORY FROM(SELECT * FROM PRODUCT,RECORD WHERE PRODUCT.PID = RECORD.PID) GROUP BY CATEGORY'
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def member_sale():
        sql = 'SELECT SUM(PRICE), MEMBER.MID, MEMBER.NAME FROM ORDER_LIST, MEMBER WHERE ORDER_LIST.MID = MEMBER.MID AND MEMBER.IDENTITY = :identity GROUP BY MEMBER.MID, MEMBER.NAME ORDER BY SUM(PRICE) DESC'
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'identity': 'user'}))

    def member_sale_count():
        sql = 'SELECT COUNT(*), MEMBER.MID, MEMBER.NAME FROM ORDER_LIST, MEMBER WHERE ORDER_LIST.MID = MEMBER.MID AND MEMBER.IDENTITY = :identity GROUP BY MEMBER.MID, MEMBER.NAME ORDER BY COUNT(*) DESC'
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'identity': 'user'}))


# 20230420 BOOKS
class Book():
    def count():
        sql = 'SELECT COUNT(*) FROM BOOKS'
        return DB.fetchone(DB.execute(DB.connect(), sql))

    def get_book(bid):
        sql = 'SELECT * FROM BOOKS WHERE BID = :id'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': bid}))

    def get_all_book():
        sql = 'SELECT * FROM BOOKS'
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def get_name(bid):
        sql = 'SELECT PNAME FROM BOOKS WHERE BID = :id'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': bid}))[0]

    def add_book(input):
        sql = 'INSERT INTO BOOKS (BID, BNAME, AUTHOR, PRESS, PDATE, IDATE, CATEGORYID, THEMEID) VALUES (:bid, :bname, :author, :press, TO_DATE(:pdate, \'YYYY-MM-DD\'), TO_DATE(:idate, \'YYYY-MM-DD\'), :categoryid, :themeid)'

        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    def delete_book(bid):
        sql = 'DELETE FROM BOOKS WHERE BID = :id '
        DB.execute_input(DB.prepare(sql), {'id': bid})
        DB.commit()

    # def update_book(input):
    #     sql = 'UPDATE BOOKS SET BNAME=:bname, AUTHOR=:author, PRESS=:press, \
    #                            PDATE=:pdate, IDATE=:idate, CATEGORYID=:categoryid, THEMEID=:themeid \
    #            WHERE BID=:bid'
    #     DB.execute_input(DB.prepare(sql), input)
    #     DB.commit()
    def update_book(input):
        sql = 'UPDATE BOOKS SET BNAME=:bname, AUTHOR=:author, PRESS=:press, \
                                CATEGORYID=:categoryid, THEMEID=:themeid \
               WHERE BID=:bid'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

class Recommend_Book():
    def recommend_book(input):
        sql = 'INSERT INTO RECOMMENDATION (R_ISBN, R_BNAME, MID) VALUES (:r_isbn, :r_bname, :mid)'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()
    def get_all_recommend_book():
        sql = 'SELECT R_ISBN, R_BNAME, MID FROM RECOMMENDATION'
        return DB.fetchall(DB.execute(DB.connect(), sql))


# 20230420 THEME
class Theme():
    def get_theme(themeid):
        sql = 'SELECT * FROM THEME WHERE THEMEID = :id'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': themeid}))
    def get_all_theme():
        sql = 'SELECT * FROM THEME'
        return DB.fetchall(DB.execute(DB.connect(), sql))
    
# 20230420 CATEGORIES
class Categories():
    def get_categories(categoryid):
        sql = 'SELECT * FROM CATEGORIES WHERE CATEGORYID = :id'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': categoryid}))
    def get_all_categories():
        sql = 'SELECT * FROM CATEGORIES'
        return DB.fetchall(DB.execute(DB.connect(), sql))

# 20230422 借閱/預約相關紀錄
class Book_Record():
    def check_book_is_reserved(bid):
        sql = 'SELECT * FROM RESERVATIONRECORDS WHERE BID = :id AND RESERVESTATUS = \'A\' '
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': bid}))
    
    def insert_reservation_record(input):
        sql = 'INSERT INTO RESERVATIONRECORDS (MID, BID, RESERVEDATE, RESERVESTATUS) VALUES (:mid, :bid, TO_DATE(:reservedate, \'YYYY-MM-DD\'), :reservestatus)'
        print(sql)
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()
    
    def check_book_is_borrowed(bid):
        sql = 'SELECT * FROM BORROWINGRECORDS WHERE BID = :id AND (RETURNDATE IS NULL OR RETURNDATE = \'\' ) '
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'id': bid}))
    
    def insert_borrow_record(input):
        sql = 'INSERT INTO BORROWINGRECORDS (MID, BID, BORROWDATE, LIMITDATE) VALUES (:mid, :bid, TO_DATE(:borrowdate, \'YYYY-MM-DD\'), TO_DATE(:limitdate, \'YYYY-MM-DD\'))'
        print(sql)

        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    def update_user_borrow_record_returndate(input):
        sql = 'UPDATE BORROWINGRECORDS SET RETURNDATE=TO_DATE(:returndate, \'YYYY-MM-DD\') WHERE MID=:mid AND BID=:bid '
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()
        
    def get_user_borrow_record(user_id):
        sql = 'SELECT MID, BID, RESERVEDATE, RESERVESTATUS  FROM RESERVATIONRECORDS WHERE RESERVATIONRECORDS.MID = :id'
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'id': user_id}))
    
    def update_user_reserve_record_status(input):
        sql = 'UPDATE RESERVATIONRECORDS SET RESERVESTATUS=:reservestatus WHERE MID=:mid AND BID=:bid '
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    def delete_user_reserve_record(input):
        sql = 'DELETE FROM RESERVATIONRECORDS WHERE MID=:mid AND BID=:bid '
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()