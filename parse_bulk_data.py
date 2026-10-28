import os
import glob
import pandas as pd

def parse_financial_data(data_dir='./data', max_file_size_mb=90):
    """
    OpenDART 대용량 텍스트 파일들을 파싱한 뒤, 
    GitHub 100MB 제한을 우회하기 위해 파일을 여러 개로 쪼개어 저장하는 함수
    """
    search_path = os.path.join(data_dir, '*.txt')
    file_list = glob.glob(search_path)
    
    if not file_list:
        print(f"경로 '{data_dir}' 내에 파싱할 .txt 파일이 없습니다.")
        return None

    df_list = []
    
    for file_path in file_list:
        print(f"처리 중: {file_path}")
        try:
            df = pd.read_csv(file_path, sep='\t', dtype=str, encoding='utf-8')
            df_list.append(df)
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, sep='\t', dtype=str, encoding='cp949')
                df_list.append(df)
            except Exception as e:
                print(f"파일 읽기 실패 ({file_path}): {e}")
        except Exception as e:
            print(f"예외 발생 ({file_path}): {e}")

    if not df_list:
        print("파싱된 데이터가 없습니다.")
        return None

    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df.columns = combined_df.columns.str.strip()

    value_cols = ['당기', '전기', '전전기']
    for col in value_cols:
        if col in combined_df.columns:
            combined_df[col] = combined_df[col].astype(str).str.replace(',', '').str.strip()
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

    # 로컬 백업용 압축 파일 저장
    output_path = os.path.join(data_dir, 'integrated_financial_data.csv.gz')
    combined_df.to_csv(output_path, index=False, encoding='utf-8-sig', compression='gzip')
    print(f"\n파싱 완료! 총 {len(combined_df):,}건의 데이터가 압축 파일로 저장되었습니다.")

    # 기존 단일 거대 파일(corps_financials.json)이 있다면 삭제 (잔여물 정리)
    if os.path.exists('corps_financials.json'):
        os.remove('corps_financials.json')
    for old_part in glob.glob('corps_financials_part_*.json'):
        os.remove(old_part)

    # 100MB 미만(기본 설정 약 90MB 단위)으로 데이터를 분할하여 여러 개의 JSON 파일로 저장
    records = combined_df.to_dict(orient='records')
    chunk_size = 50000  # 한 파일당 약 5만 행씩 분할 (용량에 따라 조절 가능)
    
    file_index = 1
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        part_filename = f'corps_financials_part_{file_index}.json'
        
        temp_df = pd.DataFrame(chunk)
        temp_df.to_json(part_filename, orient='records', force_ascii=False)
        
        print(f"분할 파일 생성 완료: {part_filename} ({len(chunk):,}건)")
        file_index += 1

    return combined_df

if __name__ == '__main__':
    TARGET_DIRECTORY = './data' 
    df_result = parse_financial_data(data_dir=TARGET_DIRECTORY)
    
    if df_result is not None:
        print("\n[상위 5개 데이터 미리보기]")
        print(df_result.head())