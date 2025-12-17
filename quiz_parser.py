import re

def parse_quiz_text(text):
    """
    텍스트에서 퀴즈 정보를 파싱하여 리스트로 반환
    각 퀴즈는 딕셔너리 형태로 반환됩니다.
    """
    quizzes = []
    
    # 숫자로 시작하는 각 퀴즈를 분리
    quiz_blocks = re.split(r'\n\s*\d+\.\s*', text.strip())
    
    # 첫 번째 빈 요소 제거
    if quiz_blocks and not quiz_blocks[0].strip():
        quiz_blocks = quiz_blocks[1:]
    
    for block in quiz_blocks:
        if not block.strip():
            continue
            
        quiz = parse_single_quiz(block)
        if quiz:
            quizzes.append(quiz)
    
    return quizzes

def parse_single_quiz(block):
    """
    단일 퀴즈 블록을 파싱하여 딕셔너리로 반환
    """
    try:
        # 각 섹션을 구분하는 패턴
        patterns = {
            'room_name': r'방의\s*이름\s*[:：]\s*(.+?)(?=\n방의\s*배경\s*묘사|\n문제|\Z)',
            'background_description': r'방의\s*배경\s*묘사\s*[:：]?\s*\n(.+?)(?=\n문제|\Z)',
            'question': r'문제\s*[:：]?\s*\n(.+?)(?=\n힌트|\Z)',
            'hint': r'힌트\s*[:：]?\s*\n(.+?)(?=\n답|\Z)',
            'answer': r'답\s*[:：]?\s*\n?(.+?)(?=\n\d+\.|\Z)'
        }
        
        quiz = {}
        
        for key, pattern in patterns.items():
            match = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # 줄바꿈 보존하되 연속된 줄바꿈은 정리
                if key in ['background_description', 'question', 'hint']:
                    # 각 줄의 앞쪽 공백 제거 (들여쓰기 제거)
                    lines = value.split('\n')
                    cleaned_lines = [line.lstrip() for line in lines]  # 각 줄의 앞쪽 공백 제거
                    value = '\n'.join(cleaned_lines)
                    
                    value = re.sub(r'\n\s*\n', '\n\n', value).strip()  # 연속 줄바꿈 정리
                    value = re.sub(r'[ \t]+', ' ', value)  # 탭과 연속 공백만 정리
                quiz[key] = value
            else:
                quiz[key] = ""
        
        # 필수 필드가 모두 있는지 확인
        required_fields = ['room_name', 'background_description', 'question', 'hint', 'answer']
        if all(quiz.get(field) for field in required_fields):
            return quiz
        else:
            print(f"퀴즈 파싱 실패: 필수 필드 누락 - {quiz}")
            return None
            
    except Exception as e:
        print(f"퀴즈 파싱 중 오류 발생: {e}")
        return None

def validate_quiz(quiz):
    """
    퀴즈 데이터의 유효성을 검사
    """
    required_fields = ['room_name', 'background_description', 'question', 'hint', 'answer']
    
    for field in required_fields:
        if not quiz.get(field) or not quiz[field].strip():
            return False, f"'{field}' 필드가 비어있습니다."
    
    # 각 필드의 길이 제한 검사
    if len(quiz['room_name']) > 100:
        return False, "방의 이름이 너무 깁니다. (최대 100자)"
    
    if len(quiz['background_description']) > 1000:
        return False, "배경 묘사가 너무 깁니다. (최대 1000자)"
    
    if len(quiz['question']) > 1000:
        return False, "문제가 너무 깁니다. (최대 1000자)"
    
    if len(quiz['hint']) > 500:
        return False, "힌트가 너무 깁니다. (최대 500자)"
    
    if len(quiz['answer']) > 100:
        return False, "답이 너무 깁니다. (최대 100자)"
    
    return True, "유효한 퀴즈입니다."

def format_quiz_preview(quiz):
    """
    퀴즈를 미리보기 형태로 포맷팅
    """
    return f"""
방의 이름: {quiz['room_name']}
방의 배경 묘사: {quiz['background_description']}
문제: {quiz['question']}
힌트: {quiz['hint']}
답: {quiz['answer']}
"""

def test_parser():
    """파서 테스트 함수"""
    sample_text = """
1. 방의 이름: 거울의 미궁
방의 배경 묘사
사방이 거울로 둘러싸인 방. 바닥에도 천장에도 거울이 있어, 어디가 진짜 벽인지 구분이 어렵다.
문제
문 옆에는 '진짜 출구는 거울에 비친 문이 아닌, 실제 문이다'라는 문구가 적혀 있다. 방 안의 거울에 비친 문은 총 5개다. 실제로 열 수 있는 문은 몇 개인가?
힌트
거울에 비치는 문은 실제 문이 아니다.
답
1

2. 방의 이름: 암호화된 서재
방의 배경 묘사
고풍스러운 책장과 오래된 책들, 책상 위에는 손글씨로 적힌 쪽지가 있다.
문제
쪽지에는 "세 번째 책의 첫 글자, 다섯 번째 책의 두 번째 글자, 일곱 번째 책의 세 번째 글자를 순서대로 조합하라"라고 적혀 있다.
힌트
각 책의 해당 글자를 뽑아 조합해 보라.
답
비탈행
"""
    
    quizzes = parse_quiz_text(sample_text)
    print(f"파싱된 퀴즈 개수: {len(quizzes)}")
    
    for i, quiz in enumerate(quizzes, 1):
        print(f"\n=== 퀴즈 {i} ===")
        print(format_quiz_preview(quiz))
        
        is_valid, message = validate_quiz(quiz)
        print(f"유효성 검사: {message}")

if __name__ == "__main__":
    test_parser() 