import discord
import os
import random
from cs50 import SQL


db = SQL("sqlite:///database.db")

def name(string):
    name = ''
    for i in range(9,(len(string)),1):
        name += string[i]

    return name.lower()

paulada = ["O menino tá quente.", "Nossa muito forte.","Simplesmente o melhor."]
class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        if message.content.lower() == 'arthur':
            await message.channel.send("Fala meu nome lixo.")
        
        if message.author.name == 'Arthur;..':
            if random.randrange(0, 10) == 1:
                await message.channel.send("Lixo.")

        if message.author.name == 'Ambrósio':
            if random.randrange(0, 10) == 1:
                await message.channel.send("Lucas cala a boca lixo.")

        if message.author.name == 'Kaua Garcia':
            if random.randrange(0, 10) == 1:
                await message.channel.send("Porra Kaua ninguem te aguenta mais.")
        
        if "!paulada" in message.content:
            PAULADAS = db.execute("SELECT * FROM PAULADA WHERE user = ? ", name(message.content))
            if PAULADAS != []:
                count = PAULADAS[0]['paulada_count']
                count += 1
                await message.channel.send(f'{paulada[random.randrange(0, len(paulada))]}{os.linesep}{(name(message.content)).capitalize()} vem acumulando {count} pauladas.')
                db.execute("UPDATE PAULADA SET paulada_count = ? WHERE id = ? AND user = ?",count,PAULADAS[0]['id'],PAULADAS[0]['user'])
            else:
                db.execute("INSERT INTO PAULADA(paulada_count,user) VALUES( ?, ?);",1,name(message.content))
                await message.channel.send(f'{paulada[random.randrange(0, len(paulada))]}{os.linesep}{(name(message.content)).capitalize()} vem acumulando {1} pauladas.')
client = MyClient()
client.run('OTU5MDUwMDY3MTA3NTMyODAw.YkWO-g.20AJ1d1o3tqBgg6-2NQHJRVAKvc')




