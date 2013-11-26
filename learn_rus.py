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
from flask import Flask,render_template,request,session,redirect
word_list=[]
app = Flask(__name__)  

def init():
    dict_file='dict.txt'
    split_sign='-'
    if len(sys.argv)>1:
        dict_file=sys.argv[1]
   
    for line in open(dict_file,'r').readlines():
        if split_sign in line and line.strip()[0]!='#':
            split_res=line.split(split_sign)
            word_list.append([split_res[0].strip(),split_res[1].strip(),0])

def check_session():
    if 'word_list' not in session:
        get_words_to_session()
            
def get_words(number=20):
    random_list=[]
    while (len(random_list)<number or len(random_list)==len(word_list)):
        random_word=word_list[random.randrange(0,len(word_list))]
        if random_word not in random_list:
            random_list.append(random_word)
    return random_list

def get_words_to_session(number=20):
    random_list=get_words(number)
    session['word_list']=random_list

@app.route("/") 
def menu():  
    check_session()
    return render_template('main.html') 

@app.route("/change") 
def change():  
    get_words_to_session()
    return render_template('change.html',word_list=session['word_list'])

@app.route("/show", methods=['GET','POST'])
@app.route("/show/<int:wid>", methods=['GET','POST'])
def show(wid=None):
    check_session()
    if not wid:
        wid=random.randrange(0,len(session['word_list']))
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
    wid=0    
    for counter in range( len(session['word_list'])):
        if  session['word_list'][wid][2]>session['word_list'][counter][2]:
            wid=counter
    return render_template('translate.html',word=session['word_list'][wid])


def remove_stress_marks(text):
    text=text.strip()
    text=text.replace('я́','я')
    text=text.replace('е́','е')
    text=text.replace('ы́','ы')
    text=text.replace('о́','о')
    text=text.replace('у́','у')
    text=text.replace('и́','и')
    text=text.replace('ю́','ю')
    text=text.replace('э́','э')   
    text=text.replace('а́','а')
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
        if request.form['answer'].strip()==request.form['question'].strip():
            add_points(10,request.form['question'])
            if len(session['word_list'])==0:
                return redirect('/change')
            return render_template('ok_reload.html')
        quest=remove_stress_marks(request.form['question'].strip())
        answer=remove_stress_marks(request.form['answer'].strip())
        if answer==quest:     
            add_points(-1,request.form['question'])
            return "OK! Brakuje akcentu. "+request.form['question']

    points=nltk.metrics.edit_distance(request.form['question'].strip(),request.form['answer'].strip())
        
    add_points((0-points),request.form['question'])

    return "NOT OK!!! "+request.form['question']+"<p class='small'>-"+str(points)+"</p> "

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":  
    init()
    get_words()
    app.run()
