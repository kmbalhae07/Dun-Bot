import discord
from discord.ext import commands
import api
import secret
import mabu

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

@bot.command()
async def 명성(ctx, server, character_name):
    reputations, character_image, job_GrowName = api.get_character_reputation(server, character_name)
    embed = discord.Embed(title=f'캐릭명 : {character_name}',
                          colour=0xff7676)

    if reputations is None:
        embed.set_footer(text = '캐릭터의 명성 정보를 가져오는 데 실패했습니다.')
        await ctx.send(embed = embed)
        return

    # 명성 , 직업 나타나게 하게
    embed.add_field(name='| 명성', value = reputations[0])
    embed.add_field(name='| 직업', value = job_GrowName)

    if character_image:
        embed.set_image(url=character_image)
        await ctx.send(embed = embed)

@bot.command()
async def 등급(ctx):
    today_item_grade = api.get_today_item_grade()
    embed = discord.Embed(title=f'오늘의 아이템 등급은 : {today_item_grade}% 입니다!',
                          colour=0xff7676)
    if today_item_grade is None:
        embed.set_footer(text="오늘의 아이템 등급 정보를 가져오는 데 실패했습니다.")
    await ctx.send(embed=embed)


@bot.command()
async def 마부(ctx, job_type: str):
    card_info = mabu.get_card_info(job_type) 
    if card_info:
        await print_card_info_pagination(ctx, job_type, card_info)
    else:
        await ctx.send(f"{job_type} 직업의 카드 정보를 찾을 수 없습니다.")

async def print_card_info_pagination(ctx, job_type: str, card_info: dict):
    num_pages = len(card_info)
    current_page = 0
    embed = create_embed(job_type, card_info, current_page, num_pages)
    message = await ctx.send(embed=embed)
    PAGINATION_EMOJIS = ["⬅️", "➡️"]
    for emoji in PAGINATION_EMOJIS:
        await message.add_reaction(emoji)
    while True:
        try:
            reaction, user = await bot.wait_for(
                "reaction_add",
                check=lambda reaction, user: user == ctx.author
                and str(reaction.emoji) in PAGINATION_EMOJIS,
                timeout=60,
            )
            await message.remove_reaction(reaction, user)
            current_page = (current_page - 1) if str(reaction.emoji) == "⬅️" else (current_page + 1) % num_pages
            embed = create_embed(job_type, card_info, current_page, num_pages)
            await message.edit(embed=embed)
        except TimeoutError:
            break

def parse_part_cards(part_name, card_info):
    formatted_card_info = ""  # 카드 정보를 저장할 변수
    if isinstance(card_info, dict):
        for card_name, card_stats in card_info.items():
            formatted_card_info += f"{part_name} 카드 목록:\n"  # 각 부위의 이름을 출력
            formatted_card_info += f"{card_name}\n"
            formatted_card_info += f"해당 부위: {part_name}\n"  # 해당 부위를 나타내는 문구 추가
            for stat, value in card_stats.items():
                formatted_card_info += f"- {stat}: {value}\n"
            formatted_card_info += "\n"  # 각 카드 정보 끝에 개행 추가
    elif isinstance(card_info, str):
        formatted_card_info += f"{part_name}: {card_info}\n"

    return formatted_card_info



def create_embed(job_type, card_info, current_page, num_pages):
    embed = discord.Embed(title=f"{job_type} 직업의 카드 목록 (페이지 {current_page + 1}/{num_pages})",
                          colour=0xff7676)

    page_cards = list(card_info.items())[current_page][1]
    for part, part_cards in page_cards.items():
        part_text = ""
        for card_name, card_info in part_cards.items():
            part_text += parse_part_cards(card_name, card_info)
        embed.add_field(name=f"{part}", value=part_text.strip(), inline=False)
    return embed

bot.run(TOKEN)
