from flask import Flask, render_template, request, redirect, url_for, session, make_response
import os
import pymysql
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='template', static_folder='resource', static_url_path='/')
# SECRET_KEY 启用Session必须配置
app.config['SECRET_KEY'] = os.urandom(24)  # 生成随机数种子，用于产生SessionID

pymysql.install_as_MySQLdb()
# 使用集成方法处理SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@39.104.207.156:3306/woniunote?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 实例化db对象
db = SQLAlchemy(app)


# 定义全局拦截器，实现自动登录
@app.before_request
def before():
    url = request.path
    pass_list = ['/user', '/login', '/logout']
    if url in pass_list or url.endswith('.js') or url.endswith('.jpg'):
        pass

    elif session.get('islogin') is None:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if username != None and password != None:
            user = Users()
            result = user.find_by_username(username)
            if len(result) == 1 and result[0].password == password:
                session['islogin'] = 'true'
                session['userid'] = result[0].userid
                session['username'] = username
                session['nickname'] = result[0].nickname
                session['role'] = result[0].role


# 定制404错误页面 请求的网页不存在
@app.errorhandler(404)
def page_not_found_404(e):
    return render_template('error-404.html')


# 定制500错误页面 500服务器内部错误
@app.errorhandler(500)
def page_not_found_500(e):
    return render_template('error-500.html')


# 定义文章类型函数
@app.context_processor
def gettype():
    type = {
        '1': 'PHP开发',
        '2': 'JAVA开发',
        '3': 'Python开发',
        '4': 'Web前端',
        '5': '测试开发',
        '6': '数据科学',
        '7': '网络安全',
        '8': '蜗牛杂谈'
    }
    return dict(article_type=type)


# 通过自定义过滤器来重构truncate原生过滤器
def mytruncate(s, length, end='...'):
    count = 0
    new = ''
    for c in s:
        new += c
        if ord(c) <= 128:
            count += 0.5
        else:
            count += 1
        if count > length:
            break
    return new + end


app.jinja_env.filters.update(truncate=mytruncate)
if __name__ == '__main__':
    from controller.index import *
    app.register_blueprint(index)

    from controller.user import *
    app.register_blueprint(user)

    from controller.article import *
    app.register_blueprint(article)

    from controller.favorite import *
    app.register_blueprint(favorite)

    from controller.ueditor import *
    app.register_blueprint(ueditor)

    from controller.admin import *
    app.register_blueprint(admin)

    from controller.ucenter import *
    app.register_blueprint(ucenter)

    from controller.comment import *
    app.register_blueprint(comment)
    app.run(debug=True)
