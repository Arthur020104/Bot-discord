import discord
from discord.ext import commands
import youtube_dl
from discord import FFmpegOpusAudio
import urllib.request
import re
#import time
playlist = []
class music(commands.Cog):
    def __init__(self,client):
        self.client = client
    @commands.command()
    async def among(self,ctx,code,vezes):
        if not vezes:
            vezes = 1
        if len(code) != 6 or False in [False if letra.isdigit() else True for letra in code]:
            await ctx.send("O código que vc digitou nao é válido.")
            return
        try:
            vezes = int(vezes)
        except:
            return
        for i in range(vezes):
            x = '.\n'.join(code)
            await ctx.send("Código do amonguinho.\n"+x, tts=True)
            #for letra in code:
            #    time.sleep(1)
            #    await ctx.send(f"{letra}", tts=True)
    @commands.command()
    async def join(self,ctx):
        if ctx.author.voice is None:
            await ctx.send("Você nao está em um canl de voz.")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
    @commands.command()
    async def disconnect(self,ctx):
        await ctx.voice_client.disconnect()
    @commands.command()
    async def play(self,ctx,*args):
        playlist.append(args)
        await ctx.send(f"Música adicionada a playlist")
        if not esperaacabar(ctx):
            #time.sleep(2)
            return #await toca(ctx)
        await toca(ctx,args)
        print('toca0')
        """
        ctx.voice_client.stop()
        saved_args = locals()
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}
        YDL_OPTIONS = {'format':'bestaudio'}
        vc = ctx.voice_client
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
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url,download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
            vc.play(source)
            print(info)
            await ctx.send(f"Tocando {info['title']}")
            time.sleep(info['duration'])
            """
    @commands.command()
    async def pause(self,ctx):
        ctx.voice_client.pause()
        await ctx.send("Pausado ⏸️")
    @commands.command()
    async def resume(self,ctx):
        ctx.voice_client.resume()
        await ctx.send("Retomando ⏯️")
    @commands.command()
    async def skip(self,ctx):
        ctx.voice_client.stop()
        await ctx.send("Pulando música atual.")
        await toca(ctx)
        print('toca1')

def setup(client):
    client.add_cog(music(client))

async def toca(ctx,*args):
    if len(playlist) == 0:
        return
    if not esperaacabar(ctx):
        #time.sleep(2)
        return #await toca(ctx)
    print(playlist,playlist[0])
    args = playlist[0]
    ctx.voice_client.stop()
    saved_args = locals()
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}
    YDL_OPTIONS = {'format':'bestaudio'}
    vc = ctx.voice_client
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
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url,download=False)
        print(url)
        url2 = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
        playlist.pop(0)
        vc.play(source,after=lambda: print('done'))
        await ctx.send(f"Tocando {info['title']}")
        #time.sleep(int(info['duration']))
        #await toca(ctx)

def esperaacabar(ctx):
    while True:
        if not ctx.voice_client.is_playing():

            return True
        else:
            return False