# 1112資料庫_PROJECT1_GROUP7
一套使用Flask開發的圖書館借閱系統，後端使用Oracle資料庫
<br>

## 功能
- 提供CRUD範例，並搭配資料分析功能。
- 以MVC架構開發。
- 一般借閱者可以搜尋、借閱、預約借閱、評論等。
- 後台管理者可以編輯書籍，並檢視每筆借閱紀錄以及書籍借閱圖表。

## 以下為助教提供範例
點選以下連結體驗系統功能: https://bookstore.tarflow.com/
![image](https://user-images.githubusercontent.com/52253495/226426951-b1ef62d0-56ae-443f-9483-c06524b5fb12.png)


## 安裝
### 1. 取得原始碼
```bash
git clone https://github.com/Text-Analytics-and-Retrieval/db_class2023.git
cd db_class2023/
```
### 2. 啟動Docker container
```bash!	
docker run --ipc=host -it -v $(pwd):/workspace -p 18080:8080 -p 15000:5000 --name=db_class2023 continuumio/anaconda3
```

### 3. 安裝環境
##### 安裝python套件
```bash
cd workspace
pip install -r requirements.txt
conda install -c anaconda libaio #Oracle Instant Client會用到
```

##### 安裝Oracle Instant Client
```bash
# 下載Oracle Instant Client
wget https://download.oracle.com/otn_software/linux/instantclient/219000/instantclient-basic-linux.x64-21.9.0.0.0dbru.zip
# 下載解壓縮套件
apt-get update
apt-get install unzip
# 解壓縮檔案
unzip instantclient-basic-linux.x64-21.9.0.0.0dbru.zip
# 設定環境變數
export LD_LIBRARY_PATH=/workspace/instantclient_21_9:$LD_LIBRARY_PATH
```

##### 修改程式碼

```python=
# 移除link.py中的指令路徑
cx_Oracle.init_oracle_client()
```

```python=
# 使Flask監聽所有介面
app.run(host='0.0.0.0')
```

### 4. 匯入SQL
- 打開 ebook.sql
- 將 SQL 檔裡面的 `GROUP19` 全部替換成 同學們自己的組別 ex: 第一組替換為 `GROUP1`
- 接著複製到 Oracle 上做執行，就可以得到一樣的資料了

### 5. 啟動程式
```python=
python app.py
```

## 使用
- 輸入http://localhost:15000/進入首頁。
- 首次使用請點選註冊按鈕，並註冊帳號。
- 註冊後，點選登入即可進入頁面。
