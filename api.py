import requests
import json
import secret
import grade
from typing import Union
from mabu import card_info

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

# 캐릭터 명성
def get_character_reputation(server: str, character_name: str) -> Union[dict, None]:
    url = f"https://api.neople.co.kr/df/servers/{SERVER_NAME_TO_ID[server]}/characters"
    params = {
        'characterName': character_name,
        'apikey': API_KEY
    }

    response = requests.get(url=url, params=params)
    
    # API 호출이 실패한 경우
    if response.status_code != 200:
        return None, None, None, None

    data = json.loads(response.text)

    characters = data.get('rows', [])

    if characters:
        character_info = characters[0]

        # 명성 정보 
        reputations = [character_info.get('fame')]

        # 캐릭터 ID
        character_id = character_info.get('characterId')

        # 캐릭터 이미지 URL
        character_image_url = f"https://img-api.neople.co.kr/df/servers/{SERVER_NAME_TO_ID[server]}/characters/{character_id}?zoom=1"

        # 직업명
        job_grow_name = character_info.get('jobGrowName')

        return reputations, character_image_url, job_grow_name
    else:
        return None, None, None
    

# 아이템 등급 관련
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
    
def get_today_item_grade(item_name: str) -> str:
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
        return {'grade_value': data.get('itemGradeValue'), 'grade_name': data.get('itemGradeName')}
    else:
        print(f"아이템 등급을 가져오는 중 오류가 발생했습니다. 응답 코드: {response.status_code}")
        return None

def get_today_item_Status(item_name: str) -> dict:
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
        return data.get('itemStatus')
    else:
        print(f"아이템 세부 상태를 가져오는 중 오류가 발생했습니다. 응답 코드: {response.status_code}")
        return None       

def get_max_grade_status(item_name: str) -> dict:
    item_id = get_item_id(item_name)

    if not item_id:
        print(f"{item_name}을(를) 찾을 수 없습니다.")
        return None

    url = f"https://api.neople.co.kr/df/items/{item_id}"
    params = {
        'apikey': API_KEY
    }

    response = requests.get(url=url, params=params)

    if response.status_code == 200:
        data = json.loads(response.text)
        return data.get('itemStatus')
    else:
        print(f"100% 상태 아이템 세부 상태를 가져오는 중 오류가 발생했습니다. 응답 코드: {response.status_code}")
        return None

# 마부 관련 함수들
def get_card_info_by_part(job_type: str, part: str) -> dict:
    if job_type in card_info:
        job_cards = card_info[job_type]
        if part in job_cards:
            return job_cards[part]
    return None

# 카드 정보 출력
def print_card_info(job_type: str) -> dict:
    if job_type in card_info:
        return card_info[job_type]
    else:
        return None



