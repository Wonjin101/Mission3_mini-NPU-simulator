import json
import os
import time

# --- 1. 우리가 만든 기계들 모음 ---
# 정규화 함수 (label을 Cross, X으로 통일)
def normalize_label(label):
    if label == "+" or label == "cross":
        return "Cross"
    elif label == "x" or label == "X":
        return "X"
    else:
        return label

# 3x3 행렬 곱셈 (MAC) 계산기
def calculate_mac(pattern, filter_grid):
    total=0
    for i in range(3):
        for j in range(3):
            total += pattern[i][j] * filter_grid[i][j]
    return total

# 판정기 
def judge_winner(score_cross, score_x):
    epsilon= 0.000000001
    difference= abs(score_cross - score_x)
    if difference < epsilon:
        return "UNDECIDED"
    elif score_cross > score_x:
        return "Cross"
    else:
        return "X"

# --- 2. 진짜 실행 부분 (파일 읽고 초시계 재기) ---
print("=== Mini NPU 시뮬레이터 (파일 검사 모드) ===")

# 정답지
cross_filter= [[0, 1, 0],
               [1, 1, 1],   
               [0, 1, 0]]   
x_filter= [[1, 0, 1],
           [0, 1, 0],
           [1, 0, 1]]   

# 파일 읽기 ("지금 이 파이썬 파일이 있는 곳이랑 똑같은 방에서 data.json을 찾아라!)
Current_folder= os.path.dirname(__file__)
file_path = os.path.join(Current_folder, 'data.json')

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

student_pattern = data["pattern"]
raw_expected = data["expected"]
expected_answer = normalize_label(raw_expected)

# 초시계 시작!
start_time = time.perf_counter() #performace counter

# 100번 반복시키기
for _ in range(100):
    cross_score = calculate_mac(student_pattern, cross_filter)
    x_score = calculate_mac(student_pattern, x_filter)
    npu_result = judge_winner(cross_score, x_score)

# 초시계 끝!
end_time= time.perf_counter()

# 걸린 평균 시간 계산 (ms 단위)
avg_time_ms = ((end_time - start_time) / 100) * 1000

print(f"=== NPU 검사 결과 ===")
print(f"1. data 파일에 적힌 정답: {expected_answer}")
print(f"2. NPU가 판단한 결과: {npu_result}")

# 두 정답이 같은지 True/False로 출력
if expected_answer == npu_result: 
    print("3. 정답 일치 여부: True")
else:
    print("3. 정답 일치 여부: False")

print(f"\n 3x3 MAC 연산 평균 소요 시간: {avg_time_ms:.6f}ms ")