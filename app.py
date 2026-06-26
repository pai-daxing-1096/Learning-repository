from flask import Flask,request,jsonify

import re

app = Flask(__name__)

# 验证函数
def verify(name,min_length,max_length,data) :

    if not data :
        return False,f"{name}不能为空,请重新输入"

    data_str = str(data).strip()

    if not re.fullmatch(r'[A-Za-z0-9]+', data_str):
        return False, f"{name}应当只包含数字和字母,请重新输入"

    if not (min_length <= len(data_str) <= max_length) :
        return False,f"{name}的长度应当为{min_length}~{max_length},请重新输入"

    return True,data_str

# 主页
@app.route('/home')
def home():
    return "主页欢迎页面,待开发"

# 主页下登录按钮(返回登录页面)
@app.route('/home/homepage_button_login')
def homepage_button_login():
    return "登录页面,待开发"

# 主页下注册按钮(返回注册页面)
@app.route('/home/homepage_button_signup')
def homepage_button_signup():
    return "注册页面,待开发"

# 登陆页面下登录按钮(开始验证账号密码)
@app.route('/login/loginpage_button_login',methods=['GET'])
def loginpage_button_login():
   return "登录验证,待开发"

# 登陆页面下注册按钮(返回注册页面)
@app.route('/login/loginpage_button_signup')
def loginpage_button_signup():
    return "注册页面,待开发"

# 注册页面下注册按钮(开始验证账号密码并且进行存储)
@app.route('/signup/signuppage_button_signup', methods=['POST'])
def signuppage_button_signup():

    json_data = request.get_json()

    if not json_data:
        return jsonify({"error": "请求必须为 JSON 格式"}), 400

    account = json_data.get('account')
    password = json_data.get('password')

    is_ok_acc, msg_acc = verify("账号", account, 6, 20)
    if not is_ok_acc:
        return jsonify({"error":msg_acc}), 400

    is_ok_pwd, msg_pwd = verify("密码", password, 8, 30)
    if not is_ok_pwd:
        return jsonify({"error":msg_pwd}), 400

    pass # 此处后续补充数据库存储逻辑

    return jsonify({"message":"注册成功"}), 200

if __name__ == '__main__':
    app.run()
