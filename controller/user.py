import hashlib
import os
import re

from flask import Blueprint, make_response, session, request, redirect, url_for, render_template
from common.utility import ImageCode, gen_email_code, send_email, parse_image_url, generate_thumb
from module.article import Article
from module.credit import Credit
from module.users import Users

user=Blueprint('user',__name__)


@user.route('/vcode')
def vcode():
    code, bstring = ImageCode().get_code() #获取到验证码图片的值和二进制数据
    response = make_response(bstring)#定义图片的响应
    response.headers['Content-Type'] = 'image/jpeg' #定义响应头的格式为图片
    session['vcode'] = code.lower() #存到session  即存到内存
    return response

@user.route('/ecode', methods=['POST'])
def ecode():
    email = request.form.get('email')
    if not re.match('.+@.+\..+', email):
        return 'email-invalid'
    code = gen_email_code()
    try:
        send_email(email, code)
        session['ecode'] = code # 将邮箱验证码保存在Session中
        return 'send-pass'
    except:
        return 'send-fail'

@user.route('/user', methods=['POST','GET'])
def register():
    user = Users()
    username = request.form.get('username')
    password = request.form.get('password')
    ecode = request.form.get('ecode')
    # 校验邮箱验证码是否正确
    if ecode != session.get('ecode'):
        return 'ecode-error'
    # 验证邮箱地址的正确性和密码的有效性
    elif not re.match('.+@.+\..+', username) or len(password) < 5:
        return 'up-invalid'
    # 验证用户是否已经注册
    elif len(user.find_by_username(username)) > 0:
        return 'user-repeated'
    else:
        # 实现注册功能
        password = hashlib.md5(password.encode()).hexdigest()#加密
        result = user.do_register(username, password)
        #缓存用户信息
        session['islogin'] = 'true'
        session['userid'] = result.userid
        session['username'] = username
        session['nickname'] = result.nickname
        session['role'] = result.role
        # 更新积分详情表
        Credit().insert_detail(type='用户注册',target='0',credit=50)
        return 'reg-pass'

@user.route('/password_back', methods=['POST','GET'])
def password_back():
    user = Users()
    username = request.form.get('username')
    password = request.form.get('password')
    ecode = request.form.get('ecode')
    # 校验邮箱验证码是否正确
    if ecode != session.get('ecode'):
        return 'ecode-error'
    # 验证邮箱地址的正确性和密码的有效性
    elif not re.match('.+@.+\..+', username) or len(password) < 5:
        return 'up-invalid'
    # 验证用户是否已经注册
    elif len(user.find_by_username(username)) > 0:
        # 实现注册功能
        print(password)
        password = hashlib.md5(password.encode()).hexdigest()#加密
        result = user.password_back(username, password)
        #缓存用户信息
        session['islogin'] = 'true'
        session['userid'] = result.userid
        session['username'] = username
        session['nickname'] = result.nickname
        session['role'] = result.role
        # 更新积分详情表
        # Credit().insert_detail_passwordBack(type='正常登录',target='0',credit=1)
        return 'password-back'

    else:
        return 'user-none'
@user.route('/login', methods=['POST'])
def login():
    user = Users()
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    vcode = request.form.get('vcode').lower().strip()

    # 校验图形验证码是否正确
    if vcode != session.get('vcode') and vcode != '0000':
        return 'vcode-error'

    else:
        # 实现登录功能
        password = hashlib.md5(password.encode()).hexdigest()
        result = user.find_by_username(username)
        print(len(result))
        if len(result) == 1 and result[0].password==password:
            session['islogin'] = 'true'
            session['userid'] = result[0].userid
            session['username'] = username
            session['nickname'] = result[0].nickname
            session['role'] = result[0].role
            # 更新积分详情表
            Credit().insert_detail(type='正常登录',target='0',credit=1)
            user.update_credit(1)
            # 将Cookie写入浏览器
            response = make_response('login-pass')
            response.set_cookie('username', username, max_age=30*24*3600)
            response.set_cookie('password', password, max_age=30*24*3600)
            return response
        else:
            return 'login-fail'
@user.route('/logout')
def logout():
    #清空session和cookie，页面跳转
    session.clear()
    response=make_response('注销并重定向',302)
    response.headers['Location'] = url_for('index.home')
    response.delete_cookie('username')
    response.set_cookie('password', '', max_age=0)

    return response
@user.route('/user/prepost')
def user_prepost():
    return render_template('user-prepost.html')

@user.route('/add_drafted',methods=['POST'])
def add_drafted():
    headline = request.form.get('headline')
    content = request.form.get('content')
    type = int(request.form.get('type'))
    credit = int(request.form.get('credit'))
    drafted = 1
    checked = 0
    articleid = int(request.form.get('articleid'))
    print(headline)
    if session.get('userid') is None:
        return 'perm-denied'
    else:
        print('session.get(userid)',session.get('userid'))
        user = Users().find_by_userid(session.get('userid'))
        if user.role == 'user':
            # 权限合格，可以执行发布文章的代码
            # 首先为文章生成缩略图，优先从内容中找，找不到则随机生成一张
            url_list = parse_image_url(content)
            print('url_list', url_list)
            if len(url_list) > 0:  # 表示文章中存在图片
                thumbname = generate_thumb(url_list)
            else:
                # 如果文章中没有图片，则根据文章类别指定一张缩略图
                thumbname = '%d.png' % type

            article = Article()
            # 再判断articleid是否为0，如果为0则表示是新数据
            if articleid == 0:
                try:
                    id = article.insert_article(type=type, headline=headline, content=content, credit=credit,
                                                thumbnail=thumbname, drafted=drafted, checked=checked)
                    # 新增文章成功后，将已经静态化的文章列表页面全部删除，便于生成新的静态文件
                    # list = os.listdir('./template/index-static/')
                    # for file in list:
                    #     os.remove('./template/index-static/' + file)
                    return str(id)
                except Exception as e:
                    return 'post-fail'
            else:
                # 如果是已经添加过的文章，则做修改操作
                try:
                    id = article.update_article(articleid=articleid, type=type,
                                                headline=headline, content=content, credit=credit,
                                                thumbnail=thumbname, drafted=drafted, checked=checked)
                    return str(id)
                except:
                    return 'post-fail'

        # 如果角色不是作者，则只能投稿，不能正式发布
        # elif checked == 1:
        #     return 'perm-denied'
        # else:
        #     return 'perm-denied'
