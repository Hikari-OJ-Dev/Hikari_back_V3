from flask import Flask,request
import os, json, time
import pymysql
from base64 import b64encode,b64decode

app = Flask(__name__)

db_host = 'localhost'
db_user = 'hikari'
db_password = 'YGZBsZ52rYpcATfE'
db_database = 'hikari'
db_port = 3306

try:
    db = pymysql.connect(host=db_host,user=db_user,password=db_password,database=db_database,port=db_port)
    cursor = db.cursor()
except Exception as e:
    print("Open Database Failed:",e)


@app.route('/data/<id>')
def fetch_data(id):
    if not os.path.exists(f'Data/{id}.json'):
        return {'data_cnt':0,'Log':'Data Not Found'}
    
    with open(f'Data/{id}.json','r') as f:
        return json.loads(f.read())

@app.route('/')
def index():
    return {'status':200,'message':'Hello from Hikari Server.'}

@app.route('/post_result',methods=['POST'])
def receivePostResult():
    try:
        data = json.loads(request.form['data'])
        detail = json.loads(data['result'])
        
        r_code = data['code'].replace("'","\\'").replace('"','\\"')
        r_status = detail['status']; del detail['status']
        r_pts = detail['pts']; del detail['pts']
        r_score = detail['score']; del detail['score']
        r_log = detail['log'].replace("'","\\'").replace('"','\\"'); del detail['log']
        
        ss = f'''INSERT INTO `record` (rid,pid,uid,code,stat,pts,score,log,detail)
        VALUES({str(int(time.time()*1000))},{data['pid']},{data['uid']},'{data['code']}','{r_status}',{r_pts},{r_score},'{r_log}','{b64encode((json.dumps(detail)).encode('utf-8')).decode('utf-8')}')'''
        
        print(ss)
        cursor.execute(ss)
        results = cursor.fetchall()
        db.commit()
        return {'status':200}
    except Exception as e:
        print("Error: ", str(e))
        return {'status':500,'message':str(e)}

if __name__=='__main__':
    app.run(port=1919,host='0.0.0.0',debug=True) 

   