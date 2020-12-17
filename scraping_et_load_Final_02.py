#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 13:38:42 2020

@author: formateur
"""

import requests
#import re
from bs4 import BeautifulSoup
import psycopg2, config, time
#import random

# connection à PG, bdd_cparra
conn = psycopg2.connect(database="bdd_cparra", user=config.user,password=config.password, host='127.0.0.1') 
cur = conn.cursor()

print (f"Scraping du jour : {time.ctime()}")
print("")
print("")

# Petit essai, que l'on ne commit pas !
#cur.execute("""INSERT INTO public."ChuckNorris" VALUES (%s, %s, %s)""", ("test fact", 4.5, 50))
cur.execute("""SELECT * FROM "ChuckNorris" LIMIT 10;""")
#print(cur.fetchall())
#cur.commit()
conn.rollback()

#cur.execute("""TRUNCATE TABLE "ChuckNorris";""")
cur.execute("""SELECT * FROM "ChuckNorris";""")
cur.fetchall()
conn.commit()

# Traitement de chaque ligne: affichage & enregistrement
def traiteInfo(id, rate, vote, fact):
    #print(f"{id:4d} : {rate:.2f} {vote:5d} {fact:s}")
    cur.execute("""INSERT INTO public."ChuckNorris" VALUES (%s, %s) ON CONFLICT (id) DO NOTHING;""", (id, fact))
    cur.execute("""INSERT INTO public."ChuckNorrisDate" VALUES (NOW()::Date, %s, %s, %s) ON CONFLICT DO NOTHING;""", (id, rate, vote))

# Definition de la procédure qui traite 1 page
def recupPage(page):
    url = "https://chucknorrisfacts.net/facts.php?page=%d" % (page)
    print("\nRécupération de %s" %(url))
    # extraction du document HTML
    r = requests.get(url, headers={"User-Agent": "Mon navigateur perso d'ici"})
    print("Request' status : ", r.status_code)
    # Traitement avec la librairie BS
    soup = BeautifulSoup(r.content, 'html.parser')
    # Récupération de tous les blocks qui contiennent les info qui nous intéressent.
    # Utilisation de soup.select avec un selecteur CSS
    blocks = soup.select("#content > div:nth-of-type(n+2)")
    #print(blocks[1])
    # 2ime boucle sur les block récupérée
    for block in blocks:
        time.sleep(.5)
        #~ print(block)
        # On récupé les champs individuels (rate, vote, fact)
        # On affiche (si fact non vide)
        fact = block.select_one("p")
        if fact is not None:
            id = block.select_one("ul.star-rating").attrs['id']
            #print(id)
            rate = block.select_one("span.out5Class")
            vote = block.select_one("span.votesClass")
            
            traiteInfo(int(id[6:]), float(rate.text), int(vote.text[:-6]), fact.text)
            #~ print("------------------------")
            
url="https://chucknorrisfacts.net/facts"
r = requests.get(url, headers={"User-Agent": "Mon navigateur perso d'ici"})
soup = BeautifulSoup(r.text, "lxml")

pages = []

for link in soup.find_all('a'):
    uno = link.get_text('href')
    #print(uno)

    pages.append(uno) #Je fais une liste avec toutes les href des balises a
    
#print(pages)  
last_page= int(pages[-6]) #Je choisis l'élément 6 à compter de la fin, qui contiendra toujours le numéro de la dernière page
#print(last_page)

# On traite toutes pages aléatoires
for p in range(last_page+1): #J'en ajoute un pour que la range contienne bien la dernière page
    recupPage(p) #page = random.randint(1,266)


print("")
print("Le nombre de lignes actuellement dans la table ChuckNorrisDate est:")
cur.execute("""SELECT COUNT(*) FROM "ChuckNorrisDate";""")
print(cur.fetchall())

print("Le nombre de lignes actuellement dans la table ChuckNorris est:")
cur.execute("""SELECT COUNT(*) FROM "ChuckNorris";""")
print(cur.fetchall())

# On commit & ferme la connection
conn.commit()
conn.close()            

