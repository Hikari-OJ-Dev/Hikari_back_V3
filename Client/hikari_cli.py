import os, json, time, subprocess, requests, hashlib, sys

#做3次MD5
def md5_3(x):
    x1 = hashlib.md5(x.encode()).hexdigest()
    x2 = hashlib.md5(x1.encode()).hexdigest()
    x3 = hashlib.md5(x2.encode()).hexdigest()
    return x3

def judgePts(execPath,inData,timeLimit,memLimit):
    #测试
    obj = subprocess.Popen([execPath],shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        obj.stdin.write(inData.encode('utf-8')) #将输入数据传递给评测进程
        output,err = obj.communicate(timeout = timeLimit) #获取进程输出
    except subprocess.TimeoutExpired: #超时
        obj.kill() #杀掉进程
        return {'status':'TLE','out':'(Time Limit Exceeded.)'}
    
    if err: #有错误信息，则报RE
        return {'status':'RE','out':err}
        
    #输出
    #if (((output.decode('utf-8')).replace('\n','')).replace(' ','')).strip() == (((outData).replace('\n','')).replace(' ','')).strip(): #去除回车和空格
    return {'status':'OK','out':output.decode('utf-8')}

def judge(data,code,language ='cpp'):
    try: #尝试创建Temp目录
        os.mkdir('Temp')
    except Exception as e:
        #print("[Warning] Temp Folder Create Failed:",e)
        pass

    resultDict = {'status':'OK'}

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

    #读取编译信息
    compileLog = ''
    with open(cplogPath,'r') as f:
        compileLog = f.read()
    
    #找不到编译出的可执行文件，就报Compile Error
    if not os.path.exists(execPath):
        return {'status':'CE','log':compileLog}
    else: resultDict['log'] = compileLog

    #逐点测试
    for i in data['data'].keys():
        resultDict[i] = judgePts(execPath,data['data'][i]['in'],data['time_limit'],data['mem_limit'])
        if resultDict['status'] == 'OK' and resultDict[i]['status'] != 'OK':
            resultDict['status'] = resultDict[i]['status']

    #尝试删除临时文件
    try:
        os.unlink(sourcePath)
        os.unlink(execPath)
        os.unlink(cplogPath)
        os.rmdir('Temp')
    except Exception as e:
        #print("[Warning] Unlink File Failed:",e)
        pass
    
    return resultDict    

"""
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

#从URL获取数据并评测
def judgeWithURL(dataURL,code,language='cpp'):
    try:
        jsonData = (requests.get(dataURL)).json() #获取数据并转化为dict
        #print(jsonData)
        if jsonData['data_cnt'] == 0: #若data_cnt为0，则报PID错误
            print ({'status':'Bad PID.'})
            exit(0)

        return judge(jsonData,code,language) #执行评测
    except Exception as e:
        print (e)
        return {'status':'UKE','log':str(e)}

#全流程测试
def judgeFlow(ojURL,uid,passwd,pid,code,language = 'cpp'):
    dataURL = f'{ojURL}/data/{pid}' #获取数据的URL
    result = judgeWithURL(dataURL,code,language) #评测
    #print(result)
    #上传结果
    try:
        postURL = f'{ojURL}/post_result' #POST数据的URL
        resultDict = { 
            'uid': uid, #用户ID
            'passwd': md5_3(passwd), #加密后的用户密码
            'pid': pid, #题目ID
            'code': code, #代码
            'result': json.dumps(result) #评测结果
        }
        res = (requests.post(url=postURL,data={'data':json.dumps(resultDict)})).json() #执行POST
        if res['status'] == 404:
            res["upload_failure"] = True
            
        print(res) #输出结果
        return res

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
        
        #执行评测
        judgeFlow(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],code)
    except Exception as e:
        print("Judge Failed.\n Exception:",str(e))

    
