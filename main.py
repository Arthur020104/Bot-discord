import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import urllib
import re
from openai import OpenAI
import gc
import asyncio
import time
import os
from valfunc import findlk, proximojogo, nomeparecido
import pytz
import datetime
import json
import urllib
from openai import ChatCompletion
import time
import time

# Create a new client instance with the specified command prefix and intents
client = commands.Bot(command_prefix='.', intents=discord.Intents.all())
y = ""

# A command to check Brazilian Valorant teams' upcoming matches
#@client.command()
async def brgames():
    global done
    done = 0
    times = ['sentinels', 'furia', 'mibr', 'loud']
    channel = client.get_channel(858555677671817217)
    br_timezone = pytz.timezone('America/Sao_Paulo')
    
    while True:
        now = datetime.datetime.now(tz=br_timezone)
        horas = (int(now.hour))
        horas = horas % 24 if ((int(now.hour))) >= 24 else horas
        dia = (int(now.day))
        mes = (int(now.month))
        tempo = []
        try:

            difhoras = ((int(date["horas"][0:int(date["horas"].find(":"))])) - horas)
        except:
            await asyncio.sleep(600)
            continue
        for time in times:
            date,h = proximojogo(time)
            if date == "Sem partidas novas":
                continue
            difhoras = ((int(date["horas"][0:int(date["horas"].find(":"))])) - horas)
            tempo.append((difhoras-1) if (mes == int(date['mes']) and (dia == int(date['dia']))) else 1)

            print("Horas:",horas, (int(date["horas"][0:(date["horas"].find(":"))]),"|Diffhour",difhoras))
            print("Mes:",mes , int(date['mes']),"|Dia:", (dia , int(date['dia'])), '\n\n\n\n')

            # Check if the match is happening today and within the next hour
            if mes == int(date['mes']) and (dia == int(date['dia'])) and (difhoras == 1):
                status = f'{date["time1"]} x {date["time2"]} dia {date["dia"]} do mês {date["mes"]} de {date["ano"]} às {date["horas"]}'
                
                allowed_mentions = discord.AllowedMentions(everyone=True)
                
                await channel.send("@everyone" + status, allowed_mentions=allowed_mentions)
                
        
        await asyncio.sleep(600)
        done = 0
@client.event
async def on_ready():
    await brgames()

@client.command()
async def valorantjogo(ctx, *, phrase):
    # calls function 'proximojogo' to get the date of the next game
    date,h = proximojogo((phrase.strip()))
    status = ''
    if isinstance(date, dict) :
        # if the date is valid, build a status string with the date info
        status = f'{date["time1"]} x {date["time2"]} dia {date["dia"]} do mês {date["mes"]} de {date["ano"]} às {date["horas"]}'
        channel = ctx.channel
        response = status 
        await channel.send(response)
        return
    elif date ==1:
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
        # if user confirms, call 'proximojogo' with the suggested name 
        if str(message.content) == "1":
            date,h = proximojogo(nome.strip())
            try:
                status = f'{date["time1"]} x {date["time2"]} dia {date["dia"]} do mês {date["mes"]} de {date["ano"]} às {date["horas"]}'
            except:
                status = f"O time {phrase} não foi encontrado"
                
            response = status
            await channel.send(response)
            return
        else:
            # if user denies, send a message saying that the team was not found
            await channel.send(f"O time {phrase} não foi encontrado")
            return
    elif h != None and (isinstance(h,list) or isinstance(h,tuple)):
        channel = ctx.channel
        await channel.send(f"Você quis dizer\n1.{h[0][2]}\n2.{h[1][2]}")
        # waits for the user to reply with 1 or 2
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        user_response = await client.wait_for('message', check=check)
        channel = client.get_channel((user_response.channel).id)
        message = await channel.fetch_message(user_response.id)
        # if user confirms, call 'proximojogo' with the suggested name 
        if str(message.content) == "1":
            x = str(h[0][2])
            x = re.split('(\d+)',x)
            if len(x) <= 3 :
                x = str(x[1])
            
            x = (phrase.strip())+x
            date,h = proximojogo(x)
            status = f'{date["time1"]} x {date["time2"]} dia {date["dia"]} do mês {date["mes"]} de {date["ano"]} às {date["horas"]}'
            response = status
            await channel.send(response)
            return
        else:
            x = str(h[1][2])
            x = re.split('(\d+)',x)
            if len(x) <= 3 :
                x = str(x[1])
            
            x = (phrase.strip())+x
            date,h = proximojogo(x)
            status = f'{date["time1"]} x {date["time2"]} dia {date["dia"]} do mês {date["mes"]} de {date["ano"]} às {date["horas"]}'
            response = status
            await channel.send(response)
            return
    else:
        channel = ctx.channel
        await channel.send(date)
async def openairesponse(prompt, temp=0.9, ctx=None):
    client_ai = OpenAI(api_key=key)
    messages = [
        {"role": "system", "content": "Você é um assistente específico para informações sobre valorant, tente manter suas respostas curtas. Para toda pergunta se for uma continuação de uma conversa suas respostas antigas virão como Resposta do bot: e o usuário como Pessoa:. Respostas em text e não adicione prefixo na suas resposta como 'Resposta do bot:'. Se for tocar musicas o nome das musicas só podem conter characteres ascii e deve ser seguido do nome do artista {musica - artista}."},
        {"role": "user", "content": prompt}
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "play",
                "description": "Play a song for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "song_name": {
                            "type": "string",
                            "description": "The name of the song to be played",
                        },
                    },
                    "required": ["song_name"],
                },
                "returns": {"type": "void"},
            },
        }
    ]

    response = client_ai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        response_format={"type": "text"},
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message

    print(response_message)
    tool_calls = response_message.tool_calls

    if tool_calls:
        available_functions = {"play": play}
        messages.append(response_message)

        for tool_call in tool_calls:
            function_call = tool_call.function
            if function_call:
                function_name = function_call.name
                function_to_call = available_functions.get(function_name)
                print(function_to_call)
                if function_to_call:
                    function_args = json.loads(function_call.arguments)
                    print(function_args)
                    # Call the play function with the song name and ctx
                    args = [10]
                    await asyncio.run_coroutine_threadsafe(function_to_call(ctx, song_name=function_args.get("song_name")),client.loop)


                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": "Yes, I can play that for you.",
                            
                        }
                    )

        second_response = client_ai.chat.completions.create(
            response_format={"type": "text"},
            model="gpt-3.5-turbo-0125",
            messages=messages,
        )

        return second_response
    else:
        # Return the completion for the original prompt if tools are not called
        return response_message.content



@client.command()
async def pt(ctx, *, phrase):
    global y

    if len(y) > 3000:
        y = y[1000:]

    x = phrase
    y += f"Pessoa:'{x}'"

    response = await openairesponse(y, 0.9, ctx)
   
    if not isinstance(response,str):
        response = "Tocando musica"
        y += f"Resposta do bot:'{response}'"
        return
    else:
        response = str(response)
    print(response)
    y += f"Resposta do bot:'{response}'"

    channel = ctx.channel

    # Check if the response is not empty before sending
    if response:
        await channel.send(response)
    else:
        print("Warning: Attempted to send an empty message.")

    # Initialize variables
    strin, index = None, None

    # Check if response is not None before checking for ".play"
    if response and ".play" in response:
        index = response.find(".play") + 5
        strin = response[index:]
        strin = strin.replace(" ", "_")

        await play(ctx, strin)

    # Delete variables if they are assigned
    if strin is not None:
        del strin
    if index is not None:
        del index
    del ctx
    gc.collect()



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
async def play(ctx, *args, song_name=None):
    print("znznnzn\n\n\nn\n\here")
    print(song_name)
    # Check if the user is in a voice channel
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("You must be in a voice channel to use this command.")
        return

    # Get the voice channel of the user who invoked the command
    channel = ctx.author.voice.channel

    # Check if the bot is already connected to a voice channel
    if ctx.voice_client is None:
        # Connect to the voice channel
        vc = await channel.connect()
    else:
        # Use the existing connection
        vc = ctx.voice_client

    # Check if arguments are provided
    if args or song_name:
        # Combine the arguments into a search query
        query = '_'.join(args) if args else song_name.replace(' ', '_')
        print(query)
        args = query
        try:
        # Use your logic to search for the music track on YouTube and extract the video ID
            video_name = '+'.join(args)
            html = urllib.request.urlopen('https://www.youtube.com/results?search_query=' + video_name)
            ids = re.findall(r"watch\s?(\S{14})", html.read().decode())
            ids = next((id for id in ids if '?v=' in id), None)
            video_id = ids

            if video_id:
                # Construct the YouTube URL
                youtube_url = f'https://www.youtube.com/watch{video_id}'
                print(youtube_url)
                # Fetch information about the video using YTDLSource
                source = await YTDLSource.from_url(youtube_url)
                audio_source = discord.FFmpegPCMAudio(source['url'])
                print(source['title'])
                players.append({'source': audio_source, 'title': source['title']})

                # If it's the first track, send a message and play the audio
                if len(players) == 1:
                    print(source['title'])
                    await ctx.send(f"Now playing: {source['title']}")
                    vc = ctx.voice_client
                    vc.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(on_song_end(ctx, e), client.loop))

            else:
                await ctx.send("No valid song found.")

        except Exception as e:
            print(f"An error occurred: {e}")

    elif players:#maybe useless
        # If no arguments are provided and there are existing tracks, play the next track
        print(players[0]['title'])
        await ctx.send(f"Now playing: {players[0]['title']}")
        vc = ctx.voice_client
        vc.play(players[0]['sorce'], after=lambda e: asyncio.run_coroutine_threadsafe(on_song_end(ctx, e), client.loop))

    else:
        # If no arguments and no existing tracks, return a message
        await ctx.send("No tracks to play.")
async def on_song_end(ctx, error):
    if error:
        print(f"Error in playing the song: {error}")

    # Remove the finished track
    players.pop(0)

    # Check if there are more tracks in the queue
    if players:
        # Play the next track in the queue
        vc = ctx.voice_client
        vc.play(players[0]['sorce'], after=lambda e: asyncio.run_coroutine_threadsafe(on_song_end(ctx, e), client.loop))
        await ctx.send(f"Now playing: {players[0]['title']}")
    else:
        # No more tracks in the queue
        await ctx.send("Queue is empty. Use !play <song_name> to add more songs.")
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
    print(ctx.message.guild.name)
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

        # Verifica se a flag A é 1 , se for, sai do loop.
        if A == 1:
            return

        # Verifica se o contador x é igual ao número de nomes a serem exibidos -1,
        # se for, define o valor de x como 0, caso contrário, incrementa o valor de x em 1.
        if x == len(displaynome) - 1:
            x = 0
            continue
        x += 1
        
@client.command()
async def comandos(ctx):
    channel = ctx.channel
    response = await openairesponse("1.valorantjogo <NomedoTime> - Comando que verifica a data e hora do próximo jogo de Valorant de uma equipe específica.\n2.Para usar o comando de conversação do bot, digite '.pt' seguido de uma frase ou pergunta que você deseja que o bot responda.\n3.Para usar o comando de conexão do bot ao canal de voz, digite '.join'.\n4.Para usar o comando de desconexão do bot do canal de voz, digite '.leave'\n5.No servidor, digite no chat o prefixo '.' seguido do comando 'play' e o nome da música que deseja tocar, por exemplo: .play never gonna give you up\n6. O '.skip' é responsável por pular para a próxima música da fila de reprodução no canal de voz do Discord.\n7.O 'chnick' é responsável por alterar o apelido de um membro do servidor.\n8.O comando 'resetnomes' é responsável por redefinir o apelido de todos os membros de um servidor.")
    await channel.send(response )
@client.command()
async def clear(ctx, number: int):
    number +=1

    if number > 19:
        # Divide o valor de number pelo número inteiro da divisão de number por 10.
        res = int(number / int(number/10))

        # Loop para deletar mensagens em lotes.
        numberOfDeletedMessages = 0
        while numberOfDeletedMessages < number:
            numberOfDeletedMessages += res
            if numberOfDeletedMessages > number:
                res = number - (numberOfDeletedMessages - res)
                numberOfDeletedMessages = number
            await asyncio.sleep(1 * (res))
            await ctx.channel.purge(limit=res)

    else:
        # Deleta as mensagens do canal.
        await ctx.channel.purge(limit=number)

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
client.run("OTg5OTE2ODE3NjYzMzUyODY0.G2jcz8.XZeNLhk98VELcQFj0usapPhzrxI14Ejdo8FhbI")