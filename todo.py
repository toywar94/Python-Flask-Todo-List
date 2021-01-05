from flask import Flask, render_template, request, url_for, redirect

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

from datetime import datetime

from bson import ObjectId
import pymongo
import sys
import logging

class create(FlaskForm):
    #QuestionForm은 Flask-WTF의 FlaskForm 클래스를 상속받아 작성해야 한다.
    #첫번째 "내용" -> 폼 라벨, 두번째 validators 검증 도구로 필수 항목인지 체크
    content = StringField('내용', validators=[DataRequired()]) 

app = Flask(__name__, static_url_path='/static')
logging.basicConfig(level=logging.DEBUG)
app.config['SECRET_KEY'] = 'dev'
host = 'localhost'
conn = pymongo.MongoClient('mongodb://%s' %(host))
database = conn.todoList
todos = database.todo

@app.route("/todo")
def todo():
    return render_template('todo.html')

#All List 
@app.route("/allList")
def allList():
    title = "All List"
    todolist = todos.find().sort('date', -1)
    form = create()
    return render_template('allListTest.html',stat=title, todos=todolist, form=form)

#Active List
@app.route("/active")
def active():
    title = "Active List"
    todolist = todos.find({ "done" : "no"}).sort('date', -1)
    form = create()
    return render_template("allListTest.html", stat=title, todos=todolist, form=form)

#Completed List
@app.route("/completed")
def completed():
    title = "completed List"
    todolist = todos.find({ "done" : "yes"}).sort('date', -1) #-1 내림차순
    form = create()
    return render_template("allListTest.html", stat=title, todos=todolist, form=form)

# update
@app.route("/update")
def update_page():
    print("dkfjkldafj;dajdklfjldsjfd")
    id=request.values.get("_id")
    task=todos.find({"_id":ObjectId(id)})[0]
    form = create()
    return render_template('update.html', task=task, form=form)



#input memo
@app.route("/action", methods=['POST', 'GET'])
def action_input():
    form = create()
    if form.validate_on_submit(): # POST로 전송된 폼 데이터의 접합성을 체크한다 ->DataRequired()
        contents = request.form['content'] #html ->content 내용값을 받음.
        date = datetime.today()
        todos.insert_one({ "contents" : contents, "date" : date, "done" : "no" })
        return """<script>
			window.location = document.referrer;
			</script>"""
    else:
        return render_template("error.html")

#memo change
@app.route("/change")
def change():
    id = request.values.get("_id")
	#task = todos.find({}, {_id:1})
    task=todos.find({"_id":ObjectId(id)})

    if(task[0]["done"]=="yes"):
    	todos.update_one({"_id":ObjectId(id)}, {"$set": {"done":"no"}})
    else:
	    todos.update_one({"_id":ObjectId(id)}, {"$set": {"done":"yes"}})
    return """<script>
		window.location = document.referrer;
		</script>"""
	

#Delete memo
@app.route("/delete")
def delete():
	key=request.values.get("_id")
	todos.delete_one( { "_id" : ObjectId(key)} )
	return """<script>
		window.location = document.referrer;
		</script>"""

#Done memo update
@app.route("/submit", methods=['GET','POST'])
def done_update():

    if request.method == 'GET':
        print("am i here??")
        key = request.values.get("_id")
        contents = request.form['content']
        print(contents)
        todos.update_one({"_id":ObjectId(key)}, {'$set':{"contents":contents}})
        return redirect(url_for('allList'))
    else:
        return render_template("error.html")

        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080')