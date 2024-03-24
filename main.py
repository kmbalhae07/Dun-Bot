import discord
import grade
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
    item_names = grade.get_item_names()

    parts = list(item_names.keys())
    num_parts = len(parts)
    current_page = 0

    async def create_embed(part_index):
        part = parts[part_index]
        item_name = item_names[part]
        item_grade = api.get_today_item_grade(item_name)
        
        if item_grade:
            grade_name = item_grade.get('grade_name')
            grade_value = item_grade.get('grade_value')
            part_text = f"**{grade_name}: {grade_value}%**\n"
            item_status = api.get_today_item_Status(item_name)

            if item_status:
                item_status_100 = api.get_max_grade_status(item_name)
                if item_status_100:
                    status_diff_text = ""  # 두 스탯의 차이를 나타내는 문자열 초기화
                    for status in item_status:
                        if status['name'] in ["힘", "체력", "지능", "정신력"]:
                            status_name = status['name']
                            status_value = int(status['value'])
                            status_text = f"{status_value}"
                            
                            # 100% 상태의 스탯 가져오기
                            for status_100 in item_status_100:
                                if status_100['name'] == status_name:
                                    status_value_100 = int(status_100['value'])
                                    break
                            else:
                                status_value_100 = 0  # 만약 100% 상태의 스탯이 없다면 0으로 설정
                            
                            # 100% 상태와 오늘 상태의 차이 계산
                            status_diff = status_value_100 - status_value
                            status_diff_text += f"{status_name} : {status_text} (-{status_diff})\n"

                    # 차이를 나타내는 문자열을 추가
                    part_text += "\n100% 상태와의 차이:\n" + status_diff_text

                else:
                    part_text += "100% 상태의 아이템 세부 상태를 가져오지 못했습니다."
            else:
                part_text += "등급 정보를 가져오지 못했습니다."

            embed = discord.Embed(title="오늘의 아이템 등급", colour=0xff7676)
            embed.add_field(name=f"상세 스탯", value=part_text.strip(), inline=False)
            embed.set_footer(text=f"페이지 {part_index + 1}/{num_parts}")

            return embed
        else:
            return None


    message = await ctx.send(embed=await create_embed(current_page))
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
            if str(reaction.emoji) == "⬅️":
                current_page = (current_page - 1) % num_parts
            elif str(reaction.emoji) == "➡️":
                current_page = (current_page + 1) % num_parts
            await message.edit(embed=await create_embed(current_page))
        except TimeoutError:
            break


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
    formatted_card_info = ""
    if isinstance(card_info, dict):
        for part_stats, stats in card_info.items():
            formatted_card_info += f"해당 부위: {part_stats}\n"
            for stat, value in stats.items():
                formatted_card_info += f"- {stat}: {value}\n"
            formatted_card_info += "\n"
    elif isinstance(card_info, str):
        formatted_card_info += f"{part_name}: {card_info}\n"

    return formatted_card_info


# card_stats = 물마독공 / 모속강
# card_stats_value = +30 / +15
# card_name = 멸절의 폭룡왕 바칼 카드
# part_cards = {'물리/마법/독립 공격력': '+30', '모든 속성 강화': '+15'}
def create_embed(job_type, card_info, current_page, num_pages):
    embed = discord.Embed(title=f"{job_type} 직업의 카드 목록 (페이지 {current_page + 1}/{num_pages})",
                          colour=0xff7676)
    
    # 현재 페이지에 해당하는 카드 정보 가져오기
    page_cards = list(card_info.items())[current_page][1]
    
    for card_name, part_cards in page_cards.items():
        # 현재 페이지에 해당하는 부위 정보 가져오기
        current_part = list(card_info.items())[current_page][0]
        part_text = f"해당 부위: {current_part}\n" 
        part_text_added = False

        for card_stats, card_status_value in part_cards.items():  
            card_image_url = api.get_card_image_url(card_name)
            if card_image_url:
                embed.set_image(url=card_image_url)
            else:
                print("아무것도 안나와")
            
            part_text += parse_part_cards(card_stats, card_status_value)  
            part_text_added = True

        if part_text_added:
            embed.add_field(name=f"| {card_name}", value=part_text.strip(), inline=False)
    
    return embed

bot.run(TOKEN)