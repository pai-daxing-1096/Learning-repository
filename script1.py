import pymysql
from flask import Flask, make_response, render_template,jsonify,request,session,redirect
from flask_cors import CORS

def get_db():
    return pymysql.connect(
        host='localhost',
        user='hai',
        password='Ngc080250',
        port=3306
    )

conn = get_db()

try :
    with conn.cursor() as cursor:

        cursor.execute('CREATE DATABASE IF NOT EXISTS library_user_information')

        conn.select_db('library_user_information')

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_login_information(
                id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户id',
                user_name VARCHAR(20) NOT NULL UNIQUE COMMENT '用户名称',
                user_password VARCHAR(20) NOT NULL COMMENT '用户密码'
            )COMMENT '用户名和密码'
        """)

        if conn:
            conn.commit()

except pymysql.Error as e:
    if conn:
        conn.rollback()

finally :
    if conn:
        conn.close()

app = Flask(__name__)
app.secret_key = 'hiowq09hfeq791bq13rj'
CORS(app)

# 登录页面接口
@app.route('/')
def login_page():
        return render_template('login.html')

# 登录页面注册按键接口
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
# 用户名输入
    username = data.get('username')

# 设置输入密码
    password_1 = data.get('password_1')

# 再次输入密码用于验证
    password_2 = data.get('password_2')

# 检查用户名是否重复
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM library_user_information.user_login_information WHERE user_name = %s',(username,))
            if cursor.fetchone():
                return jsonify({"error":"用户名重复"}),409
    finally:
        if conn:
            conn.close()

# 用户名和密码不能为空
    if not username or not password_1 or not password_2:
        return jsonify({"error":"用户名或密码不能为空"}),400

# 第一次密码输入和第二次密码输入必须一致
    if password_1 != password_2:
        return jsonify({"error":"两次输入的密码必须一致"}),400

# 密码必须大于6位
    if len(password_1) < 6:
        return jsonify({"error":"密码长度至少为6位"}),400

# 如果所有判断均确认为正常，则返回成功注册文本并且进行数据库写入
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute(
             "INSERT INTO library_user_information.user_login_information (user_name, user_password) VALUES (%s, %s)",(username, password_1),)
        conn.commit()

    except pymysql.Error as e:
        if conn:
            conn.rollback()

        return jsonify({"success":False,"message":"账号注册失败，请重试"}),400

    finally:
        if conn:
            conn.close()

    return jsonify({"success":True,"message":"账号注册成功"}),201

# 登录接口
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

# 连接数据库，通过输入的用户名查询密码
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute('SELECT id,user_password FROM library_user_information.user_login_information WHERE user_name = %s',(username,))

# 获取返回的id和密码
            row = cursor.fetchone()

# 如果无法通过用户名查询到密码，则返回输入的用户或密码不存在
            if not row:
               return jsonify({"error":"您输入的用户名或密码不存在"}),400

# 将数据库查询到的密码与用户输入的密码比对，如果不相同则返回登录失败
            if password != row[1]:
                return jsonify({"error":"您输入的用户名或密码输入错误"}),400

# 将数据库查询到的密码与用户输入的密码比对，如果相同则返回登录成功
            else:

# 将用户信息存入session
                session['user_id'] = row[0]
                session['user_name'] = username

                return jsonify({"success":True,"message":"登录成功"}),201
    finally:
        if conn:
            conn.close()

# 登录成功后的主页
@app.route('/home')
def home():

# 未成功登录则跳回登录页面
    if 'user_id' not in session:
        return redirect('/')

# 成功登录则跳到主页页面
    return render_template('home.html', username=session.get('user_name'))

@app.route('/home/')

# 登出接口
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "已退出"}), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
