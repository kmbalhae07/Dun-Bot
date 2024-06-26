import requests
import json
import os
from typing import Union
from mabu import card_info
import sys
print(sys.path)

API_KEY = os.environ.get('DUN_API')

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

def get_character_id(server: str, character_name: str) -> Union[dict, None]:
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

        # 캐릭터 ID
        character_id = character_info.get('characterId')

        return character_id
    else:
        return None

# 캐릭터
def character(server: str, character_name: str) -> Union[dict, None]:
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
    
def get_timeline(server: str, character_name: str) -> Union[dict, None]:
    character_id = get_character_id(server, character_name)

    url = f"https://api.neople.co.kr/df/servers/{SERVER_NAME_TO_ID[server]}/characters/{character_id}"
    params = {
        'characterName': character_name,
        'apikey': API_KEY
    }

    response = requests.get(url=url, params=params)
    
    # API 호출이 실패한 경우
    if response.status_code != 200:
        return None

    data = json.loads(response.text)
    return data

def get_timeline_info(server: str, character_name: str) -> dict:
    homework_dict = {}
    this_week_thursday, next_thursday = calculate_thursday_dates()

    timeline_data = get_timeline(server, character_name)
    if timeline_data:
        for timeline_code in [201, 209]:
            url = f"https://api.neople.co.kr/df/servers/{SERVER_NAME_TO_ID[server]}/characters/{timeline_data['characterId']}/timeline"
            params = {
                'timelineCode': timeline_code,
                'apikey': API_KEY
            }
            response = requests.get(url=url, params=params)
            
            if response.status_code != 200:
                print(f"Failed to fetch timeline data for code {timeline_code}")
                continue

            timeline_info = json.loads(response.text)
            for row in timeline_info['timeline']['rows']:
                if timeline_code == 209 and row['name'] == '레기온 클리어' and row['data'].get('regionName', '') != 'N/A':
                    event_date = datetime.datetime.strptime(row['date'], '%Y-%m-%d %H:%M')
                    if this_week_thursday < event_date < next_thursday:
                        homework_dict[row['data']['regionName']] = row['date']
                if timeline_code == 201 and row['name'] == '레이드' and row['data'].get('raidName', '') != 'N/A':
                    event_date = datetime.datetime.strptime(row['date'], '%Y-%m-%d %H:%M')
                    if this_week_thursday < event_date < next_thursday:
                        homework_dict[row['data']['raidName']] = row['date']
    
    return homework_dict



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

# 100% 등급짜리 아이템 갖고오기
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
    
# 이미지 출력
def image_url(item_name: str) -> str:
    item_id = get_item_id(item_name)
    if item_id:
        return f"https://img-api.neople.co.kr/df/items/{item_id}"
    else:
        print("카드 이미지 URL을 가져올 수 없음")
        return None
    
def get_dungeon_reputation():
    return {
        "아스라한 (53680)": 53680,
        "이면경계 마스터 (55034)": 55034,
        "이면경계 익스 (51527)": 51527,
        "이면경계 노멀 (44872)": 44872,
        "상급던전 마스터 (54098)": 54098,
        "상급던전 익스 (47624)": 47624,
        "상급던전 노멀 (36132)": 36132
    }

def dungeon_comparison(reputation: int, dungeon_reputation: dict) -> dict:
    comparison_result = {}
    #.items -> 딕셔너리의 메서드. 딕셔너리의 key & value를 모두 반환하는 이터레이터 생성
    for dungeon, req_reputation in dungeon_reputation.items():
        if reputation >= req_reputation:
            comparison_result[dungeon] = '✅'
        else:
            difference = req_reputation - reputation
            comparison_result[dungeon] = f'❌ (남은 명성: {difference})'
            
    return comparison_result

def calculate_thursday_dates():
    current_date = datetime.datetime.now()

    days_until_next_thursday = (3 - current_date.weekday()) % 7
    next_thursday = current_date + datetime.timedelta(days=days_until_next_thursday)
    next_thursday = datetime.datetime.combine(next_thursday, datetime.time(10, 0))
    next_thursday -= datetime.timedelta(hours=3)

    this_week_thursday = next_thursday - datetime.timedelta(days=7)

    return this_week_thursday, next_thursday