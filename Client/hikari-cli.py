import os, json, time, subprocess, requests
import sys


def judgePts(execPath,inData,outData,timeLimit,memLimit):
    #测试
    obj = subprocess.Popen([execPath],shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        obj.stdin.write(inData.encode('utf-8'))
        output,err = obj.communicate(timeout = timeLimit)
    except subprocess.TimeoutExpired:
        obj.kill()
        return {'status':'TLE','out':'(Time Limit Exceeded.)','ans':outData}
    
    if err:
        return {'status':'RE','out':err,'ans':outData}
        
    #比对程序输出
    if (((output.decode('utf-8')).replace('\n','')).replace(' ','')).strip() == (((outData).replace('\n','')).replace(' ','')).strip(): #去除回车和空格
        return {'status':'AC','out':output.decode('utf-8'),'ans':outData}
    else:
        return {'status':'WA','out':output.decode('utf-8'),'ans':outData}

def judge(data,code,language ='cpp'):
    try:
        os.mkdir('Temp')
    except Exception as e:
        #print("[Warning] Temp Folder Create Failed:",e)
        pass

    resultDict = {'status':'AC'}
    score = 0;pts = 0

    runID = str(time.time()) # 测试ID
    sourcePath ='Temp\\' + runID + '.' + language #源文件路径
    execPath =  'Temp\\' + runID + '.exe' #执行文件路径
    cplogPath = 'Temp\\' + runID + '.log' #编译信息路径
    # 写源文件
    with open(sourcePath,'w') as f:
        f.write(code)
    
    compileCommands = { #编译命令
        'cpp':f'Compilers\\Mingw64\\bin\\g++.exe {sourcePath} -o {execPath} > {cplogPath} 2>&1',
        'c':f'Compilers\\Mingw64\\bin\\gcc.exe {sourcePath} -o {execPath} > {cplogPath} 2>&1'
    }
    #执行编译
    os.system(compileCommands[language])

    compileLog = ''
    with open(cplogPath,'r') as f:
        compileLog = f.read()
    
    #找不到编译出的可执行文件，就报Compile Error
    if not os.path.exists(execPath):
        return {'status':'CE','log':compileLog,'pts':0,'score':0}
    else: resultDict['log'] = compileLog

    #逐点测试
    for i in data['data'].keys():
        resultDict[i] = judgePts(execPath,data['data'][i]['in'],data['data'][i]['out'],data['time_limit'],data['mem_limit'])
        score += data['data'][i]['score'] if resultDict[i]['status'] == 'AC' else 0 #如果AC加上对应score
        pts += 1 if resultDict[i]['status'] == 'AC' else 0
        if resultDict['status'] == 'AC' and resultDict[i]['status'] != 'AC':
            resultDict['status'] = resultDict[i]['status']

    #删除临时文件
    try:
        os.unlink(sourcePath)
        os.unlink(execPath)
        os.unlink(cplogPath)
        os.rmdir('Temp')
    except Exception as e:
        #print("[Warning] Unlink File Failed:",e)
        pass
    
    resultDict['score'] = score
    resultDict['pts'] = pts
    return resultDict    

"""
Usage:

with open("./1000.json",'r') as f:
        print(judge(json.loads(f.read()),'''
              #include <bits/stdc++.h>
              using namespace std;
              
              int main(){
                int a,b;
                cin>>a>>b;
                cout<<a+b;
                return 0;
              }
              ''','cpp'))

Json Example:
{
    "pid":1000,
    "time_limit":1,
    "mem_limit":1000,
    "data_cnt":2,
    "data":{
        "1":{"in":"1 1","out":"2","score":50},
        "2":{"in":"2 3","out":"5","score":50}
    }
}
"""

def judgeWithURL(dataURL,code,language='cpp'):
    try:
        jsonData = requests.get(dataURL)
        return judge(jsonData.json(),code,language)
    except Exception as e:
        print (e)
        return {'status':'UKE','log':str(e)}

#全流程测试
def judgeFlow(ojURL,uid,passwd,pid,code):
    dataURL = f'{ojURL}/data/{pid}'
    result = judgeWithURL(dataURL,code,'cpp')

    #上传结果
    try:
        postURL = f'{ojURL}/post_result'
        resultDict = { 
            'uid': uid,
            'passwd': passwd,
            'pid': pid,
            'code': code,
            'result': json.dumps(result)
        }
        res = (requests.post(url=postURL,data={'data':json.dumps(resultDict)})).json()
        if res['status'] == 404:
            result["upload_failure"] = True
            
        print(result)

    except Exception as e:
        print("Upload Result Failed.\n Exception:",str(e))

#                                      OJ网址           UID 密码明文 题号  测试文件
#传参方式：python hikari-cli.py "http://127.0.0.1:1919"  2   123456  1000 test.cpp 
if __name__ == '__main__':
    result = ''
    try:
        #从文件读取代码
        code = ''
        with open(sys.argv[5],'r') as f:
            code = f.read()
        
        judgeFlow(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],code)
    except Exception as e:
        print("Judge Failed.\n Exception:",str(e))

    
