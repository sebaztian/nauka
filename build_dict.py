#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os


reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import re
import nltk

def get_accent_for_word(word):
    r = requests.get('http://ru.wiktionary.org/wiki/'+word)
    html=r.text
    clean_html=nltk.clean_html(html)
    search_pattern = re.compile( u'Им\.\s+(.*)', re.UNICODE )
    if u'Глагол' in clean_html:
        search_pattern = re.compile( u'буду/будешь…\s+(.*)',re.UNICODE )
    res=search_pattern.search(clean_html)
    if res:
        accented=re.sub("\s\s+" , " ", res.group(1))
        return accented
    else:
        with open('wiki_no_accent_dict.txt', 'a') as f:
            f.write(word+'\n')
        with open('wiki_no_accent_log.txt', 'a') as f:
            f.write('----------\n'+word+':\n'+clean_html+'----------\n')            
        return False

def get_words(last_word=""):
    r = requests.get('http://pl.wiktionary.org/w/index.php?title=Kategoria:rosyjski_%28indeks%29&pagefrom='+last_word)
    html=r.text
    #<li><a href="/wiki/%D0%B0%D0%B1%D0%B1%D0%B0%D1%82" title="аббат">аббат</a></li>
    search_pattern = re.compile( '<li><a href="/wiki/\S+" title="([^\"]+)">([^<]+)</a></li>', re.UNICODE )
    word_list=[]    
    for match in search_pattern.finditer(html): 
        if 'Kategoria' not in match.group(1):
            word_list.append(match.group(2))
    return word_list

def get_translation(word):
    r = requests.get('http://pl.wiktionary.org/wiki/'+word)
    html=r.text
    
    
    clean_html=nltk.clean_html(html)
    
    clean_html=clean_html[clean_html.find(u'język rosyjski ) [ edytuj ]'):]
    clean_html=clean_html[:clean_html.find(u'odmiana')]
    trasnlation_search=re.search('znaczenia\s*\:\s+(.*)',clean_html,re.DOTALL)
    if trasnlation_search:
        translation=re.sub("\s\s+" , " ", trasnlation_search.group(1))
        return translation
    return False

last_word='а'
while last_word:
    unstressed_word_list=get_words(last_word)
    stressed_list=[]
    for unstressed_word in unstressed_word_list:
        stressed=get_accent_for_word(unstressed_word)
        translation=get_translation(unstressed_word)
        if stressed and translation:    
            stressed_list.append([stressed,translation])
    with open('wiki_dict.txt', 'a') as f:
        for word, translation in stressed_list:
            
            f.write(word+';'+translation+'\n')
        else:
            if last_word==word:
                last_word=False
            else:
                last_word=word