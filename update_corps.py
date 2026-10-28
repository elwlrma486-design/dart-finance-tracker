import os
import zipfile
import urllib.request
import xml.etree.ElementTree as ET
import json

def generate_local_corps_json():
    # 본인의 OpenDART API 인증키를 여기에 직접 입력하세요
    api_key = "c9b5df47e8a21f57b8f50ebecd85969046ecb8f9"
    url = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={api_key}"
    zip_filename = "corpCode.zip"

    print("🔄 OpenDART에서 전체 기업 코드 파일 다운로드 중...")
    urllib.request.urlretrieve(url, zip_filename)

    print("📦 압축 해제 및 XML 파싱 중...")
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(".")

    tree = ET.parse("CORPCODE.xml")
    root = tree.getroot()

    listed_corps = []
    for corp in root.findall("list"):
        stock_code = corp.find("stock_code").text.strip()
        corp_name = corp.find("corp_name").text.strip()
        corp_code = corp.find("corp_code").text.strip()

        # stock_code가 공백이 아니면 실제 주식시장 상장사
        if stock_code and stock_code != "":
            listed_corps.append({
                "name": corp_name,
                "code": stock_code,
                "dartCode": corp_code
            })

    # 가나다순 정렬
    listed_corps = sorted(listed_corps, key=lambda x: x["name"])

    # 프로젝트 폴더에 corps.json으로 저장
    with open("corps.json", "w", encoding="utf-8") as f:
        json.dump(listed_corps, f, ensure_ascii=False, indent=4)

    print(f"✅ 총 {len(listed_corps)}개의 전체 상장사 데이터가 corps.json으로 저장되었습니다!")

if __name__ == "__main__":
    generate_local_corps_json()