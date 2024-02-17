import webview, requests, os, configparser
import webview.menu as wm
from hikari_cli import judgeFlow

#检查config.ini是否存在
if os.path.exists("config.ini"):
    config = configparser.ConfigParser()
    config.read('config.ini')
    ojURL = config['Network']['URL']

else:
    ojURL = 'http://124.220.133.192'

ojFrontURL = ojURL + ':1243' #前端网址
ojBackURL = ojURL + ':1919' #后端网址


def submit(pid, uid, language, codeFile, clientID):
    window.load_html('<center><h1>正在评测，请稍等</h1></center>')
    print (pid, uid, language, codeFile, clientID)
    #print(ojFrontURL+ '/problem/Temp/' + codeFile) #代码文件路径
    code_c = (requests.get(ojFrontURL+ '/problem/Temp/' + codeFile)).text #获取代码
    res = judgeFlow(ojBackURL,uid,clientID,pid,code_c,language)
    #print(res)
    requests.get(ojFrontURL+ '/problem/submit?delete=' + codeFile) #删除云端临时文件
    window.load_url(ojFrontURL + f'/record/?id={res['rid']}') #跳转至结果页



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

if not os.path.exists("./Compilers/MinGW64"): #没有编译器，则报错
    winErr = webview.create_window(
        'Error', html='<html><head></head><body><center><h1>MingGW Not Found.</center></body></html>'
    )
    webview.start(winErr)
else: #正常启动
    window = webview.create_window('Hikari',ojFrontURL,width=1280,height=800,min_size=(900,600), text_select = True)
    window.expose(submit)
    webview.start(menu=menu_items, private_mode=False)
