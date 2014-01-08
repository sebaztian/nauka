#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 09:48:16 2013

@author: sgr
"""
import sys
import os


reload(sys)
sys.setdefaultencoding("utf-8")
import nltk
import random
import requests
import re
from flask import Flask,render_template,request,session,redirect
from redis_session import RedisSessionInterface
#from simplekv.fs import FilesystemStore
#from simplekv.memory import DictStore
#from flaskext.kvsession import KVSessionExtension

app = Flask(__name__)  
#store = FilesystemStore('./kvdata')
#store = DictStore()
#KVSessionExtension(store, app)

app.session_interface = RedisSessionInterface()

split_sign=';'
word_list=[]



def read_dict(dict_file):
    for line in open(dict_file,'r').readlines():
        if split_sign in line and line.strip()[0]!='#':

            split_res=line.partition(split_sign)
            word_list.append([split_res[0].strip(),split_res[2].strip(),0])

def init():
    
    if len(sys.argv)>1:  
        read_dict(sys.argv[1])
        return
    for dict_file in os.listdir('dicts/'):
        read_dict('dicts/'+dict_file)

def check_session():
    if 'word_list' not in session or not session['word_list']:
        get_words_to_session()
            
def get_words(number=20):
    random_list=[]
    if len(word_list)<=number :
        return word_list
    while (len(random_list)<number):
        random_word=word_list[random.randrange(0,len(word_list))]
        if random_word not in random_list:
            random_list.append(random_word)
    return random_list

def get_words_to_session(number=20):
    random_list=get_words(number)
    if 'word_list' in session:
        del session['word_list']
    session['word_list']=random_list

def count_vowels(word):
    counter=0    
    word_lower=word.lower()
    vowels=set(u'аеыуиоэюяё')
    for character in word_lower:
        if character in vowels:
            counter+=1
    return counter


@app.route("/") 
def menu():  
    check_session()
    return render_template('main.html') 

@app.route("/change") 
def change():
    
    try:
        get_words_to_session()
        return render_template('change.html',word_list=session['word_list'])
    except Exception,e:
        return str(e)        



@app.route("/show", methods=['GET','POST'])
@app.route("/show/<int:wid>", methods=['GET','POST'])
def show(wid=None):
    
    check_session()
    if 'last_show_word' not in session:
        session['last_show_word']=""
    while not wid:    
        wid_r=random.randrange(0,len(session['word_list']))
        if session['last_show_word']!=session['word_list'][wid_r][0] and len(session['word_list'])>1:
            wid=wid_r
    session['last_show_word']=session['word_list'][wid][0]
    return render_template('show.html',word=session['word_list'][wid])


@app.route("/choose", methods=['GET','POST'])
def choose():
    check_session()
    wid=random.randrange(0,len(session['word_list']))
    choose_list=[session['word_list'][wid][0]]
    while len(choose_list)<5:
        random_word=session['word_list'][random.randrange(0,len(session['word_list']))][0]
        if random_word not in choose_list:
            choose_list.append(random_word)
    random.shuffle(choose_list)
    try:
        return render_template('choose.html',word=session['word_list'][wid],choose_list=choose_list)
    except Exception, e:
        print str(e)

@app.route("/translate", methods=['GET','POST'])
def translate(wid=None):
    check_session()

    #if not wid:
    #    wid=random.randrange(0,len(session['word_list']))
    if 'prev_trans_word' in session and session['word_list'][0][0]==session['prev_trans_word'] and len(session['word_list'])>1:
        wid=1
    else:
        wid=0    
    for counter in range( len(session['word_list'])):
        if  session['word_list'][wid][2]>session['word_list'][counter][2] and session['word_list'][counter][0]!=session['prev_trans_word']:
            wid=counter

    session['prev_trans_word']=session['word_list'][wid][0]
    return render_template('translate.html',word=session['word_list'][wid])

@app.route("/wiki/<word>", methods=['GET','POST'])
def get_wiktionary(word):
    r = requests.get('http://ru.wiktionary.org/wiki/'+word)
    html=r.text
    search_list=[u"Им",u"Р",u"Д",u"В",u"Тв",u"Пр"]
    resdict={}
    try:
        for search_element in search_list:
            search_pattern = re.compile( search_element+u".</a></td>\s+<td bgcolor=\"\S+\">([^<]+)(<br />[^<]+)?</td>\s+<td bgcolor=\"\S+\">([^<]+)</td>", re.UNICODE )
            search_res=search_pattern.search(html)
            if search_res:
                resdict[search_element+'1']=search_res.group(1)
                resdict[search_element+'2']=search_res.group(3)
    except Exception,e:
        return str(e)
    return render_template('wiktionary.html',resdict=resdict,case_list=search_list)
    

def remove_stress_marks(text):
    text=text.strip()
    """
    text=text.replace('я́','я')
    text=text.replace('е́','е')
    text=text.replace('ы́','ы')
    text=text.replace('о́','о')
    text=text.replace('у́','у')
    text=text.replace('и́','и')
    text=text.replace('ю́','ю')
    text=text.replace('э́','э')   
    text=text.replace('а́','а')
    """
    text=text.replace(unichr(0x301),'')
    return text


def add_points(points,word):
    local_word_list=session['word_list']
    for element in local_word_list:
        if element[0]==word:
            element[2]+=points
            break
    local_word_list[:] = [tup for tup in local_word_list if tup[2]<50]
    session['word_list']=local_word_list


@app.route("/check", methods=['GET','POST'])    
def check():   
    if request.form and 'answer' in request.form and 'question' in request.form:
        if request.form['answer'].strip().lower()==request.form['question'].strip().lower():
            add_points(10,request.form['question'])
            if len(session['word_list'])==0:
                return redirect('/change')   
            return render_template('ok_reload.html')
        quest=remove_stress_marks(request.form['question'].strip())
        answer=remove_stress_marks(request.form['answer'].strip())
        if answer==quest:
            if count_vowels(quest)<2:
                add_points(10,request.form['question'])
                return render_template('ok_reload.html')
            add_points(-1,request.form['question'])
            return "OK! Brakuje akcentu. "+request.form['question']

    points=nltk.metrics.edit_distance(request.form['question'].strip().lower(),request.form['answer'].strip().lower())
        
    add_points((0-points),request.form['question'])

    return "NOT OK!!! "+request.form['question']+"<p class='small'>-"+str(points)+"</p> "

app.secret_key = 'A0Zr9rj/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":  
    init()
    get_words()
    app.run()
