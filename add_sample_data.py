from database import add_quiz

# 제공받은 10개의 샘플 퀴즈 데이터
sample_quizzes = [
    {
        "room_name": "거울의 미궁",
        "background_description": "사방이 거울로 둘러싸인 방. 바닥에도 천장에도 거울이 있어, 어디가 진짜 벽인지 구분이 어렵다. 한쪽 벽에는 단 하나의 문이 있다.",
        "question": "문 옆에는 '진짜 출구는 거울에 비친 문이 아닌, 실제 문이다'라는 문구가 적혀 있다. 방 안의 거울에 비친 문은 총 5개다. 실제로 열 수 있는 문은 몇 개인가?",
        "hint": "거울에 비치는 문은 실제 문이 아니다.",
        "answer": "1"
    },
    {
        "room_name": "암호화된 서재",
        "background_description": "고풍스러운 책장과 오래된 책들, 책상 위에는 손글씨로 적힌 쪽지가 있다.",
        "question": "쪽지에는 '세 번째 책의 첫 글자, 다섯 번째 책의 두 번째 글자, 일곱 번째 책의 세 번째 글자를 순서대로 조합하라'라고 적혀 있다. 책 제목은 각각 '마법', '시간', '비밀', '열쇠', '방탈출', '지혜', '여행'이다.",
        "hint": "각 책의 해당 글자를 뽑아 조합해 보라.",
        "answer": "비탈행"
    },
    {
        "room_name": "어둠 속의 실험실",
        "background_description": "불이 꺼진 실험실. 책상 위에는 랜턴, 성냥, 양초, 건전지, 전구가 놓여 있다.",
        "question": "실험실의 불을 켤 수 있는 단 하나의 물건을 먼저 사용해야 한다면, 무엇을 선택해야 하는가?",
        "hint": "불을 붙이거나 빛을 내려면 가장 먼저 필요한 것이 무엇인지 생각해 보라.",
        "answer": "성냥"
    },
    {
        "room_name": "시간의 방",
        "background_description": "네 개의 시계가 각각 다른 시간을 가리키고 있다. 벽에는 '가장 빠른 시계가 답을 말한다'라는 문구가 있다.",
        "question": "시계가 각각 3:15, 2:50, 4:05, 1:40을 가리키고 있다. 분침이 가장 먼저 12를 지나치는 시계는 몇 시를 가리키고 있는가?",
        "hint": "분침이 12를 먼저 지나치는 순서를 생각해 보라.",
        "answer": "2:50"
    },
    {
        "room_name": "추리의 서재",
        "background_description": "책상 위에 세 개의 봉투가 놓여 있고, 각각 'A', 'B', 'C'라고 적혀 있다.",
        "question": "A: '정답은 B다.' B: '정답은 C다.' C: '나는 거짓말을 하고 있다.' 오직 하나만 진실을 말한다면, 정답은 어느 봉투인가?",
        "hint": "각 문장을 논리적으로 대입해 보라.",
        "answer": "A"
    },
    {
        "room_name": "빛과 그림자의 방",
        "background_description": "방 중앙에 전등이 있고, 네 개의 물체(구, 정육면체, 원기둥, 삼각뿔)가 바닥에 놓여 있다.",
        "question": "전등을 켜면, 바닥에 그림자가 완전히 원형으로 드리워지는 물체는 무엇인가?",
        "hint": "모든 방향에서 그림자가 원이 되는 물체를 생각해 보라.",
        "answer": "구"
    },
    {
        "room_name": "숫자의 미로",
        "background_description": "벽에는 2, 6, 12, 20, ? 라는 숫자들이 적혀 있다.",
        "question": "물음표에 들어갈 다음 숫자는 무엇인가?",
        "hint": "각 숫자의 차이를 관찰해 보라.",
        "answer": "30"
    },
    {
        "room_name": "심리의 방",
        "background_description": "방 한가운데 투명한 상자가 있고, 그 안에 빨간 공 하나가 들어 있다. 상자 옆에는 '진짜 색을 말하라'는 쪽지가 있다.",
        "question": "상자에 파란색 조명이 켜지면, 상자 안의 공은 무슨 색으로 보이는가?",
        "hint": "조명 색과 실제 공 색의 관계를 생각해 보라.",
        "answer": "보라"
    },
    {
        "room_name": "관찰자의 갤러리",
        "background_description": "여러 그림이 전시된 갤러리. 한 그림만이 액자가 거꾸로 걸려 있다.",
        "question": "모든 그림 제목의 첫 글자를 순서대로 읽으면 '방탈출'이 된다. 거꾸로 걸린 액자의 그림 제목은 무엇인가?",
        "hint": "'방탈출'의 마지막 글자를 찾아보라.",
        "answer": "출"
    },
    {
        "room_name": "생존의 창고",
        "background_description": "냉장고, 깨진 유리, 밧줄, 사다리, 물통이 있는 창고. 창문이 높이 있어 탈출하려면 도구가 필요하다.",
        "question": "이 방에서 가장 안전하게 창문까지 올라갈 수 있는 도구는 무엇인가?",
        "hint": "안전성과 실용성을 모두 고려해 보라.",
        "answer": "사다리"
    }
]

def add_sample_quizzes():
    """샘플 퀴즈 데이터를 데이터베이스에 추가"""
    print("샘플 퀴즈 데이터를 추가하는 중...")
    
    for i, quiz in enumerate(sample_quizzes, 1):
        try:
            quiz_id = add_quiz(
                quiz["room_name"],
                quiz["background_description"],
                quiz["question"],
                quiz["hint"],
                quiz["answer"]
            )
            print(f"{i:2d}. {quiz['room_name']} (ID: {quiz_id}) ✓")
        except Exception as e:
            print(f"{i:2d}. {quiz['room_name']} - 오류: {e}")
    
    print(f"\n총 {len(sample_quizzes)}개의 샘플 퀴즈 추가 완료!")

if __name__ == "__main__":
    add_sample_quizzes() 