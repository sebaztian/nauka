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

import random
from flask import Flask,render_template,request,session,redirect
word_list=[]
app = Flask(__name__)  

def init():

    for line in open('dict.txt','r').readlines():
        if '-' in line:
            split_res=line.split('-')
            word_list.append([split_res[0].strip(),split_res[1].strip()])

def check_session():
    if 'word_list' not in session:
        get_words_to_session()
            
def get_words(number=25):
    random_list=[]
    while len(random_list)<number:
        random_word=word_list[random.randrange(0,len(word_list))]
        if random_word not in random_list:
            random_list.append(random_word)
    return random_list

def get_words_to_session(number=25):
    random_list=get_words(number)
    session['word_list']=random_list

@app.route("/") 
def menu():  
    check_session()
    return render_template('main.html') 

@app.route("/change") 
def change():  
    get_words_to_session()
    return redirect('/')

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
    if not wid:
        wid=random.randrange(0,len(session['word_list']))
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
    
@app.route("/check", methods=['GET','POST'])    
def check():   
    if request.form and 'answer' in request.form and 'question' in request.form:
        if request.form['answer'].strip()==request.form['question'].strip():
            return render_template('ok_reload.html')
        quest=remove_stress_marks(request.form['question'])
        answer=remove_stress_marks(request.form['answer'])
        if answer==quest:          
            return "OK! Brakuje akcentu. "+request.form['answer']
    return "NOT OK!!! "+request.form['question']

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":  
    init()
    get_words()
    app.run()
