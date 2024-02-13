import webview, requests, os
import webview.menu as wm
from hikari_cli import judgeFlow

ojURL = 'http://124.220.133.192'
ojFrontURL = ojURL + ':1243'
ojBackURL = ojURL + ':1919'

def submit(pid, uid, language, codeFile, Passwd):
    window.load_html('<center><h1>正在评测，请稍等</h1></center>')
    print (pid, uid, language, codeFile, Passwd)
    #print(ojFrontURL+ '/problem/Temp/' + codeFile)
    code_c = (requests.get(ojFrontURL+ '/problem/Temp/' + codeFile)).text
    res = judgeFlow(ojBackURL,uid,Passwd,pid,code_c,language)
    #print(res)
    requests.get(ojFrontURL+ '/problem/submit?delete=' + codeFile)
    window.load_url(ojFrontURL + f'/record/?id={res['rid']}')



def homePage():
    window.load_url(ojFrontURL)

def goBack():
    window.evaluate_js('history.go(-1)');

def goForth():
    window.evaluate_js('history.go(1)');

def showAbout():
    window.create_confirmation_dialog('关于','''          
     Proudly Powered by Hikari-Frontend
  Main Contributers: Tianyu Wang, Zichen Wang''')
menu_items = [
        wm.MenuAction('主页', homePage),
        wm.MenuAction('后退', goBack),
        wm.MenuAction('前进', goForth),
        wm.MenuAction('关于', showAbout),
    ]

if not os.path.exists("./Compilers/MinGW64"):
    winErr = webview.create_window(
        'Error', html='<html><head></head><body><center><h1>MingGW Not Found.</center></body></html>'
    )
    webview.start(winErr)
else:
    window = webview.create_window('Hikari',ojFrontURL,width=1280,height=800,min_size=(900,600), text_select = True)
    window.expose(submit)
    webview.start(menu=menu_items)

