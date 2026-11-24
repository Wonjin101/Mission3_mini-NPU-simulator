def get_user_input(name):
    print(f"\n{name}입력] (숫자 3개를 띄어서 입력하세요)")
    grid= []

    for i in range(3):
        while True:
            line= input(f" {i+1}번째 줄:")
            tokens =line.split()

            if len(tokens) != 3:
                print("숫자가 3개가 아닙니다. 다시 입력하세요.")
                continue

            try:
                row=[float(tokens[0]), float(tokens[1]), float(tokens[2])]
                grid.append(row)
                break
            except ValueError:
                print("숫자가 아닌 값이 있습니다. 다시 입력하세요.")
    return grid

def calculate_mac(pattern, filter_grid):
    total = 0
    for i in range(3):
        for j in range(3):
            total += pattern[i][j] * filter_grid[i][j]
    return total

def judge_winner(score_cross, score_x):
    epsilon = 0.000000001
    difference = abs(score_cross - score_x)

    if difference < epsilon:
        return "같은 그림"
    elif score_cross > score_x:
        return "십자가"
    else:
        return "x자"

print("=== Mini NPU 시뮬레이터 (사용자 입력 모드) ===")
cross_filter = get_user_input("십자가")
x_filter = get_user_input("x자")

student_pattern = get_user_input("학생 패턴")

cross_score = calculate_mac(student_pattern, cross_filter)
x_score = calculate_mac(student_pattern, x_filter)

print("\n--- 채점 결과 ---")
print(f"십자가 점수: {cross_score:.6f}")
print(f"x자 점수: {x_score:.6f}")
print("최종 결과:", judge_winner(cross_score, x_score))