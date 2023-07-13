from flask import Blueprint, render_template, abort, jsonify, session
import math
from module.article import Article

index=Blueprint("index",__name__)

@index.route('/')
def home():
    article=Article()
    result=article.find_limit_with_user(0,10)
    total=math.ceil(article.get_total_count()/5) #向上取整
    last,most,recommended=article.find_last_most_recommended()
    return  render_template('index.html',result=result,total=total,page=1,last=last,most=most,recommended=recommended)
@index.route('/page/<int:page>')
def paginate(page):
    start=(page-1)*5
    article=Article()
    result=article.find_limit_with_user(start,5)
    total=math.ceil(article.get_total_count()/5) #向上取整
    return  render_template('index.html',result=result,total=total,page=page)

@index.route('/type/<int:type>-<int:page>')
def classify(type,page):
    start=(page-1)*5
    article=Article()
    result=article.find_by_type(type,start,5)
    total=math.ceil(article.get_count_by_type(type)/10)
    return render_template('type.html',result=result,total=total,page=page,type=type)
@index.route('/search/<int:page>-<keyword>')
def search(page,keyword):
    keyword=keyword.strip()
    if keyword is None or keyword=='' or '%' in keyword or len(keyword)>10:
        abort(404)
    start=(page-1)*5
    article=Article()
    result=article.find_by_headline(keyword,start,5)
    total=math.ceil(article.get_count_by_headline(keyword)/10)
    return render_template('search.html',result=result,page=page,keyword=keyword,total=total)
@index.route('/recommend')
def recommended():
    article = Article()
    last, most, recommended = article.find_last_most_recommended()
    last_ = []
    most_ = []
    recommended_ = []
    for (id, step) in last:
        step =(id, step)
        last_.append(step)
    for (id, step) in most:
        step =(id, step)
        most_.append(step)
    for (id, step) in recommended:
        step =(id, step)
        recommended_.append(step)
    list = []
    list.append(last_)
    list.append(most_)
    list.append(recommended_)
    return jsonify(list)
