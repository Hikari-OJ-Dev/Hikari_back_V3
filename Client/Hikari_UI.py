import webview, requests
from hikari_cli import judgeFlow

ojURL = 'http://124.220.133.192'
ojFrontURL = ojURL + ':1243'
ojBackURL = ojURL + ':1919'

def submit(pid, uid, language, codeFile, Passwd):
    print (pid, uid, language, codeFile, Passwd)
    #print(ojFrontURL+ '/problem/Temp/' + codeFile)
    code_c = (requests.get(ojFrontURL+ '/problem/Temp/' + codeFile)).text
    res = judgeFlow(ojBackURL,uid,Passwd,pid,code_c,language)
    #print(res)
    requests.get(ojFrontURL+ '/problem/submit?delete=' + codeFile)
    window.evaluate_js(f'window.location="/record/?id={res['rid']}"')

window = webview.create_window('Hikari',ojFrontURL)
window.expose(submit)
webview.start()

