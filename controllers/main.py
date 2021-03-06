import sys
import os
import logging
sys.path.insert(1, '../models')
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import and_
from config import DevConfig
from tokens import Tokens
from departments import Departments
from streams import Streams
from admins import Admins
from counters import Counters
template_dir = os.path.abspath('../templates')
static_dir = os.path.abspath('../static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(DevConfig)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/version_1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Admin related function 
@app.route('/admin')
def admin():
    return render_template('admin.html')
@app.route('/dashboard')
def dashboard():
    return 'Dashboard'


#Token related functions
def _get_current_token():
    from datetime import datetime, timedelta
    today = datetime.today().date()
    tokens = Tokens.query.filter(Tokens.date > today).all()
    if tokens:
        last_token = tokens[-1].token_day_number
        last_token = int(last_token)
        current_token = last_token + 1
        current_token = str(current_token).zfill(3)
        return current_token
    else:
        return "001"
    logging.critical(last_token)
@app.route('/', methods=['GET', 'POST'])
@app.route('/token_interface', methods=['GET', 'POST'])
def token_interface():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        dept_id = request.form['departments']
        stream_id = request.form['streams']
        token_day_number = _get_current_token()
        attending = 1
        token = Tokens(token_day_number=token_day_number, phone_number=phone_number,
                        department=dept_id, stream=stream_id)
        db.session.add(token)
        db.session.commit()
        dept_name = Departments.query.filter_by(id=dept_id).first().name
        stream_name = Streams.query.filter_by(id=stream_id).first().name
        return render_template('generated_token.html', dept_name=dept_name, 
            token_number=token_day_number, attending=attending, token=token, stream_name=stream_name)
    departments = Departments.query.all()
    streams = Streams.query.all()
    return render_template('token_interface.html', departments= departments, streams=streams)
@app.route('/token_list')
def tokens_list():
    tokens = Tokens.query.filter_by().all()
    departments = Departments
    streams = Streams
    return render_template('token.html', tokens=tokens, streams= streams, departments=departments)

#Departments related functions
@app.route('/departments/new',  methods=['GET', 'POST'])
def create_new_department():
    if request.method == 'POST':
        name = request.form['name']
        dept = Departments(name=name)
        db.session.add(dept)
        db.session.commit()
        return redirect('/departments_list')
    return render_template('new_department.html')
@app.route('/departments/edit/<int:dept_id>', methods=['GET', 'POST'])
def edit_department(dept_id):
    department = Departments.query.filter_by(id=dept_id).first()
    if request.method == 'POST':
        name = request.form['name']
        dept_name = Departments.query.filter_by(id=dept_id).first()
        dept_name.name = name
        db.session.merge(dept_name)
        db.session.commit()
        return redirect('/departments_list')
    return render_template('dept_edit.html', department=department)
@app.route('/departments/delete/<int:dept_id>')
def delete_department(dept_id):
    department = Departments.query.filter_by(id=dept_id).first()
    current_db_session = db.session.object_session(department)
    current_db_session.delete(department)
    current_db_session.commit()
    departments = Departments.query.all()
    return redirect('/departments_list')
@app.route('/departments_list')
def departments_list():
    departments = Departments.query.all()
    return render_template('departments.html',departments=departments)

#Streams related functions

@app.route('/streams_list')
def streams_list():
    streams = Streams.query.all()
    departments = Departments
    return render_template('streams.html',streams=streams, departments=departments)
@app.route('/streams/new',  methods=['GET', 'POST'])
def create_new_stream():
    if request.method == 'POST':
        name = request.form['name']
        dept_id = request.form['departments']
        stream = Streams(name=name, dept_id=dept_id)
        db.session.add(stream)
        db.session.commit()
        return redirect('/streams_list')
    departments = Departments.query.all()
    return render_template('new_stream.html', departments=departments)
@app.route('/streams/edit/<int:stream_id>', methods=['GET', 'POST'])
def edit_stream(stream_id):
    stream = Streams.query.filter_by(id=stream_id).first()
    if request.method == 'POST':
        name = request.form['name']
        dept_id = request.form['departments']
        stream = Streams.query.filter_by(id=stream_id).first()
        stream.name = name
        stream.dept_id = dept_id
        db.session.merge(stream)
        db.session.commit()
        return redirect('/streams_list')
    departments = Departments.query.all()
    return render_template('stream_edit.html', stream=stream, departments=departments)
@app.route('/streams/delete/<int:stream_id>')
def delete_stream(stream_id):
    stream = Streams.query.filter_by(id=stream_id).first()
    current_db_session = db.session.object_session(stream)
    current_db_session.delete(stream)
    current_db_session.commit()
    return redirect('/streams_list')

#Counters related functions

@app.route('/counters_list')
def counters_list():
    counters = Counters.query.all()
    return render_template('counters.html',counters=counters)
@app.route('/counters/new',  methods=['GET', 'POST'])
def create_new_counter():
    if request.method == 'POST':
        name = request.form['name']
        counter = Counters(name=name)
        db.session.add(counter)
        db.session.commit()
        return redirect('/counters_list')
    return render_template('new_counter.html')
@app.route('/counters/edit/<int:counter_id>', methods=['GET', 'POST'])
def edit_counter(counter_id):
    counter = Counters.query.filter_by(id=counter_id).first()
    if request.method == 'POST':
        name = request.form['name']
        counter = Counters.query.filter_by(id=counter_id).first()
        counter.name = name
        db.session.merge(counter)
        db.session.commit()
        return redirect('/counters_list')
    return render_template('counter_edit.html', counter=counter)
@app.route('/counters/delete/<int:counter_id>')
def delete_counter(counter_id):
    counter = Counters.query.filter_by(id=counter_id).first()
    current_db_session = db.session.object_session(counter)
    current_db_session.delete(counter)
    current_db_session.commit()
    return redirect('/counters_list')

#Queue processing related functions
@app.route('/queue/processing/dashboard/<int:counter_id>', methods=['GET', 'POST'])
def queue_processing_dashboard(counter_id):
    departments = Departments.query.all()
    streams = Streams.query.all()
    if request.method == 'POST':
        dept_id = request.form['departments']
        stream_id = request.form['streams']
        counter_id = counter_id
        from datetime import datetime, timedelta
        today = datetime.today().date()
        tokens = Tokens.query.filter(and_(Tokens.date > today, Tokens.state == 'waiting', Tokens.department == dept_id, 
                        Tokens.stream == stream_id)).all()
        departments = Departments
        streams = Streams
        counters = Counters
        return render_template('queue_processing.html', dept_id=dept_id, stream_id=stream_id, counter_id=counter_id, 
                              tokens=tokens, counters=counters, departments=departments, streams=streams)
    return render_template('queue_dashboard.html', streams=streams, departments=departments)

@app.route('/counter/login', methods=['GET', 'POST'])
def counter_login():
    if request.method == 'POST':
        name = request.form['name']
        try:
            counter_id = Counters.query.filter(Counters.name == name).first().id  
            return redirect('/queue/processing/dashboard/{0}'.format(counter_id))
        except Exception as exp:
            error = "Counter does not exist"
            logging.critical(exp)
            return render_template('login_counter.html', error=error)
    counters = Counters.query.all()
    return render_template('login_counter.html', counters=counters)
if __name__ == '__main__':
    app.run(DEBUG=True)