import os
import json
import time
import requests

API_KEY = "c9b5df47e8a21fs7b8f50ebecd85969046ecb8f9"  # 본인의 DART API 키

def load_local_corps():
    if os.path.exists("corps.json"):
        with open("corps.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def fetch_10year_financials(corp_name, dart_code):
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
    financials = {}
    years = [str(y) for y in range(2016, 2026)]
    
    for year in years:
        params = {
            "crtfc_key": API_KEY,
            "corp_code": dart_code,
            "bsns_year": year,
            "reprt_code": "11011"  # 사업보고서
        }
        try:
            res = requests.get(url, params=params, timeout=5).json()
            
            # DART API 응답 상태 확인
            status = res.get("status")
            if status != "000":
                # 에러 메시지가 있다면 출력해서 원인 확인
                # print(f"[{corp_name} {year}년] API 에러 메시지: {res.get('message')}")
                continue
                
            accounts = res.get("list", [])
            rev, op, net = 0, 0, 0
            for acc in accounts:
                if acc.get("fs_div") in ["CFS", "OFS"]:
                    name = acc.get("account_nm", "").replace(" ", "")
                    amt_str = acc.get("thstrm_amount", "0")
                    if not amt_str or amt_str == "-" or amt_str == "":
                        continue
                    try:
                        amt = int(amt_str.replace(",", "").strip())
                    except:
                        continue
                    
                    if ("매출액" in name or "수익" in name) and rev == 0:
                        rev = round(amt / 100000000)
                    elif "영업이익" in name and "법인세" not in name and op == 0:
                        op = round(amt / 100000000)
                    elif "당기순이익" in name and net == 0:
                        net = round(amt / 100000000)
            
            if rev != 0 or op != 0:
                financials[year] = {"revenue": rev, "op": op, "net": net}
                
        except Exception as e:
            print(f"[{corp_name} {year}년 예외 발생]: {e}")
            
        time.sleep(0.05)
            
    return financials

def main():
    corps = load_local_corps()
    if not corps:
        print("❌ corps.json 파일이 없습니다.")
        return

    output_filename = "corps_financials.json"
    saved_data = {}
    
    if os.path.exists(output_filename):
        with open(output_filename, "r", encoding="utf-8") as f:
            try:
                saved_data = json.load(f)
            except:
                saved_data = {}

    total_corps = len(corps)
    print(f"🚀 전체 {total_corps}개 상장사 재무 데이터 정밀 수집 시작!")

    completed_count = len(saved_data)

    for idx, corp in enumerate(corps, 1):
        corp_name = corp["name"]
        
        # 데이터가 이미 있고 비어있지 않다면 스킵
        if corp_name in saved_data and saved_data[corp_name].get("financials"):
            continue

        print(f"[{idx}/{total_corps}] ⏳ {corp_name} 데이터 수집 중...")
        fin = fetch_10year_financials(corp_name, corp["dartCode"])
        
        saved_data[corp_name] = {
            "code": corp["code"],
            "dartCode": corp["dartCode"],
            "financials": fin
        }
        completed_count += 1

        if completed_count % 5 == 0 or idx == total_corps:
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(saved_data, f, ensure_ascii=False, indent=2)
            print(f"💾 중간 저장 완료 ({len(saved_data)}/{total_corps})")

    print(f"\n🎉 재무 데이터 수집 완료!")

if __name__ == "__main__":
    main()