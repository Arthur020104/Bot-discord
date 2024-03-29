import discord
from discord.ext import commands
import youtube_dl as youtube_dl
import urllib
import re
import openai
import gc
import asyncio
import time
import os
from teste import findlk, proximojogo, nomeparecido
import pytz
import datetime

# Create a new client instance with the specified command prefix and intents
client = commands.Bot(command_prefix='.', intents=discord.Intents.all())
y = ""
done = 0
times = ['sentinels', 'furia', 'mibr', 'loud']
channel = client.get_channel(858555677671817217)

# A command to check Brazilian Valorant teams' upcoming matches
@client.command()
async def brgames(ctx):
    global done
    
    # Get the timezone for Brazil
    br_tz = pytz.timezone('America/Sao_Paulo')
    
    while True:
        # Get the current date and time in the Brazil timezone
        now = datetime.datetime.now(tz=br_tz)
        horas = (int(now.hour))
        horas = horas % 24 if ((int(now.hour))) >= 24 else horas
        dia = (int(now.day))
        mes = (int(now.month))
        tempo = []

        for time in times:
            date = proximojogo(time)
            difhour = ((int(date["horas"][0:(date["horas"].find(":"))])) - horas)
            tempo.append((difhour-1) if (mes == int(date['mes']) and (dia == int(date['dia']))) else 1)
            print(horas, (int(date["horas"][0:(date["horas"].find(":"))])), '\n\n\n\n')

            # Check if the match is happening today and within the next hour
            if mes == int(date['mes']) and (dia == int(date['dia'])) and (difhour < 1 and difhour >= 0):
                done = 1
                status = f'{date["time1"]} x {date["time2"]} dia {date["dia"]} do mês {date["mes"]} de {date["ano"]} às {date["horas"]}'
                
                # Create an allowed_mentions object to mention everyone in the server
                allowed_mentions = discord.AllowedMentions(everyone=True)
                
                # Use OpenAI API to generate an announcement message and send it to the specified channel
                response = openairesponse(f'faça um anuncio desse jogo de valorant(Valorant é um jogo eletrônico multijogador de tiro em primeira pessoa) que será transmitido no canal da twitch https://www.twitch.tv/valorant_br,anuncio será feito em um server do discord entao faça formataçao apropriada, de forma simples que possa ser usado como template {status}, nao assuma nada além dasinformaçoes fornecidas', 0.1)
                await channel.send("@everyone" + response["choices"][0]["text"], allowed_mentions=allowed_mentions)
                
        # Wait for an hour before checking again
        if done == 1:
            await asyncio.sleep(3600)
            done = 0
        # Wait for the time until the next match starts before checking again
        await asyncio.sleep((min(tempo) * 60) * 60)
@client.command()
async def valorantjogo(ctx, *, phrase):
    # calls function 'proximojogo' to get the date of the next game
    date = proximojogo(phrase)
    status = ''
    if date != 1:
        # if the date is valid, build a status string with the date info
        status = f'{date["time1"]} x {date["time2"]} dia {date["dia"]} do mês {date["mes"]} de {date["ano"]} às {date["horas"]}'
        channel = ctx.channel
        print(status)
        # calls function 'openairesponse' to generate a message using the status string
        response = openairesponse(f'faça um anuncio desse jogo de valorant(Valorant é um jogo eletrônico multijogador de tiro em primeira pessoa) que será transmitido no canal da twitch https://www.twitch.tv/valorant_br,anuncio será feito em um server do discord entao faça formataçao apropriada, de forma simples que possa ser usado como template {status}, nao assuma nada além dasinformaçoes fornecidas',0.1)
        # sends the message to the channel where the command was called
        await channel.send(response["choices"][0]["text"])
    else:
        # if the date is invalid, suggest a similar name and ask for confirmation
        channel = ctx.channel
        nome = nomeparecido(phrase)
        await channel.send(f"Você quis dizer {nome}\n1.Sim\n2.Não")
        # waits for the user to reply with 1 or 2
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        user_response = await client.wait_for('message', check=check)
        channel = client.get_channel((user_response.channel).id)
        message = await channel.fetch_message(user_response.id)
        # if user confirms, call 'proximojogo' with the suggested name and build the status string
        if str(message.content) == "1":
            date = proximojogo(nome)
            status = f'{date["time1"]} x {date["time2"]} dia {date["dia"]} do mês {date["mes"]} de {date["ano"]} às {date["horas"]}'
            print(status)
            # calls function 'openairesponse' to generate a message using the status string
            response = openairesponse(f'faça um anuncio desse jogo de valorant(Valorant é um jogo eletrônico multijogador de tiro em primeira pessoa) que será transmitido no canal da twitch https://www.twitch.tv/valorant_br,anuncio será feito em um server do discord entao faça formataçao apropriada, de forma simples que possa ser usado como template {status}, nao assuma nada além dasinformaçoes fornecidas',0.1)
            # sends the message to the channel where the command was called
            await channel.send(response["choices"][0]["text"])
        else:
            # if user denies, send a message saying that the team was not found
            await channel.send(f"O time {phrase} não foi encontrado")
def openairesponse(prompt, temp=0.9):
    # Function that sends a request to OpenAI's API to generate text.
    # The generated text will be a response to a given prompt.
    response = openai.Completion.create(
        model="text-davinci-003",  # Specify the OpenAI model to use for text generation.
        prompt=prompt,  # Provide the prompt for which to generate a response.
        temperature=temp,  # Set the temperature parameter for the text generation.
        max_tokens=1000,  # Set the maximum number of tokens the API can return.
        top_p=1,  # Set the sampling algorithm for tokens.
        logprobs=1,  # Include log probabilities of each token to allow re-ranking.
        frequency_penalty=0,  # Set the frequency penalty for the text generation.
        presence_penalty=0.6,  # Set the presence penalty for the text generation.
        api_key="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",  # The API key for OpenAI's API.
        stop=[" Human:", " AI"]  # Set the stop sequence for text generation.
    )
    return response


@client.command()
async def pt(ctx, *, phrase):
    # A Discord bot command that takes a phrase as input and generates a response using OpenAI's API.
    global y
    if len(y) > 3000:
        y = y[1000:len(y)]
    x = phrase
    y = y + "Pessoa:'" + x + "'"
    response = openairesponse(y)
    y = y + "Resposta do bot:'" + response['choices'][0]['text'] + "'"
    channel = ctx.channel
    await channel.send(response["choices"][0]["text"])
    print(response["choices"][0]["finish_reason"])
    if response["choices"][0]["finish_reason"] == "length":
        await channel.send("Essa resposta foi limitada pela quantidade de tokens.")
    if ".play" in response["choices"][0]["text"]:
        index = (response["choices"][0]["text"].find(".play")) + 5
        strin = (response["choices"][0]["text"][index:len(response["choices"][0]["text"])])
        # Replace all spaces in the string with underscores.
        strin = strin.replace(" ", "_")
        await play(ctx, strin)  # Play the audio corresponding to the specified string.
        del strin
        del index
        del ctx
        gc.collect()
        return


def is_connected(ctx):
    # Function that checks if the bot is connected to a voice channel.
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


# Options for playing audio using FFmpeg and YouTube DL.
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio'}
@client.command()
async def join(ctx):
    # Get the voice channel of the author
    channel = ctx.author.voice.channel
    # Disconnect from any previous voice channel and join the new one
    if client.voice_clients:
        await client.voice_clients[0].disconnect()
    await channel.connect()
    await asyncio.sleep(1)

@client.command()
async def leave(ctx):
    # Get the voice client of the server
    server = ctx.voice_client
    # Clear the list of players
    if players:
        for i in range(len(players)):
            players.pop(0)     
    # Disconnect from the voice channel
    await server.disconnect()

global players
players = []
@client.command()
async def play(ctx, *args):
    global players
    print(players) # Exibe a lista de músicas na console.

    # Verifica se o bot já está conectado em algum canal de voz do servidor.
    if is_connected(ctx) == False:
        server = ctx.guild.voice_client

    if args: # Se foram passados argumentos para o comando, inicia a busca do vídeo no YouTube.
        if is_connected(ctx) == False: # Verifica se o bot já está conectado em algum canal de voz do servidor.
            server = ctx.guild.voice_client

        video_name = '' # Define uma string vazia que armazenará o nome do vídeo pesquisado.
        count = 0 # Define um contador para percorrer a lista de argumentos passados.

        # Concatena os argumentos passados na linha de comando em uma única string separada por '+', que será utilizada na busca do vídeo no YouTube.
        for name in args:
            if count != 0:
                video_name += f'+{name}'
            else:
                video_name += f'{name}'
            count +=1

        html = urllib.request.urlopen('https://www.youtube.com/results?search_query='+video_name) # Realiza uma busca no YouTube com o nome do vídeo passado como argumento.
        ids = re.findall(r"watch\s?(\S{14})",html.read().decode()) # Extrai o ID do vídeo da página de resultados da busca.
        for id in ids:
            if '?v=' in id:
                ids = id
                break
        url = 'https://www.youtube.com/watch'+ids # Monta a URL do vídeo encontrado no YouTube.

        # Obtém informações do vídeo (título, duração, etc.) utilizando o módulo YTDL.
        info = await YTDLSource.from_url(url)

        # Obtém a URL do arquivo de áudio do vídeo encontrado no YouTube.
        url2 = info['formats'][0]['url']

        # Adiciona a música encontrada na lista de músicas a serem tocadas.
        players.append( {"player":url2,"info":info['title']})

        # Se for a primeira música da lista, conecta no canal de voz e começa a tocá-la.
        if len(players) == 1:
            channel = ctx.author.voice.channel
            server = await channel.connect()
            print("player",players,"Len",len(players))
            await ctx.send(f"Tocando {players[0]['info']}")
            server.play(await discord.FFmpegOpusAudio.from_probe(players[0]['player'],**FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else loop.create_task(play(ctx)) if len(players)!=0 else leave(ctx))
            loop = asyncio.get_event_loop()

        # Se já existem músicas na lista, adiciona a nova música na fila.
        else:
            await ctx.send(f"{info['title']} está na fila")

        # Remove as variáveis que não são mais necessárias da memória.
        del args
        del info
        del url2
        del url
        del video_name
        del html
        gc.collect()
    # Se não foram passados argumentos e há músicas na lista de reprodução
    elif len(players) > 0:
    # Remove a primeira música da lista de players
        if len(players) > 0:
            players.pop(0)
        else:
            print(players)
            return

        # Toca a próxima música
        await ctx.send(f"Tocando {players[0]['info']}")
        channel = ctx.author.voice.channel
        server = ctx.guild.voice_client
        try:
            server.play(await discord.FFmpegOpusAudio.from_probe(players[0]['player'],**FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else loop.create_task(play(ctx)) if len(players)!=0 else leave(ctx))
        except :
            if players:
                server.play(await discord.FFmpegOpusAudio.from_probe(players[0]['player'],**FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else loop.create_task(play(ctx)) if len(players)!=0 else leave(ctx))
        loop = asyncio.get_event_loop()
    else:
        return
# Definindo uma função para pular a música atual e tocar a próxima na fila
@client.command()
async def skip(ctx):
    server = ctx.voice_client
    await server.disconnect()   # desconecta o servidor de áudio atual
    channel = ctx.author.voice.channel
    await channel.connect()     # conecta ao canal de voz do autor da mensagem
    time.sleep(0.5)

    if len(players) == 0:  # se a lista de players (músicas) estiver vazia, sai do canal de voz
        await leave(ctx)
        print("len players is 0")
        return

    await play(ctx)  # toca a próxima música da fila

# Comando para alterar o apelido de um membro do servidor
@client.command(pass_context=True)
async def chnick(ctx, member: discord.Member, nick):
    print(ctx.message.guild.name)  # exibe o nome do servidor na qual o comando foi executado
    await member.edit(nick=nick)   # altera o apelido do membro para o novo apelido especificado no comando

# Comando para obter a lista de membros de um servidor
@client.command()
async def memberss(ctx, servidor):
    arr = []

    for guild in client.guilds:
        if guild.name == servidor:  # verifica se o nome do servidor corresponde ao servidor especificado no comando
            for member in guild.members:
                arr.append(member)

    return arr  # retorna uma lista com os membros do servidor especificado

# Variável global utilizada para resetar os nomes dos membros
A = 0

# Comando para resetar o apelido dos membros de um servidor
@client.command()
async def resetnomes(ctx):
    global A
    A = 1

    members = await memberss(ctx, ctx.guild.name)  # obtém a lista de membros do servidor
    await asyncio.sleep(2)

    for member in members:
        try:
            await member.edit(nick=f"{((str(member)).split('#'))[0]}")  # reseta o apelido do membro para o nome de usuário (parte antes do #)
        except:
            continue  # continua o loop mesmo que ocorra uma exceção ao tentar alterar o apelido do membro
@client.command()
async def nomedinamico(ctx, *args):
    # Obtém uma lista de todos os membros do servidor.
    members = await memberss(ctx, ctx.guild.name)
    global A
    A = 1

    for member in members:
        # Chama a função 'dinamicn' para cada membro da lista.
        asyncio.run_coroutine_threadsafe(dinamicn(ctx, member,args), loop=client.loop)

async def dinamicn(ctx, member, displaynome):
    x = 0
    global A

    # Verifica se a flag A é 1 (true), se for, espera 3 segundos.
    if A == 1:
        await asyncio.sleep(3)
        A = 0

    # Loop para alterar o nome do membro.
    for i in range(100):
        await member.edit(nick=f"{displaynome[x]}")
        await asyncio.sleep(2)

        # Verifica se a flag A é 1 (true), se for, sai do loop.
        if A == 1:
            return

        # Verifica se o contador x é igual ao número de nomes a serem exibidos -1,
        # se for, define o valor de x como 0, caso contrário, incrementa o valor de x em 1.
        if x == len(displaynome) - 1:
            x = 0
            continue
        x += 1

@client.command()
async def clear(ctx, number: int):
    # Incrementa o valor de number em 1.
    number +=1

    # Verifica se o valor de number é maior que 19.
    if number > 19:
        # Divide o valor de number pelo número inteiro da divisão de number por 10.
        res = int(number / int(number/10))

        # Loop para deletar mensagens em lotes.
        for  i in range(int(number/10)):
            await asyncio.sleep(1*(i) if i < 10 else 10)
            await ctx.channel.purge(limit=res)

    else:
        # Deleta as mensagens do canal.
        await ctx.channel.purge(limit=number+1)

class YTDLSource(discord.PCMVolumeTransformer):
    # ...

    @classmethod
    async def from_url(cls, url):
        try:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url,download=False)
                return info
        except Exception as e:
            print(f'Error occured: {e}')

# Cria uma instância do YoutubeDL com as opções FFMPEG.
ytdl = youtube_dl.YoutubeDL(FFMPEG_OPTIONS)

# Inicia o bot.
client.run("OTg5OTE2ODE3NjYzMzUyODY0.Glxb65.uLKbJLPme-YiVQXg6vWoD4z7yrEOiA5lzOgCnU")


