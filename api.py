import requests
import json
import secret
from typing import Union

API_KEY = secret.API_KEY

# 던파 서버
SERVER_NAME_TO_ID = {
        '안톤': 'anton',
        '바칼': 'bakal',
        '카인': 'cain',
        '카시야스': 'casillas',
        '디레지에': 'diregie',
        '힐더': 'hilder',
        '프레이': 'prey',
        '시로코': 'siroco',
        '전체': 'all'
    }

character_cache = {}

# 캐릭터 명성
def get_character_reputation(server: str, character_name: str) -> Union[dict, None]:
    # 캐시 키 생성
    cache_key = (server, character_name)

    # 캐시에 해당 데이터가 있는지 확인
    if cache_key in character_cache:
        return character_cache[cache_key]

    url = f"https://api.neople.co.kr/df/servers/{SERVER_NAME_TO_ID[server]}/characters"
    params = {
        'characterName': character_name,
        'apikey': API_KEY
    }

    response = requests.get(url=url, params=params)
    
    # API 호출이 실패한 경우
    if response.status_code != 200:
        return None, None

    data = json.loads(response.text)

    # 서버와 캐릭터 이름이 일치하는 캐릭터 정보가 있는지 확인
    matching_characters = [row for row in data['rows'] if row['characterName'] == character_name and row['serverId'] == SERVER_NAME_TO_ID[server]]

    if matching_characters:
        # fame 필드를 사용하여 명성 정보를 가져옴
        reputations = [char_info['fame'] for char_info in matching_characters]

        # 캐릭터 이미지 URL
        character_id = matching_characters[0]['characterId']
        character_image_url = f"https://img-api.neople.co.kr/df/servers/{SERVER_NAME_TO_ID[server]}/characters/{character_id}?zoom=1"

        # 캐시에 저장
        character_cache[cache_key] = (reputations, character_image_url)

        return reputations, character_image_url
    else:
        return None, None  # 일치하는 정보가 없으면 None 반환
    

# 아이템 등급
def get_item_id(item_name: str) -> Union[str, None]:
    url = "https://api.neople.co.kr/df/items"
    params = {
        'itemName': item_name,
        'apikey': API_KEY
    }

    response = requests.get(url=url, params=params)

    if response.status_code == 200:
        data = json.loads(response.text)
        if data['rows']:
            return data['rows'][0]['itemId']  # 첫 번째 검색 결과의 아이템 ID 반환
    return None

def get_today_item_grade() -> Union[str, None]:
    item_name = "리버시블 레더 코트"
    item_id = get_item_id(item_name)

    if not item_id:
        print(f"{item_name}을(를) 찾을 수 없습니다.")
        return None

    url = f"https://api.neople.co.kr/df/items/{item_id}/shop"
    params = {
        'apikey': API_KEY
    }

    response = requests.get(url=url, params=params)

    if response.status_code == 200:
        data = json.loads(response.text)
        return data.get('itemGradeValue')
    else:
        print(f"아이템 등급을 가져오는 중 오류가 발생했습니다. 응답 코드: {response.status_code}")
        return None

item_grade = get_today_item_grade()
if item_grade:
    print(f"오늘의 아이템 등급은 {item_grade}% 입니다.")
else:
    print("아이템 등급을 가져오는 데 실패했습니다.")