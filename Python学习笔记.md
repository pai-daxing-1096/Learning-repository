> [!CAUTION]
>
> 1. **PyMySQL 库**：用于连接 MySQL 数据库、执行 SQL 语句、提交/回滚事务。
> 2. **数据库连接参数**：`host`、`user`、`password`、`port`。
> 3. **数据库创建**：`CREATE DATABASE IF NOT EXISTS`。
> 4. **选择数据库**：`conn.select_db()`。
> 5. **创建表**：`CREATE TABLE IF NOT EXISTS`，包含字段类型、约束（`PRIMARY KEY`、`AUTO_INCREMENT`、`NOT NULL`、`UNIQUE`）、注释（`COMMENT`）。
> 6. **数据库事务**：`conn.commit()` 提交更改。
> 7. **Flask 框架**：Web 框架，用于创建应用、定义路由、处理请求与响应。
> 8. **Flask 应用实例**：`Flask(__name__)`。
> 9. **路由装饰器**：`@app.route()` 定义 URL 与函数的映射。
> 10. **请求方法限制**：`methods=['POST']` 指定接口允许的 HTTP 方法。
> 11. **获取 JSON 请求数据**：`request.get_json()`。
> 12. **字典安全取值**：`data.get('key')` 避免 KeyError。
> 13. **JSON 响应**：`jsonify()` 返回 JSON 格式的数据。
> 14. **HTTP 状态码**：`400`（错误请求）、`409`（冲突）、`201`（创建成功）、`200`（成功）、`401`（未授权）等。
> 15. **异常处理**：`try...finally` 确保数据库连接关闭。
> 16. **数据库查询**：`cursor.execute()` 执行 SQL，`cursor.fetchone()` 取一行结果。
> 17. **Session 管理**：
> 	- 设置 `app.secret_key` 用于加密签名。
> 	- `session` 对象像字典一样存储用户数据（如 `session['user_id']`）。
> 	- 判断登录状态：`if 'user_id' in session`。
> 	- 清除 session：`session.clear()`。
> 18. **重定向**：`redirect('/')` 跳转到其他路由。
> 19. **模板渲染**：`render_template('home.html', username=...)` 返回 HTML 页面，支持变量替换。
> 20. **跨域支持**：`CORS(app)` 允许前端跨域请求。
> 21. **Python 模块导入**：`from flask import ...`，`import pymysql`。
> 22. **函数定义**：`def get_db():` 等。
> 23. **上下文管理器**：`with conn.cursor() as cursor` 自动管理游标生命周期。
> 24. **环境变量（未使用但隐含）**：`secret_key` 硬编码，生产环境应使用环境变量。
> 25. **应用启动入口**：`if __name__ == '__main__':` 判断是否直接运行，并启动开发服务器 `app.run()`。
> 26. **开发服务器参数**：`host='0.0.0.0'` 监听所有网络接口，`port=5000`，`debug=True` 开启调试模式。

# Python学习笔记

---

#### 一.三个常用进制转换函数

| 函数     | 作用                          | 返回示例（输入42） |
| :------- | :---------------------------- | :----------------- |
| `bin(x)` | 将整数 x 转换为二进制字符串   | `'0b101010'`       |
| `oct(x)` | 将整数 x 转换为八进制字符串   | `'0o52'`           |
| `hex(x)` | 将整数 x 转换为十六进制字符串 | `'0x2a'`           |

---

#### 二. .format()的详细用法

##### 1. 基本语法

```
"模板字符串".format(参数1, 参数2, ...)
```

##### 2. 位置参数

可以在 `{}` 中指定参数的索引，实现按位置引用，甚至重复引用同一参数。

```
print("{0} love {1}. {1} loves {0} too.".format("Tom", "Jerry"))
# 输出：Tom love Jerry. Jerry loves Tom too.
```

##### 3. 关键字参数

通过参数名指定，使代码更清晰。

```
print("我的名字是{name}，年龄是{age}。".format(name="李四", age=25))
# 输出：我的名字是李四，年龄是25。
```

##### 4.访问对象的属性

```
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

p = Person("王五", 30)
print("姓名：{0.name}，年龄：{0.age}".format(p))
# 输出：姓名：王五，年龄：30
```

##### 5.访问字典的键

```
data = {"name": "赵六", "age": 22}
print("姓名：{d[name]}，年龄：{d[age]}".format(d=data))
# 输出：姓名：赵六，年龄：22
```

---

#### 二.格式说明符的通用语法

```
{[填充字符][对齐方式][符号][#][0][宽度][.精度][类型]}
```

**顺序必须严格遵守**：填充字符必须在最前面（如果有），然后是对齐方式，然后是符号等。

##### 1. 对齐方式

| 选项 | 含义               | 示例                | 输出（假设内容为"hi"，宽度6，填充*） |
| :--- | :----------------- | :------------------ | :----------------------------------- |
| `<`  | 左对齐             | `{:*<6}`            | `hi****`                             |
| `>`  | 右对齐（默认）     | `{:*>6}`            | `****hi`                             |
| `^`  | 居中对齐           | `{:*^6}`            | `**hi**`                             |
| `=`  | 填充在符号与数字间 | `{:=+6}`（数字-42） | `- 42`（填充空格在符号后）           |

**注意**：`=` 只用于数字，且必须与符号选项一起使用。

##### 2. 符号选项（仅用于数字）

| 选项 | 含义                         | 示例（n=42）    | 示例（n=-42）   |
| :--- | :--------------------------- | :-------------- | :-------------- |
| `+`  | 正数加 `+`，负数加 `-`       | `{:+d}` → `+42` | `{:+d}` → `-42` |
| `-`  | （默认）负数加 `-`，正数不加 | `{:-d}` → `42`  | `{:-d}` → `-42` |
| 空格 | 正数前加空格，负数前加 `-`   | `{: d}` → `42`  | `{: d}` → `-42` |

##### 3. 特殊选项

| 选项 | 含义                                                       | 示例                       | 输出         |
| :--- | :--------------------------------------------------------- | :------------------------- | :----------- |
| `#`  | 进制前缀（二进制 `0b`，八进制 `0o`，十六进制 `0x`）        | `{:#b}` (42) → `0b101010`  | 显示进制前缀 |
| `0`  | 用零填充数字左侧的空位（当宽度大于数字位数时）             | `{:05d}` (42) → `00042`    | 数字前补零   |
| `.`  | 精度分隔符，后跟数字（用于浮点数小数位数或字符串最大长度） | `{:.2f}` (3.1415) → `3.14` | 保留两位小数 |

##### 4. 宽度

- 指定最小输出宽度，是一个整数。
- 如果内容长度小于宽度，用填充字符补齐。
- 如果内容长度大于等于宽度，则宽度无效，按实际长度显示。

示例：

```
"{:10}".format("hi")      # 'hi        '（默认右对齐）
"{:<10}".format("hi")     # 'hi        '（左对齐）
```

##### 5. 精度

格式：`.` 后跟整数。

- 对浮点数（`f`、`e` 等）：指定小数点后保留的位数。
- 对字符串（`s`）：指定最大字符数，超出部分截断。
- 对整数一般不使用。

示例：

```
"{:.3f}".format(3.14159)   # '3.142'
"{:.3s}".format("hello")   # 'hel'
```

##### 6. 类型（数据类型指示符）

###### ①整数类型

| 类型 | 含义             | 示例（n=42） | 输出     |
| :--- | :--------------- | :----------- | :------- |
| `d`  | 十进制整数       | `{:d}`       | `42`     |
| `b`  | 二进制           | `{:b}`       | `101010` |
| `o`  | 八进制           | `{:o}`       | `52`     |
| `x`  | 十六进制（小写） | `{:x}`       | `2a`     |
| `X`  | 十六进制（大写） | `{:X}`       | `2A`     |

###### ②浮点数类型

| 类型 | 含义                          | 示例（x=3.14159） | 输出       |
| :--- | :---------------------------- | :---------------- | :--------- |
| `f`  | 定点表示法                    | `{:.2f}`          | `3.14`     |
| `F`  | 同 `f`，但 `nan` 转为 `NAN`   | `{:F}`            | `3.14159`  |
| `e`  | 科学计数法（小写e）           | `{:.2e}`          | `3.14e+00` |
| `E`  | 科学计数法（大写E）           | `{:.2E}`          | `3.14E+00` |
| `g`  | 通用格式（自动选 `f` 或 `e`） | `{:.3g}`          | `3.14`     |
| `G`  | 通用格式（大写E）             | `{:.3G}`          | `3.14`     |
| `%`  | 百分比格式（数值×100加%）     | `{:.2%}` (0.1234) | `12.34%`   |

###### ③字符串类型

| 类型 | 含义           | 示例（s="hello"） | 输出    |
| :--- | :------------- | :---------------- | :------ |
| `s`  | 字符串（默认） | `{:.3s}`          | `hel`   |
| 无   | 同 `s`         | `{}`              | `hello` |

###### ④其他类型

| 类型 | 含义                      | 示例        | 输出 |
| :--- | :------------------------ | :---------- | :--- |
| `c`  | 将整数转为对应Unicode字符 | `{:c}` (65) | `A`  |
| `%`  | 百分比（见上）            |             |      |

---

#### 三.索引和切片

##### 1.在 Python 中，**索引** 指的是字符串（或列表、元组等）中每个字符的位置编号。

- 索引从 **0** 开始，即第一个字符的索引是 `0`，第二个是 `1`，依此类推。
- 也可以使用 **负数索引**，`-1` 表示最后一个字符，`-2` 表示倒数第二个，以此类推。

##### 2.切片（提取子串）

使用 `[起始:结束]` 可以截取从 `起始` 到 `结束` 之间的字符（**注意**：包含起始，但不包含结束）。

- 如果省略 `起始`，默认从开头开始。
- 如果省略 `结束`，默认一直到末尾。

---

#### 四.字符串方法

```python
#移除字符串头尾的空白字符或指定字符序列
.strip("指定字符")

#移除字符串开头的空白字符或指定字符序列
str.lstrip("指定字符")

#移除字符串尾部的空白字符或指定字符序列
str.rstrip("指定字符")

#用于将字符串分割成列表，最多分割n次
.split("指定分割符",n)

#用于判断字符串 变量名 是否以指定的子串 '指定字符串' 开头。如果是，返回 True；否则返回 False
变量名.startswith('指定字符串')`

#n:指定切割次数

cmp(list1,list2)							#比较列表的两个元素
len(list)									#列表元素个数
max(list)									#返回列表的最大值
min(list)									#返回列表的最小值
list(seq)									#将元组转化为列表
sum(list)									#求和

list.append(obj)							#在列表末尾添加新对象
list.count(obj)								#统计某个元素在列表中出现的次数
list.extend(seq)							#在列表的末尾一次性追加另一个序列的多个值
list.index(obj)								#在列表中找出某个值第一个匹配项的索引位置
list.insert(index,obj)						#将对象插入列表
list.pop([index=-1])						#移除列表中的一个元素（默认最后一个值），并且返回该元素的值
list.remove(obj)							#移除列表中某个值的第一个匹配项
list.reverse()								#反向列表中的元素
list.sort(key=None,reverse=False)			#对原列表进行排序（key：指定一个函数，该函数从每个元素中提取一个用于比较											   的“键值”，reverse：布尔值，True 表示降序，False（默认）升序）
list.upper()								#全大写
list.lower()								#全小写
list.capitalize()							#首字母大写
list.title()								#首字母大写(每个单词首字母大写)
list.islower()								#检查是否全为小写
list.isdigit()								#检查是否全为数字
list.isupper()								#检查是否全部大写
list.isalpha()								#检查是否为字母
isinstance(object, classinfo)
'''
其中object是要检查的对象，classinfo可以是一个数据类型，也可以是由多个数据类型组成的元组。如果object是classinfo中任一类型的实例，或者是其子类的实例，isinstance()将返回True，否则返回False。

例如，检查一个变量是否是整数可以这样写：

a = 2
print(isinstance(a, int)) # 输出: True
'''

dict.fromkeys(list)							#去重
#字符串分割
chars = ['a', 'b', 'n']
result = ''.join(chars)   # 使用空字符串 '' 作为分隔符
print(result)

tuple()   元组

set()   集合

issubclass() 是 Python 内置函数，用于检查类之间的继承关系。
```

>```
>list_end = []
>list1 = input()
>list2 = list1.strip("[]")
>list3 = list2.split(",")
>for i in list3:
>    j = int(i)
>    list_end.append(j)
>
>best = []
>cur = [list_end[0]]
>
>for i in range(1, len(list_end)):
>    if list_end[i] > list_end[i - 1]:
>        cur.append(list_end[i])
>    else:
>        if len(cur) > len(best):
>            best = cur
>        cur = [list_end[i]]
>
>if len(cur) > len(best):
>    best = cur
>print(best)
>```

---

#### 五.异常处理

```
try:
    # 可能发生异常的代码
except pymysql.Error as e:
    # 捕获特定异常
    print(f"错误: {e}")
except Exception as e:
    # 捕获其他所有异常（谨慎使用）
    print(f"未知错误: {e}")
else:
    # 没有异常时执行（可选）
    print("操作成功")
finally:
	# 无论结果如何必须执行的代码
	pass
```

- `ZeroDivisionError`: 除数为零
- `IndexError`: 序列索引越界
- `KeyError`: 字典中键不存在
- `NameError`: 使用未定义的变量
- `FileNotFoundError`: 试图打开不存在的文件
- `ValueError`: 传入无效参数（如将"abc"转int）
- `TypeError`: 操作或函数类型不匹配
- `AttributeError`: 对象没有某属性
- `ImportError`: `import` 语句失败
- `AssertionError`: `assert` 断言失败

---

#### 六.日志记录

```
import logging

# 配置日志（一次配置，全局生效）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),   # 输出到文件
        logging.StreamHandler()           # 同时输出到控制台
    ]
)

# 使用
logging.debug("调试信息")      # 不会输出（因为 level=INFO）
logging.info("程序启动")
logging.warning("警告")
logging.error("错误", exc_info=True)   # exc_info 记录异常堆栈
logging.critical("严重错误")
```

> [!CAUTION]
>
> - 日志级别：DEBUG < INFO < WARNING < ERROR < CRITICAL
> - `exc_info=True` 可以记录完整的异常回溯信息，便于排查。
> - 生产环境推荐将日志输出到文件，并定期切割。

**format='%(asctime)s - %(levelname)s - %(message)s'常见占位符**

| 占位符          | 含义           | 示例值                    |
| :-------------- | :------------- | :------------------------ |
| `%(asctime)s`   | 日志记录的时间 | `2025-01-15 10:30:45,123` |
| `%(levelname)s` | 日志级别名称   | `INFO`, `ERROR`           |
| `%(message)s`   | 日志消息文本   | 你传入的字符串            |
| `%(name)s`      | 日志记录器名称 | 通常为 `__name__`         |
| `%(filename)s`  | 源文件名       | `monitor.py`              |
| `%(lineno)d`    | 行号           | `42`                      |
| `%(funcName)s`  | 函数名         | `main`                    |
| `%(process)d`   | 进程ID         | `1234`                    |
| `%(thread)d`    | 线程ID         | `5678`                    |

---

#### 七.时间

##### 1. 导入方式

```
from datetime import date, datetime, timedelta
```

- `date` – 处理年、月、日（没有时间部分）
- `datetime` – 处理年、月、日、时、分、秒、微秒
- `timedelta` – 表示时间差，用于日期时间的加减运算

------

##### 2. `date` 类（仅日期）

常用方法

```
from datetime import date

# 获取当前日期
today = date.today()
print(today)               # 2026-04-02
print(type(today))         # <class 'datetime.date'>

# 创建指定日期
d = date(2025, 12, 31)     # 年, 月, 日
print(d)                   # 2025-12-31

# 从字符串解析（ISO格式）
d2 = date.fromisoformat("2025-12-31")
print(d2)                  # 2025-12-31

# 获取单个属性
print(d.year)              # 2025
print(d.month)             # 12
print(d.day)               # 31

# 格式化输出（自定义格式）
print(d.strftime("%Y/%m/%d"))   # 2025/12/31
print(d.strftime("%B %d, %Y"))  # December 31, 2025

# 日期差值
delta = today - d
print(delta.days)          # 相差的天数（整数）

# 日期加减
from datetime import timedelta
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)
print(tomorrow, yesterday)
```

格式化代码（常用）

| 代码 | 含义          | 示例     |
| :--- | :------------ | :------- |
| `%Y` | 四位年份      | 2026     |
| `%y` | 两位年份      | 26       |
| `%m` | 月份（01-12） | 04       |
| `%d` | 日（01-31）   | 02       |
| `%B` | 完整月份名    | April    |
| `%b` | 缩写月份名    | Apr      |
| `%A` | 完整星期名    | Thursday |
| `%a` | 缩写星期名    | Thu      |

------

##### 3. `datetime` 类（日期 + 时间）

常用方法

```
from datetime import datetime

# 获取当前日期时间
now = datetime.now()
print(now)                 # 2026-04-02 15:30:45.123456

# 获取当前日期（不带时间）
today_date = datetime.today()  # 等价于 datetime.now()
print(today_date.date())   # 2026-04-02

# 创建指定日期时间
dt = datetime(2026, 4, 2, 14, 30, 0)   # 年,月,日,时,分,秒
print(dt)                  # 2026-04-02 14:30:00

# 从字符串解析（需指定格式）
dt2 = datetime.strptime("2026-04-02 14:30:00", "%Y-%m-%d %H:%M:%S")
print(dt2)

# 格式化为字符串
print(now.strftime("%Y-%m-%d %H:%M:%S"))   # 2026-04-02 15:30:45

# 获取时间戳（秒数，从1970-01-01开始）
timestamp = now.timestamp()
print(timestamp)           # 1743595845.123456

# 从时间戳恢复
dt3 = datetime.fromtimestamp(timestamp)
print(dt3)

# 日期时间差值
delta = now - dt
print(delta.total_seconds())  # 相差的总秒数

# 日期时间加减（与date类似，使用timedelta）
later = now + timedelta(hours=3, minutes=30)
print(later)
```

------

##### 4. `date` 与 `datetime` 的区别和转换

| 特性     | `date`                         | `datetime`                            |
| :------- | :----------------------------- | :------------------------------------ |
| 包含时间 | 否                             | 是                                    |
| 精度     | 天                             | 微秒                                  |
| 常用创建 | `date.today()`                 | `datetime.now()`                      |
| 相互转换 | `datetime.combine(date, time)` | `datetime.date()` / `datetime.time()` |

转换示例

```
from datetime import date, datetime, time

# datetime → date
now = datetime.now()
only_date = now.date()
print(only_date)           # 2026-04-02

# date → datetime（组合一个默认时间，如午夜）
today = date.today()
dt_midnight = datetime.combine(today, time.min)   # 2026-04-02 00:00:00
dt_custom = datetime.combine(today, time(14, 30)) # 2026-04-02 14:30:00
```

---

#### 八.Flask 后端接口开发笔记（速查版）

##### 1.环境准备

```
# 安装 Flask 及相关库
pip install flask flask-cors pymysql
# 如果普通用户无权限，加 --user
```

##### 2.最小 Flask 应用

```
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域（前后端分离必须）

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello World"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

- `@app.route(路径, methods=[请求方式])`：定义接口
- `jsonify(字典)`：返回 JSON 格式响应
- `debug=True`：代码改动自动重启

##### 3.接收前端数据

###### ①GET 请求参数（查询字符串）

```
@app.route('/api/search')
def search():
    keyword = request.args.get('keyword', '')   # 从 ?keyword=xxx 获取
    page = request.args.get('page', 1, type=int)
    return jsonify({"keyword": keyword, "page": page})
```

###### ② POST 请求（JSON 格式）

```
@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.get_json()          # 解析 JSON 请求体
    name = data.get('name')            # 安全取值，不存在返回 None
    age = data.get('age', 0)           # 可指定默认值
    return jsonify({"received": name})
```

###### ③POST 请求（表单格式）

```
@app.route('/api/form', methods=['POST'])
def form():
    name = request.form.get('name')
    return jsonify({"name": name})
```

##### 4.返回响应

###### ①返回 JSON + 状态码

```
return jsonify({"success": True, "data": ...}), 200
return jsonify({"error": "用户名已存在"}), 409
```

###### ②常用状态码

- 200 OK
- 201 Created（POST 成功）
- 400 Bad Request（参数错误）
- 401 Unauthorized（未登录）
- 403 Forbidden（无权限）
- 404 Not Found
- 409 Conflict（资源冲突，如用户名重复）
- 500 Internal Server Error

###### ③返回纯文本或 HTML

```
return "Hello", 200
return render_template('login.html')   # 需要 templates 文件夹
```

---

#### 九.Flask session 用法

session 就是一个服务器端的临时字典，用来记住用户登录状态。

##### 1. 准备工作：设置 `secret_key`

```
app = Flask(__name__)
app.secret_key = '你的随机字符串'   # 必须设置，否则 session 不工作
```

##### 2. 登录成功时：存入用户信息

```
from flask import session

session['user_id'] = 123
session['username'] = '张三'
```

##### 3. 在其他接口中：取出信息或判断是否登录

```
# 判断是否登录
if 'user_id' in session:
    user_id = session['user_id']      # 取出
    username = session.get('username') # 安全取出（不存在返回 None）
else:
    return jsonify({"error": "未登录"}), 401
```

##### 4. 登出时：清除 session

```
session.clear()   # 或者 session.pop('user_id')
```

---

## 集合（set）常用操作

| 方法                 | 说明                                         |
| :------------------- | :------------------------------------------- |
| `s.add(x)`           | 添加元素 x，如果已存在则无变化               |
| `s.update(iterable)` | 从可迭代对象中添加多个元素（相当于批量添加） |
| `s.remove(x)`        | 删除元素 x，若不存在则抛出 KeyError          |
| `s.discard(x)`       | 删除元素 x，若不存在也不报错                 |
| `s.pop()`            | 随机删除并返回一个元素（集合无序）           |
| `s.clear()`          | 清空集合                                     |
| `s.copy()`           | 返回集合的浅拷贝                             |
| `s.union()`          | 合并两个集合                                 |

**集合运算（返回新集合）**

- `s1 \| s2` 或 `s1.union(s2)`：并集
- `s1 & s2` 或 `s1.intersection(s2)`：交集
- `s1 - s2` 或 `s1.difference(s2)`：差集
- `s1 ^ s2` 或 `s1.symmetric_difference(s2)`：对称差集

------

## 字典（dict）常用操作

| 方法                  | 说明                                                         |
| :-------------------- | :----------------------------------------------------------- |
| `d[key] = value`      | 添加或修改键值对                                             |
| `d.update(d2)`        | 将字典 d2 的键值对合并到 d 中（覆盖同名键）                  |
| `d.get(key, default)` | 安全获取值，键不存在时返回 default（不报错）                 |
| `d.pop(key, default)` | 删除并返回 key 对应的值；若不存在且给了 default 则返回 default，否则报错 |
| `d.popitem()`         | 删除并返回最后插入的键值对（Python 3.7+ 按插入顺序）         |
| `d.keys()`            | 返回所有键的视图                                             |
| `d.values()`          | 返回所有值的视图                                             |
| `d.items()`           | 返回所有 (键, 值) 对的视图                                   |
| `d.clear()`           | 清空字典                                                     |
| `d.copy()`            | 浅拷贝字典                                                   |
| del d[“key”]          | 删除指定键值对                                               |
