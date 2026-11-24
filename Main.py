import json
import os
import time

# ==========================================
# 1. 공통 핵심 함수 정의 (4대 모듈)
# ==========================================

# 1) 라벨 정규화 함수 (표준 라벨: Cross, X)
def normalize_label(label):
    clean = str(label).strip().lower()
    if clean in ["+", "cross"]:
        return "Cross"
    elif clean in ["x"]:
        return "X"
    return str(label).strip()


# 2) 사용자 콘솔 입력 및 검증 함수 (3x3 기준)
def get_user_input(name, size=3):
    print(f"\n[{name} 입력] (한 줄에 숫자 {size}개를 공백으로 구분해 입력하세요)")
    grid = []
    for i in range(size):
        while True:
            line = input(f"  {i + 1}번째 줄: ")
            tokens = line.split()
            if len(tokens) != size:
                print(f"    [!] 입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요.")
                continue
            try:
                row = [float(val) for val in tokens]
                grid.append(row)
                break
            except ValueError:
                print("    [!] 입력 형식 오류: 숫자만 입력할 수 있습니다. 다시 입력하세요.")
    return grid


# 3) MAC 연산 함수 (외부 라이브러리 없이 N x N 처리)
def calculate_mac(pattern, filter_grid):
    size = len(pattern)
    total = 0.0
    for i in range(size):
        for j in range(size):
            total += pattern[i][j] * filter_grid[i][j]
    return total


# 4) 부동소수점 허용오차(epsilon) 기반 판정 함수
def judge_winner(score_a, score_b, label_a="Cross", label_b="X"):
    epsilon = 1e-9  # 0.000000001
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    elif score_a > score_b:
        return label_a
    else:
        return label_b


# 5) 연산 성능 측정 함수 (I/O 제외 순수 연산 시간 측정)
def measure_performance(pattern, filter_a, filter_b, iterations=10):
    start_time = time.perf_counter()
    for _ in range(iterations):
        calculate_mac(pattern, filter_a)
        calculate_mac(pattern, filter_b)
    end_time = time.perf_counter()
    # 1회 MAC 연산 기준 평균 시간(ms) 계산
    avg_time_ms = ((end_time - start_time) / (iterations * 2)) * 1000
    return avg_time_ms


# ==========================================
# 2. 메인 실행 제어부 (모드 1 & 모드 2)
# ==========================================

def main():
    print("=== 🚀 Mini NPU 시뮬레이터 메인 메뉴 ===")
    print("1. 사용자 키보드 입력 모드 (3x3)")
    print("2. JSON 파일 자동 검사 모드 (data.json)")
    print("========================================")

    choice = input("원하시는 모드를 선택하세요 (1 또는 2): ").strip()

    # ---------- [모드 1] 사용자 입력 모드 ----------
    if choice == "1":
        print("\n[모드 1] 사용자 키보드 입력 모드를 시작합니다!")

        filter_a = get_user_input("필터 A (예: 십자가 필터)", size=3)
        filter_b = get_user_input("필터 B (예: X자 필터)", size=3)
        student_pattern = get_user_input("입력 패턴", size=3)

        score_a = calculate_mac(student_pattern, filter_a)
        score_b = calculate_mac(student_pattern, filter_b)
        npu_result = judge_winner(score_a, score_b, label_a="A", label_b="B")
        avg_time_ms = measure_performance(student_pattern, filter_a, filter_b, iterations=100)

        print("\n--- 채점 및 성능 결과 ---")
        print(f"필터 A MAC 점수: {score_a:.6f}")
        print(f"필터 B MAC 점수: {score_b:.6f}")
        print(f"최종 판정 결과: {npu_result}")
        print(f"3x3 MAC 연산 평균 소요 시간: {avg_time_ms:.6f} ms")

    # ---------- [모드 2] JSON 파일 자동 검사 모드 ----------
    elif choice == "2":
        print("\n[모드 2] JSON 파일 자동 검사 모드를 시작합니다!")

        current_folder = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_folder, "data.json")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print("[!] 오류: 같은 폴더에 data.json 파일이 없습니다.")
            return
        except json.JSONDecodeError as e:
            print(f"[!] 오류: data.json 파일의 JSON 형식이 올바르지 않습니다. ({e})")
            return

        filters_data = data.get("filters", {})
        patterns_data = data.get("patterns", {})

        total_count = 0
        pass_count = 0
        fail_count = 0
        fail_cases = []
        perf_records = {}  # 크기별 성능 기록용

        print("\n--- 케이스별 NPU 검사 결과 ---")
        for case_key, case_info in patterns_data.items():
            total_count += 1
            try:
                # 1) 키에서 크기(N) 추출 (예: "size_5_1" -> 5)
                parts = case_key.split("_")
                n = int(parts[1])
                size_key = f"size_{n}"

                # 2) 필터 존재 여부 및 정규화 매핑 확인
                if size_key not in filters_data:
                    raise ValueError(f"해당 크기({size_key})의 필터가 data.json에 없습니다.")

                raw_filters = filters_data[size_key]
                norm_filters = {normalize_label(k): v for k, v in raw_filters.items()}

                if "Cross" not in norm_filters or "X" not in norm_filters:
                    raise ValueError(f"{size_key}에 Cross 또는 X 필터가 누락되었습니다.")

                cross_filter = norm_filters["Cross"]
                x_filter = norm_filters["X"]
                student_pattern = case_info["input"]
                expected_answer = normalize_label(case_info["expected"])

                # 3) 스키마 및 배열 크기 일치 검증
                if len(student_pattern) != n or any(len(row) != n for row in student_pattern):
                    raise ValueError(f"패턴 크기가 {n}x{n}과 일치하지 않습니다.")
                if len(cross_filter) != n or len(x_filter) != n:
                    raise ValueError(f"필터 크기가 {n}x{n}과 일치하지 않습니다.")

                # 4) MAC 연산 및 판정
                cross_score = calculate_mac(student_pattern, cross_filter)
                x_score = calculate_mac(student_pattern, x_filter)
                npu_result = judge_winner(cross_score, x_score, label_a="Cross", label_b="X")

                # 5) 크기별 첫 정상 케이스에 대해 성능 측정 (최소 10회 이상 반복)
                if n not in perf_records:
                    perf_records[n] = measure_performance(
                        student_pattern, cross_filter, x_filter, iterations=100
                    )

                # 6) PASS / FAIL 판별
                if npu_result == expected_answer:
                    status = "PASS"
                    pass_count += 1
                else:
                    status = "FAIL"
                    fail_count += 1
                    fail_cases.append((case_key, f"예상값({expected_answer}) != 판정값({npu_result})"))

                print(
                    f"[{case_key}] Cross: {cross_score:.2f} | X: {x_score:.2f} "
                    f"| 판정: {npu_result} | 정답: {expected_answer} -> {status}"
                )

            except Exception as e:
                fail_count += 1
                fail_cases.append((case_key, f"데이터/스키마 오류: {e}"))
                print(f"[{case_key}] -> FAIL (사유: {e})")

        # 3x3 기본 성능도 표에 함께 포함하기 위해 측정
        if 3 not in perf_records:
            sample_3 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
            filter_3_a = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
            filter_3_b = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]
            perf_records[3] = measure_performance(sample_3, filter_3_a, filter_3_b, iterations=100)

        # --- 성능 분석 표 출력 ---
        print("\n--- 크기별 MAC 연산 성능 분석 ---")
        print(f"{'크기 (N×N)':<12} | {'평균 시간 (ms)':<16} | {'연산 횟수 (N²)':<12}")
        print("-" * 46)
        for n in sorted(perf_records.keys()):
            print(f"{f'{n}×{n}':<12} | {perf_records[n]:<16.6f} | {n * n:<12}")

        # --- 최종 요약 리포트 출력 ---
        print("\n--- 최종 테스트 요약 리포트 ---")
        print(f"전체 테스트 수: {total_count} | 통과(PASS): {pass_count} | 실패(FAIL): {fail_count}")
        if fail_cases:
            print("실패 케이스 목록:")
            for cid, reason in fail_cases:
                print(f" - {cid}: {reason}")
        else:
            print("실패 케이스 목록: 없음 (모든 테스트 통과)")

    else:
        print("\n[!] 삐빅! 1 또는 2만 입력하셔야 합니다. 프로그램을 종료합니다.")


if __name__ == "__main__":
    main()