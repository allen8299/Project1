import cx_Oracle
# init Oracle instant client 位置
cx_Oracle.init_oracle_client(lib_dir="./instantclient_19_8")
connection = cx_Oracle.connect('GROUP7', 'Mt6LzciHp8', cx_Oracle.makedsn(
    '140.117.69.70', 1521, service_name='ORCLPDB1'))
cursor = connection.cursor()
