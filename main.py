import discord
from discord.ext import commands
import api
import secret

TOKEN = secret.TOKEN
API_KEY = secret.API_KEY

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user}이(가) 로그인하였습니다.')

@bot.event
async def on_guild_join(guild):
    channel = await guild.create_text_channel('던봇용 채널')
    await channel.send('안녕하세요! 이 채널은 던봇 전용 채널입니다.')

@bot.command(name='명성', description='캐릭터의 명성 정보를 확인합니다.')
async def 명성(ctx, server, character_name):
    reputations, character_image = api.get_character_reputation(server, character_name)

    if reputations is None:
        await ctx.send("캐릭터의 명성 정보를 가져오는 데 실패했습니다.")
        return

    await ctx.send(f"{character_name}의 명성은 {reputations[0]}입니다.")

    if character_image:
        await ctx.send(character_image)

@bot.command(name='등급', description='오늘의 아이템 등급과 퍼센테이지를 확인합니다.')
async def 아이템등급(ctx):
    today_item_grade = api.get_today_item_grade()

    if today_item_grade is None:
        await ctx.send("오늘의 아이템 등급 정보를 가져오는 데 실패했습니다.")
        return

    await ctx.send(f"오늘의 아이템 등급은 {today_item_grade}% 입니다.")

    
bot.run(TOKEN)
