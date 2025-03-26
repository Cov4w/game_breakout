import pygame
import sys
import random
import math  # math 모듈 추가

def main():
    try:
        pygame.init()
        screen = pygame.display.set_mode((700, 800))  # 창 크기 조정
        pygame.display.set_caption("Breakout Game")
        clock = pygame.time.Clock()

        balls = [{"rect": pygame.Rect(350, 740, 20, 20), "speed": [0, 0], "delay": 0}]  # 빨간색 공만 초기화
        aiming = True  # 공 발사 준비 상태
        aim_vector = pygame.math.Vector2(0, 0)  # 공 발사 방향 벡터
        round_number = 1  # 현재 라운드
        blocks = []  # 블록 리스트
        items = []  # 아이템 리스트
        launch_position = (350, 740)  # 공 발사 위치 (초기 중앙)
        additional_balls = 0  # 아이템으로 추가된 공의 갯수
        base_launch_delay = 10  # 기본 공 발사 간격 (프레임 단위)
        max_speed_multiplier = 1 + 50 * 0.05  # 최대 속도 제한 (50개의 공 기준)
        score = 0  # 점수 초기화

        # 블록 생성 함수
        def create_blocks(round_number):
            block_width = 100  # 블록 너비
            block_height = 30  # 블록 높이
            all_positions = list(range(6))  # 6개의 블록 위치
            random_positions = random.sample(all_positions, 4)  # 6개 중 4개를 랜덤 선택
            new_blocks = [
                {"rect": pygame.Rect(col * (block_width + 5) + 50, 50, block_width, block_height), "hits": round_number}
                for col in random_positions
            ]
            return new_blocks

        # 아이템 생성 함수
        def create_item():
            return pygame.Rect(random.randint(50, 650), random.randint(100, 700), 20, 20)

        # 초기 블록 생성
        blocks.extend(create_blocks(round_number))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # 마우스 클릭 시 공 발사
                if aiming and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 마우스 왼쪽 버튼 클릭
                    speed_multiplier = min(1 + len(balls) * 0.05, max_speed_multiplier)  # 속도 제한 적용
                    launch_delay = max(1, int(base_launch_delay / speed_multiplier))  # 속도에 따라 발사 간격 조정
                    for i, ball in enumerate(balls):
                        ball["speed"] = [aim_vector.x * 5 * speed_multiplier, aim_vector.y * 5 * speed_multiplier]
                        ball["delay"] = i * launch_delay  # 각 공의 발사 지연 시간 설정
                    aiming = False

            # 마우스로 공 발사 각도 설정
            if aiming:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                aim_vector = pygame.math.Vector2(mouse_x - launch_position[0], mouse_y - launch_position[1])
                if aim_vector.length() > 0:  # 벡터 길이가 0이 아닐 때만 정규화
                    aim_vector = aim_vector.normalize()

            # 공 이동
            for ball in balls:
                if ball["delay"] > 0:  # 발사 지연 시간이 남아 있으면 대기
                    ball["delay"] -= 1
                else:  # 지연 시간이 끝난 공만 이동
                    ball["rect"].move_ip(ball["speed"])

                if ball["rect"].left <= 0 or ball["rect"].right >= 700:
                    ball["speed"][0] = -ball["speed"][0]
                if ball["rect"].top <= 0:
                    ball["speed"][1] = -ball["speed"][1]

            # 공과 블록 충돌 처리
            for block in blocks[:]:
                for ball in balls:
                    if ball["rect"].colliderect(block["rect"]):
                        # 공의 가장자리 기준으로 충돌 판정
                        ball_left = ball["rect"].left
                        ball_right = ball["rect"].right
                        ball_top = ball["rect"].top
                        ball_bottom = ball["rect"].bottom

                        block_left = block["rect"].left
                        block_right = block["rect"].right
                        block_top = block["rect"].top
                        block_bottom = block["rect"].bottom

                        # 좌우 충돌
                        if ball_right > block_left and ball_left < block_left:
                            ball["speed"][0] = -abs(ball["speed"][0])  # 좌측 반사
                        elif ball_left < block_right and ball_right > block_right:
                            ball["speed"][0] = abs(ball["speed"][0])  # 우측 반사

                        # 상하 충돌
                        if ball_bottom > block_top and ball_top < block_top:
                            ball["speed"][1] = -abs(ball["speed"][1])  # 상단 반사
                        elif ball_top < block_bottom and ball_bottom > block_bottom:
                            ball["speed"][1] = abs(ball["speed"][1])  # 하단 반사

                        block["hits"] -= 1
                        score += 1  # 점수 증가
                        if block["hits"] <= 0:  # 블록의 hits가 0 이하일 때 즉시 제거
                            blocks.remove(block)
                        break

            # 공과 아이템 충돌 처리
            for item in items[:]:
                for ball in balls:
                    if ball["rect"].colliderect(item):
                        items.remove(item)
                        additional_balls += 1  # 추가된 공 갯수 증가
                        break  # 아이템 충돌 처리 후 루프 종료

            # 공이 화면 하단으로 돌아오면 다음 라운드
            if not aiming and all(ball["rect"].top >= 800 for ball in balls):  # aiming이 False일 때만 라운드 진행
                # 마지막 공의 위치를 다음 라운드 출발 지점으로 설정
                launch_position = balls[-1]["rect"].center
                total_balls = max(1, len(balls) + additional_balls)  # 최소 공 갯수를 1로 설정
                while len(balls) < total_balls:  # 필요한 공 추가
                    balls.append({"rect": pygame.Rect(launch_position[0], launch_position[1], 20, 20), "speed": [0, 0], "delay": 0})
                for i, ball in enumerate(balls):  # 모든 공 위치와 속도 초기화
                    ball["rect"].topleft = (launch_position[0] - 10, 740)
                    ball["speed"] = [0, 0]
                    ball["delay"] = i * launch_delay  # 각 공의 발사 지연 시간 설정
                additional_balls = 0  # 추가된 공 갯수 초기화
                aiming = True
                round_number += 1

                # 기존 블록 아래로 이동
                for block in blocks:
                    block["rect"].move_ip(0, 35)

                # 새로운 블록 생성
                blocks.extend(create_blocks(round_number))

                # 블록이 바닥에 닿으면 게임 오버
                if any(block["rect"].bottom >= 800 for block in blocks):
                    print("Game Over")
                    pygame.quit()
                    sys.exit()

                # 매 라운드 아이템 생성
                items.append(create_item())

            # 화면 그리기
            screen.fill((0, 0, 0))  # 검은 배경
            for ball in balls:
                pygame.draw.ellipse(screen, (255, 0, 0), ball["rect"])  # 빨간색 공만 그림
            for block in blocks:
                pygame.draw.rect(screen, (0, 255, 255), block["rect"])  # 블록 색상 변경 (RGB: #00ffff)
                font = pygame.font.SysFont(None, 24)
                text = font.render(str(block["hits"]), True, (255, 255, 255))
                screen.blit(text, block["rect"].topleft)
            for item in items:
                pygame.draw.rect(screen, (0, 0, 255), item)  # 아이템
            if aiming:
                pygame.draw.ellipse(screen, (255, 0, 0), pygame.Rect(launch_position[0] - 10, launch_position[1] - 10, 20, 20))  # 빨간색 공 시작 위치 표시

            # 점수 표시
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))  # 왼쪽 상단에 점수 표시

            # 현재 라운드 표시
            round_text = font.render(f"Round: {round_number}", True, (255, 255, 255))
            screen.blit(round_text, (550, 10))

            pygame.display.flip()
            clock.tick(60)
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
