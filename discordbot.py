import discord
import os
import random

PAULADAS = {
    "Arthur": 0,
    "Lucas": 0,
    "Kaua":0,
    "Johnny":0,
    "Nicolas":0,
    "Asuna": 0,
    "Sucata":0,
}
paulada = ["O menino tá quente.", "Nossa muito forte.","Simplesmente o melhor."]
class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        if message.content.lower() == 'arthur':
            await message.channel.send("Fala meu nome lixo.")
        
        if message.author.name == 'Arthur;..':
            if random.randrange(0, 3) == 1:
                await message.channel.send("Lixo.")

        if message.author.name == 'Ambrósio':
            if random.randrange(0, 3) == 1:
                await message.channel.send("Lucas cala a boca lixo.")

        if message.author.name == 'Kaua Garcia':
            await message.channel.send("Porra Kaua ninguem te aguenta mais.")
        
        if "!paulada" in message.content:
            for word in PAULADAS:
                if word in message.content:
                    PAULADAS[word] += 1
                    await message.channel.send(f'{paulada[random.randrange(0, len(paulada))]}{os.linesep}O {word} vem acumulando {PAULADAS[word]} pauladas.')
client = MyClient()
client.run('OTU5MDUwMDY3MTA3NTMyODAw.YkWO-g.ow_KHsXFOPVQpK5PBhW0lw09pN4')