import urllib.request # Importa a biblioteca urllib.request para fazer requisições HTTP
import sqlite3 # Importa a biblioteca sqlite3 para lidar com o banco de dados
import gc # Importa a biblioteca gc para coletar lixo e liberar memória
import difflib # Importa a biblioteca difflib para encontrar strings mais próximas

try:
    # Tenta se conectar ao banco de dados database_links_val.db, se ele existir
    db = sqlite3.connect(f"database_links_val.db")
except sqlite3.OperationalError:
    # Caso contrário, cria o arquivo e conecta ao banco de dados
    print("Não existe")
    arquivo = open(f"database_links_val.db", 'w+')
    arquivo.close()
    db = sqlite3.connect(f"database_links_val.db")
    # Cria a tabela times com os campos id, nome e link
    db.execute('''CREATE TABLE times(id INTEGER PRIMARY KEY,nome TEXT, link TEXT)''')

def findlk(name):
    # Transforma o nome em minúsculo
    name = name.lower()
    if " " in name:
        # Substitui os espaços por traços
        name = name.replace(' ','-')
    # Procura no banco de dados o nome exato
    x= list(db.execute("SELECT * FROM times WHERE nome == ?",(name.lower(),)))
    id_value = None
    try:
        # Procura o último id do banco de dados
        tamanhox = db.execute("SELECT id FROM times ORDER BY id DESC LIMIT 1")
        id_value = int(tamanhox.fetchone()[0])
    except:
        id_value = None
    print(id_value)
    # Verifica se o nome exato foi encontrado no banco de dados
    for dado in x:
        if dado[1] == name:
            return dado[2]
    html =''
    link = ''
    for i in range((id_value if id_value else 0),id_value+3): 
        try:
            # Faz uma requisição HTTP para o site https://www.vlr.gg/team/ com o id atual
            html = urllib.request.urlopen(f"https://www.vlr.gg/team/{i}/")
            html = html.read().decode()
            link = f"https://www.vlr.gg/team/{i}/"
            x = '<h1 class="wf-title" style="display: inline-block;">'
            st = html.find(x)+len(x)
            end = html.find('</h1>')
            nome = html[st:end]
            if html :
                # Insere o nome e link no banco de dados
                db.execute("INSERT INTO times(nome,link) VALUES(?, ?)",(nome.lower(), link))
                db.commit()
            continue
        except:
            continue
    x= list(db.execute("SELECT * FROM times WHERE nome == ?",(name.lower(),)))
    # Verifica se o nome exato foi encontrado após a busca adicional
    for dado in x:
        if dado[1] == name:
            return dado[2]
    return 1
def proximojogo(name):
    # chama a função findlk para encontrar o link da página do time
    teste = findlk(name)
    if teste == 1:
        return 1
    # abre a página do time e lê o código fonte
    html = urllib.request.urlopen(teste)
    html = html.read().decode()

    # procura a seção com os próximos jogos
    num = html.find("Upcoming matches")
    if num == -1:
        print("Sem partidas novas")
        return "Sem partidas novas"

    # procura os nomes dos times do próximo jogo
    stri = '<span class="m-item-team-name">'
    index_st_table = html.find(stri,num)+len(stri)
    index_end_table = html.find('</span>',index_st_table)-1
    time1 = html[index_st_table:index_end_table].strip()
    index_st_table = html.find(stri,index_st_table)+len(stri)
    index_end_table = html.find('</span>',index_st_table)-1
    time2 = html[index_st_table:index_end_table].strip()
    print(time1,time2)

    # procura a data e hora do próximo jogo
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

    # ajusta a hora para o fuso horário correto
    if horas.find('pm') == -1:
        horas = str((int(horas[0:(horas.find(':'))])+2 )if horas[0:(horas.find(':'))] !=12 else "02")+str(horas[horas.find(":"):horas.find('m')-1])
    else:
        x = int(horas[0:(horas.find(':'))])+(12 if int(horas[0:(horas.find(':'))]) != 12 else 0)
        horas = str(((x + 2) if x+2< 24 else (x+2)%24))+str(horas[horas.find(":"):horas.find('m')-1])

    # cria um dicionário com as informações do jogo e retorna
    date= {'time1':time1,'time2':time2,'dia':data[2],'mes':data[1],'ano':data[0],'horas': horas}
    return date
