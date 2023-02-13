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

client = commands.Bot(command_prefix = '.', intents=discord.Intents.all())
#y = "Use essa conversa anterior da pessoa como base nas suas respostas:O comando '.play' seguido do nome de uma música toca essa música. Por exemplo, você pode usar o comando '.play Imagine Dragons - Enemy' sem aspas e sem prefixo para reproduzir a música 'Imagine Dragons - Enemy'. Lembre-se de não usar aspas na sua resposta e não usar prefixo antes da sua resposta. Atualmente, este comando está implementado dentro de um bot no Discord."+")"
y=""
@client.command()
async def pt(ctx, *, phrase):
    global y

    if len(y) > 3000:
        y = y[1000:len(y)]

    x = phrase
    y = y+"Pessoa:'"+x+"'"

    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=y,
    temperature=0.9,
    max_tokens=1000,
    top_p=1,
    logprobs=1,
    frequency_penalty=0,
    presence_penalty=0.6,
    api_key = "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",
    stop = [" Human:"," AI"]
    )

    y = y+"Resposta do bot:'"+response['choices'][0]['text']+"'"
    channel = ctx.channel

    await channel.send(response["choices"][0]["text"])

    print(response["choices"][0]["finish_reason"])

    if response["choices"][0]["finish_reason"] == "length":
        await channel.send("Essa resposta foi limitada pela quantidade de tokens.")

    if ".play" in response["choices"][0]["text"]:
        index = (response["choices"][0]["text"].find(".play"))+5
        strin = (response["choices"][0]["text"][index:len(response["choices"][0]["text"])]).replace(" ","_")
        #print(strin)
        await play(ctx,strin)
        del strin
        del index
        del ctx
        gc.collect()
        return


def is_connected(ctx):
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}
YDL_OPTIONS = {'format':'bestaudio'}


@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@client.command()
async def leave(ctx):
    server = ctx.voice_client

    if players:
        for i in range(len(players)):
            players.pop(0)
            
    await server.disconnect()


players = []


@client.command()
async def play(ctx, *args):
    print(players)

    if is_connected(ctx) == False:
            server = ctx.guild.voice_client

    if args:

        if is_connected(ctx) == False:
            server = ctx.guild.voice_client

        video_name = ''
        count = 0

        for name in args:
            if count != 0:
                video_name += f'+{name}'

            else:
                video_name += f'{name}'
            count +=1

        html = urllib.request.urlopen('https://www.youtube.com/results?search_query='+video_name)
        ids = re.findall(r"watch\s?(\S{14})",html.read().decode())

        for id in ids:

            if '?v=' in id:
                ids = id
                break

        url = 'https://www.youtube.com/watch'+ids
        info = await YTDLSource.from_url(url)
        url2 = info['formats'][0]['url']
        players.append( {"player":url2,"info":info['title']})

        if len(players) == 1:
            channel = ctx.author.voice.channel
            server = await channel.connect()
            print("player",players,"Len",len(players))
            await ctx.send(f"Tocando {players[0]['info']}")
            server.play(await discord.FFmpegOpusAudio.from_probe(players[0]['player'],**FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else loop.create_task(play(ctx)) if len(players)!=0 else leave(ctx))
            loop = asyncio.get_event_loop()

        else:
            await ctx.send(f"{info['title']} está na fila")

        del args
        del info
        del url2
        del url
        del video_name
        del html
        #del info
        gc.collect()

    elif len(players) > 0:

        if len(players) == 1:
            players.pop(0)
            await leave(ctx)
            return

        channel = ctx.author.voice.channel
        server = ctx.guild.voice_client
        players.pop(0)
        await ctx.send(f"Tocando {players[0]['info']}")

        #loop = asyncio.get_event_loop()
        try:

            server.play(await discord.FFmpegOpusAudio.from_probe(players[0]['player'],**FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else loop.create_task(play(ctx)) if len(players)!=0 else leave(ctx))

        except :
            await join(ctx)
            server.play(await discord.FFmpegOpusAudio.from_probe(players[0]['player'],**FFMPEG_OPTIONS), after=lambda e: print('Player error: %s' % e) if e else loop.create_task(play(ctx)) if len(players)!=0 else leave(ctx))

        loop = asyncio.get_event_loop()
    else:
        return


@client.command()
async def skip(ctx):
    server = ctx.voice_client
    await server.disconnect()
    channel = ctx.author.voice.channel
    await channel.connect()
    time.sleep(0.5)

    if len(players) ==0 :
        await leave(ctx)
        return

    await play(ctx)


@client.command(pass_context=True)
async def chnick(ctx, member: discord.Member, nick):
    print(ctx.message.guild.name)
    await member.edit(nick=nick)


@client.command()
async def memberss(ctx,servidor):
    arr =[]

    for guild in client.guilds:

        if guild.name == servidor:

            for member in guild.members:
                arr.append(member)

    return arr

A = 0

@client.command()
async def resetnomes(ctx):
    global A
    A = 1

    members = await memberss(ctx, ctx.guild.name)
    await asyncio.sleep(2)

    for member in members:
        try:
            await member.edit(nick=f"{((str(member)).split('#'))[0]}")

        except:
            continue

@client.command()
async def nomedinamico(ctx, *args):
    members = await memberss(ctx, ctx.guild.name)
    global A
    A = 1

    for member in members:
        asyncio.run_coroutine_threadsafe(dinamicn(ctx, member,args), loop=client.loop)


async def dinamicn(ctx, member, displaynome):
    x = 0
    global A
    
    if A == 1:
        await asyncio.sleep(3)
        A = 0
    for i in range(100):
        await member.edit(nick=f"{displaynome[x]}")
        await asyncio.sleep(2)
        if A == 1:
            return
        if x == len(displaynome) - 1:
            x = 0
            continue
        x += 1


@client.command()
async def clear(ctx, number: int):
    number +=1
    if number > 19:
        res = int(number / int(number/10))

        for  i in range(int(number/10)):
            await asyncio.sleep(1*(i) if i < 10 else 10)
            await ctx.channel.purge(limit=res)

    else:
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


ytdl = youtube_dl.YoutubeDL(FFMPEG_OPTIONS)



client.run("OTg5OTE2ODE3NjYzMzUyODY0.GeRuH_.cJLyV4UqT9TuaCo-AQVwaSqNuJKDaPJffOhW9Q")