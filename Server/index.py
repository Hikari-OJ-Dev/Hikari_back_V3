from flask import Flask,request
import os, json
app = Flask(__name__)

@app.route('/data/<id>')
def fetch_data(id):
    if not os.path.exists(f'Data/{id}.json'):
        return {'data_cnt':0,'Log':'Data Not Found'}
    
    with open(f'Data/{id}.json','r') as f:
        return json.loads(f.read())

@app.route('/')
def index():
    return {'stat':200,'message':'Hello from Hikari Server.'}

@app.route('/post_result',methods=['POST'])
def receivePostResult():
    data = json.loads(request.form['data'])
    print (data)

if __name__=='__main__':
    app.run(port=1919,host='0.0.0.0',debug=True) 