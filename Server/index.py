from flask import Flask,request
import os, json, time, hashlib
import pymysql
from base64 import b64encode,b64decode

app = Flask(__name__)

db_host = 'localhost'
db_user = 'hikari'
db_password = 'YGZBsZ52rYpcATfE'
db_database = 'hikari'
db_port = 3306

#做3次MD5
def md5_3(x):
    x1 = hashlib.md5(x.encode()).hexdigest()
    x2 = hashlib.md5(x1.encode()).hexdigest()
    x3 = hashlib.md5(x2.encode()).hexdigest()
    return x3

@app.route('/data/<idx>')
def fetch_data(idx):
    if not os.path.exists(f'Data/{idx}.json'):
        return {'data_cnt':0,'Log':'Data Not Found'}
    
    data = []
    with open(f'Data/{idx}.json','r') as f:
        data = json.loads(f.read())
    
    for i in data['data'].values():
        del i['out']
        
    return data

@app.route('/')
def index():
    return {'status':200,'message':'Hello from Hikari Server.'}

@app.route('/post_result',methods=['POST'])
def receivePostResult():
    try:
        try:
            db = pymysql.connect(host=db_host,user=db_user,password=db_password,database=db_database,port=db_port)
            cursor = db.cursor()
        except Exception as e:
            print("Open Database Failed:",e)
        
        data = json.loads(request.form['data'])
        detail = json.loads(data['result'])
        
        cursor.execute("SELECT password FROM `user` WHERE `id`=%d" % (int(data['uid'])))
        result = cursor.fetchall()
        if len(result) == 0:
            print('[Post result] Invalid UID:',data['uid'])
            return {'status':404,'message':'Invalid UID.'}
        elif result[0][0] != data['passwd'] and md5_3(result[0][0]) != data['passwd']:
            print('[Post result] Bad Password:',data['uid'],data['passwd'])
            return {'status':404,'message':'Bad Password.'}
        
        #print(data)
        r_code = data['code'].replace("'","\\'").replace('"','\\"')
        r_status = detail['status']; del detail['status']
        r_score = 0;r_pts = 0
        r_log = detail['log'].replace("'","\\'").replace('"','\\"'); del detail['log']
        
        #判分
        with open(f'Data/{data['pid']}.json','r') as f:
            data00 = json.loads(f.read())
            data_cnt = data00['data_cnt']
            dataxx = data00['data']
            #print(data_cnt,dataxx)
        for i in detail.keys():
            detail[i]['ans'] = (dataxx[i]['out'])[:1000]
            if detail[i]['status'] == 'OK':
                if ((detail[i]['out'].replace('\n','')).replace(' ','')).strip() == ((dataxx[i]['out'].replace('\n','')).replace(' ','')).strip():
                    detail[i]['status'] = 'AC'
                    r_pts += 1
                    r_score += dataxx[i]['score']
                else:
                    detail[i]['status'] = 'WA'
                    if r_status == "OK":
                        r_status = "WA" 
            detail[i]['out'] = (detail[i]['out'])[:1000]
            
        if (r_pts == data_cnt):
            r_status = "AC"
        
        r_rid = str(int(time.time()*1000))
        ss = f'''INSERT INTO `record` (rid,pid,uid,code,stat,pts,score,log,detail)
        VALUES({r_rid},{data['pid']},{data['uid']},'{data['code']}','{r_status}',{r_pts},{r_score},'{r_log}','{b64encode((json.dumps(detail)).encode('utf-8')).decode('utf-8')}')'''
        
        #print(ss)
        cursor.execute(ss)
        db.commit()
        ss = f'SELECT * FROM `statistics` WHERE id in({data['uid']})';
        cursor.execute(ss)
        results = cursor.fetchall()
        if len(results) == 0:
            ss = f"INSERT INTO `statistics` VALUE({data['uid']},0,0,'[]',1000)";
            cursor.execute(ss)
            db.commit()
        else:
            xtmp = json.loads(results[0][3])
            if not data['pid'] in xtmp:
                ss = f"UPDATE `statistics` SET tot_submit = tot_submit+1"
                if r_status == 'AC':
                    ss += f",tot_ac = tot_ac + 1,rank = rank + 3,ac_detail=json_array_append(ac_detail,'$','{data['pid']}')"
                ss += f"where `id` = {data['uid']}"
                cursor.execute(ss)
                db.commit()
        
        db.close()
        
        detail['status'] = r_status
        detail['score'] = r_score
        detail['pts'] = r_pts
        detail['log'] = r_log
        detail['rid'] = r_rid
        return json.dumps(detail);
    except Exception as e:
        print("Error: ", str(e))
        return {'status':500,'message':str(e)}

if __name__=='__main__':
    app.run(port=1919,host='0.0.0.0',debug=True) 

   