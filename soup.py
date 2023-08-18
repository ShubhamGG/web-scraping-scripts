#!/usr/bin/env python
import requests
import os
from urllib import url2pathname
from BeautifulSoup import BeautifulSoup
import shutil

def chap(url):
    content = ''
    while True:
        print 'getting '+url
        page = requests.get(url, allow_redirects=True,headers={ "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" })
        soup = BeautifulSoup(page.content)
        body = soup.find('div', attrs={'class': 'b-story-body-x x-r15'}).find('p')
        content = content + (body.prettify().replace('<br />', '</p><p>').replace('<p>\n</p>', ''))
        # Get the next button
        next = soup.find('a', attrs={'class': 'b-pager-next'})
        if next != None and next.text == 'Next':
            url = next.get('href')
        else:
            heading = soup.find('div', attrs={'class': 'b-story-header'}).find('h1')
            print heading.text
            content = heading.prettify() + content
            return content


url=raw_input('Enter URL: ')
title=raw_input('Enter Title: ')
if title.strip() == '':
    print 'Please enter a valid title'
    exit()
if os.path.isdir(title):
    shutil.rmtree(title,ignore_errors=True)
os.mkdir(title)
os.chdir(title)
page=requests.get(url, allow_redirects=True,headers={ "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" })

# Opening HTML file and starting writing
f = open('story.html','w')
f.write('<?xml version="1.0" encoding="UTF-8"?>\
<!DOCTYPE html><html xmlns:epub="http://www.idpf.org/2007/ops" xmlns="http://www.w3.org/1999/xhtml"><body>')

# Downloading the current chapter, assuming the url is the first page of it
soup = BeautifulSoup(page.content)
body = soup.find('div', attrs={'class': 'b-story-body-x x-r15'}).find('p') #Story body
author = soup.find('span',attrs={'class':'b-story-user-y x-r22'}).find('a').text
content=body.prettify().replace('<br />', '</p><p>').replace('<p>\n</p>', '')
nextbutt = soup.find('a', attrs={'class': 'b-pager-next'}) #URL to next page
if nextbutt != None and nextbutt.text == 'Next':
    # Downloading the rest of the pages in the chapter
    url = nextbutt.get('href')
    while True:
        print 'getting '+url
        page = requests.get(url, allow_redirects=True,headers={ "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36" })
        soup = BeautifulSoup(page.content)
        body = soup.find('div', attrs={'class': 'b-story-body-x x-r15'}).find('p')
        content = content + (body.prettify().replace('<br />', '</p><p>').replace('<p>\n</p>', ''))
        # Get the next button
        nextbutt = soup.find('a', attrs={'class': 'b-pager-next'})
        if nextbutt != None and nextbutt.text == 'Next':
            url = nextbutt.get('href')
        else:
            heading = soup.find('div', attrs={'class': 'b-story-header'}).find('h1')
            print heading.text
            content = heading.prettify() + content
            break
f.write(content)
content=''
# Getting links of all the chapters
chaps = soup.find('div',attrs={'class':'b-s-story-list t-4ut'})
if chaps:
	chaps = chaps.findAll('a',attrs={'class':'ser_link i-18k'})
	if len(chaps)>0:
	    for chapter in chaps:
	        ch = chapter.get('href')
	        f.write(chap(ch))

# Closing HTML file
f.write('</body></html>')
f.close()
#Writing other files to make epub
#Writing mimetype file
f=open('mimetype','w')
f.write(r'application/epub+zip')
f.close()
#Writing Title file
f=open('titlepage.xhtml','w')
f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html\nPUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\
<head>\
    <title>Cover</title></head><body style="text-align: center"><h1>'+title+'</h1><br/>'+author\
        +'</body></html>')
f.close()
#Writing Meta file
os.mkdir('META-INF')
os.chdir('META-INF')
f=open('container.xml','w')
f.write('<?xml version="1.0"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\
<rootfiles>\n<rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>\n</rootfiles>\
</container>')
f.close()
os.chdir('..')
#Writing contents list
f = open('content.opf','w')
f.write('<?xml version=\'1.0\' encoding=\'utf-8\'?>\n\
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uuid_id">\n\
    <metadata xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:opf="http://www.idpf.org/2007/opf"\
              xmlns:dc="http://purl.org/dc/elements/1.1/">\n\
        <dc:language>en</dc:language>\
        <dc:title>'+title+'</dc:title>\n\
        <dc:creator opf:file-as="AUTHOR" opf:role="aut">'+author+'/dc:creator>\n\
        <meta name="cover" content="cover"/>\n</metadata>\n<manifest>\n\
        <item href="story.html" id="id1" media-type="application/xhtml+xml"/>\n\
        <item href="titlepage.xhtml" id="titlepage" media-type="application/xhtml+xml"/>\n</manifest>\n\
    <spine toc="ncx">\n\
        <itemref idref="titlepage"/>\n\
        <itemref idref="id1"/>\n\
    </spine>\n\
    <guide>\n\
        <reference href="titlepage.xhtml" type="cover" title="Cover"/>\n\
    </guide>\n\
</package>')
f.close()

# Packaging to epub
print 'creating epub'
os.chdir('..')
shutil.make_archive(os.path.abspath(title),'zip',title)
shutil.rmtree(title)
os.rename(title+'.zip',title+'.epub')
