import os, json

pid,timeLimit,memLimit,data_cnt = map(int,input("请输入PID、时间限制、空间限制、数据组数, 用空格分隔: ").split())
cnt = 0
data = {}
for inFile in os.listdir():
    if '.in' in inFile:
        cnt += 1
        outFile = inFile[:-3] + '.out'

        with open(inFile,'r') as f:
            inData = f.read()
        with open(outFile,'r') as f:
            outData = f.read()
        
        data[str(cnt)] = {'in':inData,'out':outData,'score':100//data_cnt}

print(json.dumps({
    'pid': pid,
    'time_limit': timeLimit,
    'mem_limit': memLimit,
    'data_cnt': data_cnt,
    'data': data
}))