import urllib.request
import sqlite3
import gc
import difflib
try:
    db = sqlite3.connect(f"database_links_val.db")
except sqlite3.OperationalError:
    print("Nao existe")
    arquivo = open(f"database_links_val.db", 'w+')
    arquivo.close()
    db = sqlite3.connect(f"database_links_val.db")
    db.execute('''CREATE TABLE times(id INTEGER PRIMARY KEY,nome TEXT, link TEXT)''')

def findlk(name):
    name = name.lower()
    if " " in name:
        name = name.replace(' ','-')
    x= list(db.execute("SELECT * FROM times WHERE nome == ?",(name.lower(),)))
    id_value = None
    try:
        tamanhox = db.execute("SELECT id FROM times ORDER BY id DESC LIMIT 1")
        id_value = int(tamanhox.fetchone()[0])
    except:
        id_value = None
    print(id_value)
    for dado in x:
        if dado[1] == name:
            return dado[2]
    html =''
    link = ''
    for i in range((id_value if id_value else 0),id_value+3): 
        try:
            html = urllib.request.urlopen(f"https://www.vlr.gg/team/{i}/")
            html = html.read().decode()
            link = f"https://www.vlr.gg/team/{i}/"
            x = '<h1 class="wf-title" style="display: inline-block;">'
            st = html.find(x)+len(x)
            end = html.find('</h1>')
            nome = html[st:end]
            if html :
                db.execute("INSERT INTO times(nome,link) VALUES(?, ?)",(nome.lower(), link))
                db.commit()
            del html
            del end
            del st
            gc.collect()
            continue
        except:
            continue
    x= list(db.execute("SELECT * FROM times WHERE nome == ?",(name.lower(),)))
    for dado in x:
        if dado[1] == name:
            return dado[2]
    return 1

def nomeparecido(name):
    x = list(db.execute("SELECT * FROM times"))
    names_list = []
    for y in x:
        names_list.append(y[1])
    closest_matches = difflib.get_close_matches(name, names_list)
    if closest_matches:
        return closest_matches[0]
    else:
        return None

def proximojogo(name):
    teste = findlk(name)
    if teste == 1:
        return 1
    html = urllib.request.urlopen(teste)
    html = html.read().decode()
    num = html.find("Upcoming matches")
    if num == -1:
        print("Sem partidas novas")
        return "Sem partidas novas"
    stri = '<span class="m-item-team-name">'
    index_st_table = html.find(stri,num)+len(stri)
    #index_st_table = html.find('<table class="simple">',(num-26))
    index_end_table = html.find('</span>',index_st_table)-1
    time1 = html[index_st_table:index_end_table].strip()
    index_st_table = html.find(stri,index_st_table)+len(stri)
    index_end_table = html.find('</span>',index_st_table)-1
    time2 = html[index_st_table:index_end_table].strip()
    print(time1,time2)
    string = '<div class="m-item-date">'
    data_st = html.find(string,index_end_table)+len(string)
    data_st = html.find('<div>',data_st)+len('<div>')
    data_end = html.find("</div>",data_st)
    data = html[data_st:data_end].strip()
    data = data.split('/')
    time_st = data_end+len('</div>')+1
    time_end = html.find('m',time_st)+1
    horas = html[time_st:time_end].strip()
    print(horas)
    #print(horas[0:(horas.find(':'))])
    if horas.find('pm') == -1:
        horas = str((int(horas[0:(horas.find(':'))])+2 )if horas[0:(horas.find(':'))] !=12 else "02")+str(horas[horas.find(":"):horas.find('m')-1])
    else:
        x = int(horas[0:(horas.find(':'))])+(12 if int(horas[0:(horas.find(':'))]) != 12 else 0)
        horas = str(((x + 2) if x+2< 24 else (x+2)%24))+str(horas[horas.find(":"):horas.find('m')-1])
    date= {'time1':time1,'time2':time2,'dia':data[2],'mes':data[1],'ano':data[0],'horas': horas}
    return date