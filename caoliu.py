# -*- coding:utf-8 -*-
'''
爬取某1024社区达盖尔旗帜的图片
需要 BeautifulSoup 库的支持
需要设置代理
'''
import urllib2
from bs4 import BeautifulSoup
import os

addr = 'http://t66y.com/thread0806.php?fid=16&page='
prefix = 'http://t66y.com/'

headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0'
          }

## 代理服务器设置 如果使用Goagent，应该不用修改
proxies = {
        'http': 'http://127.0.0.1:8087',
        'https': 'http://127.0.0.1:8087',
          }

proxy_handler = urllib2.ProxyHandler(proxies)
null_proxy_handler = urllib2.ProxyHandler({})

# 如果可以直接访问1024，这里可以换成 null_proxy_handler，但没有测试
opener = urllib2.build_opener(proxy_handler)
urllib2.install_opener(opener)

# 用作目录和文件名称时不合法的字符
invalidchars = ['?','\\','/',':','*','<','>','|','\"']


def process_str(oristr):
    for invalidchar in invalidchars:
        oristr = oristr.replace(invalidchar, '_')
    return oristr


def gethtml(url):
    req = urllib2.Request(url, headers = headers)
    try:
        response = urllib2.urlopen(url,timeout = 20)
    except Exception, e:
        print u"%s 打开失败" % url
        return ""
    else:
        try:
            thepage = response.read()
        except Exception, e:
            print u"%s 打开失败" % url
            return ""
        else:
            html = thepage.decode('gb2312','ignore')
            return html

def getpage(page):
    # 当前地址页
    url = addr + str(page)
    return gethtml(url)

'''
获取当前页面下所有帖子的标题和链接
'''
def findtiezi_link(html):
    # 获取soup
    soup = BeautifulSoup(html)

    # 分析 HTML 结构
    bigpage = soup.find('body').find('div', style = "margin:3px auto").find('tbody', style = "table-layout:fixed;")

    tmp = bigpage.find_all('tr', class_ = 'tr2')

    mountain = tmp[-1]

    trs = mountain.find_next_siblings('tr',class_ = "tr3 t_one")
    links = []
    titles = []

    for tr in trs:
        td = tr.find('td', style="text-align:left;padding-left:8px")
        h = td.find('h3')
        title = process_str(h.get_text())

        if os.path.exists(title):   # 当前已经有了这个帖子了
            print u'%s 已经下载过了，此次跳过' % (title)
            continue

        a = h.find('a')
        link = a.get('href')

        links.append(link)
        titles.append(title)

        #print >> outfile, "%s %s" %(link.encode('utf-8'), title.encode('utf-8'))
    return titles, links

'''
获取当前link下的图片
'''
def getimgs(titles, links):
    if titles == []:
        return
    idx = 0
    for link in links:
        title = titles[idx]
        idx = idx + 1

        print u'开始分析第 %d 个帖子的链接' % (idx)
        print u'帖子的题目是 %s' % title

        imglinks = []

        jumpurl = prefix + link

        html = gethtml(jumpurl)
        if html:
            soup = BeautifulSoup(html)
        else:
            continue

        inputs = soup.find('body').find('div', class_ = "tpc_content").find_all('input',recursive=True)

        for inp in inputs:
            imglink = inp.get('src')
            print imglink
            imglinks.append(imglink)

        mkdirname = title
        try:
            os.mkdir(mkdirname)
        except Exception, e:
            print u'无法创建目录 %s' % mkdirname
            continue
        print mkdirname

        print u'开始下载图片，帖子题目是 %s' %mkdirname

        for imglink in imglinks:
            try:
                imgreq = urllib2.urlopen(imglink,timeout = 20)
            except Exception, e:
                print u"%s 打开失败" % imglink
                continue
            else:
                try:
                    img = imgreq.read()
                except Exception, e:
                    print u"从链接读取图像失败 %s" % imglink
                    continue
                else:
                    surfix = imglink[-20:]
                    imgname = mkdirname+'/'+ process_str(surfix)
                    try:
                        with open(imgname, 'wb') as writter:
                            writter.write(img)
                    except Exception, e:
                        print u'不能写入图片 %s' %imgname
                        continue
                print u'图片 %s 处理完了' % imglink
        print u'第 %d 个帖子下载完了' % idx


start = 1
end = 5

for page in range(start, end + 1):
    print u'开始第 %d 页' % page

    html = getpage(page)

    if html:
        titles, links = findtiezi_link(html)
        print u'第 %d 页一共找到了 %d 个帖子' %(page, len(titles))
        getimgs(titles, links)
    print u'第 %d 页下载完了' % page

print u'全部任务完成'

