from flask import Blueprint, render_template, session
from module.users import Users

from module.comment import Comment
from module.favorite import Favorite
from module.article import Article
ucenter = Blueprint("ucenter", __name__)

@ucenter.route('/ucenter')
def user_center():
    result = Favorite().find_my_favorite()
    return render_template('user-center.html', result=result)

@ucenter.route('/user/favorite/<int:favoriteid>')
def user_favorite(favoriteid):
    canceled = Favorite().switch_favorite(favoriteid)
    return str(canceled)

@ucenter.route('/user/post')
def user_post():
    return render_template('user-post.html')
@ucenter.route('/user/mydraft')
def user_draft():
    userid=session['userid']
    result=Article().find_drafted_by_userid(userid=userid)
    print(result)
    return render_template('myDraft.html',result=result)
@ucenter.route('/user/hidDrafted-<int:articleid>')
def hidDrafted(articleid):
    hidden = Article().switch_hidden(articleid)
    print(hidden)
    return str(hidden)
@ucenter.route('/user/comment-<int:commentid>')
def hidcomment(commentid):
    hidden = Comment().switch_hidden(commentid)
    return str(hidden)
@ucenter.route('/user/hidArticle-<int:articleid>')
def hidArticle(articleid):
    hidden = Article().switch_hidden(articleid)
    print(hidden)
    return str(hidden)
@ucenter.route('/user/editDraft-<int:articleid>')
def editDraft(articleid):

    #根据articleid 查询出 headline和content
    result=Article().find_drafted_by_articleid(articleid)
    headline=result[0][0]
    content=result[0][1]
    return render_template('editDraft.html',headline=headline,content=content)
@ucenter.route('/user/myarticle')
def myarticle():
    userid=session['userid']
    result=Article().find_by_userid(userid=userid)
    return render_template('myArticle.html',result=result)
@ucenter.route('/user/mycomment')
def mycomment():
    #查询出comment 和 article
    result=Comment().find_my_comment()
    #
    # print(type(result[0][0]))
    return render_template('myComment.html',result=result)
@ucenter.route('/admin/adminComment')
def adminComment():
    #查询出comment 和 article
    result=Comment().find_all_comment()
    #
    # print(type(result[0][0]))
    return render_template('admin-Comment.html',result=result)

@ucenter.route('/user/info')
def myInfo():
    result=Users().find_user_info()
    return render_template('myInfo.html',result=result)