import sqlite3
import os
from datetime import datetime

DATABASE_NAME = 'escape_room_quizzes.db'

def init_database():
    """데이터베이스 초기화 및 테이블 생성"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT NOT NULL,
            background_description TEXT NOT NULL,
            question TEXT NOT NULL,
            hint TEXT NOT NULL,
            answer TEXT NOT NULL,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 리더보드 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            total_rounds INTEGER NOT NULL,
            hints_used INTEGER NOT NULL,
            completion_time INTEGER NOT NULL,
            score INTEGER DEFAULT 0,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 기존 테이블에 image_path 컬럼이 없다면 추가
    cursor.execute("PRAGMA table_info(quizzes)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'image_path' not in columns:
        cursor.execute('ALTER TABLE quizzes ADD COLUMN image_path TEXT')
        print("이미지 경로 필드가 추가되었습니다.")
    
    conn.commit()
    conn.close()
    print("데이터베이스가 초기화되었습니다.")

def add_quiz(room_name, background_description, question, hint, answer, image_path=None):
    """퀴즈를 데이터베이스에 추가"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO quizzes (room_name, background_description, question, hint, answer, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (room_name, background_description, question, hint, answer, image_path))
    
    quiz_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return quiz_id

def get_all_quizzes():
    """모든 퀴즈 조회"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, room_name, background_description, question, hint, answer, image_path, created_at
        FROM quizzes ORDER BY created_at DESC
    ''')
    
    quizzes = cursor.fetchall()
    conn.close()
    return quizzes

def get_quiz_by_id(quiz_id):
    """ID로 특정 퀴즈 조회"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, room_name, background_description, question, hint, answer, image_path, created_at
        FROM quizzes WHERE id = ?
    ''', (quiz_id,))
    
    quiz = cursor.fetchone()
    conn.close()
    return quiz

def delete_quiz(quiz_id):
    """퀴즈 삭제"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM quizzes WHERE id = ?', (quiz_id,))
    deleted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    return deleted_count > 0

def get_quiz_count():
    """전체 퀴즈 개수 조회"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM quizzes')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count

def update_quiz(quiz_id, room_name, background_description, question, hint, answer, image_path=None):
    """퀴즈 수정"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE quizzes 
        SET room_name = ?, background_description = ?, question = ?, hint = ?, answer = ?, image_path = ?
        WHERE id = ?
    ''', (room_name, background_description, question, hint, answer, image_path, quiz_id))
    
    updated_count = cursor.rowcount
    conn.commit()
    conn.close()
    return updated_count > 0

def update_quiz_image(quiz_id, image_path):
    """퀴즈의 이미지 경로만 업데이트"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE quizzes 
        SET image_path = ?
        WHERE id = ?
    ''', (image_path, quiz_id))
    
    updated_count = cursor.rowcount
    conn.commit()
    conn.close()
    return updated_count > 0

def get_quizzes_without_images():
    """이미지가 없는 퀴즈들 조회"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, room_name, background_description
        FROM quizzes 
        WHERE image_path IS NULL OR image_path = ''
        ORDER BY id
    ''')
    
    quizzes = cursor.fetchall()
    conn.close()
    return quizzes

def get_next_prev_quiz_ids(current_quiz_id):
    """현재 퀴즈의 다음/이전 퀴즈 ID 조회"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # 모든 퀴즈 ID를 생성일 순으로 정렬하여 가져오기
    cursor.execute('SELECT id FROM quizzes ORDER BY created_at DESC')
    quiz_ids = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    if current_quiz_id not in quiz_ids:
        return None, None
    
    current_index = quiz_ids.index(current_quiz_id)
    
    # 이전 퀴즈 (인덱스가 더 작은 것, 즉 더 최근 것)
    prev_quiz_id = quiz_ids[current_index - 1] if current_index > 0 else None
    
    # 다음 퀴즈 (인덱스가 더 큰 것, 즉 더 오래된 것)
    next_quiz_id = quiz_ids[current_index + 1] if current_index < len(quiz_ids) - 1 else None
    
    return prev_quiz_id, next_quiz_id

def clear_all_quizzes():
    """모든 퀴즈 삭제 (개발용)"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM quizzes')
    conn.commit()
    conn.close()
    print("모든 퀴즈가 삭제되었습니다.")

def add_leaderboard_entry(player_name, total_rounds, hints_used, completion_time, score=0):
    """리더보드에 새 기록 추가"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO leaderboard (player_name, total_rounds, hints_used, completion_time, score)
            VALUES (?, ?, ?, ?, ?)
        ''', (player_name, total_rounds, hints_used, completion_time, score))
        
        entry_id = cursor.lastrowid
        conn.commit()
        return entry_id
    except sqlite3.Error as e:
        print(f"리더보드 추가 오류: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_leaderboard(limit=20):
    """리더보드 조회 (상위 기록들)"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT player_name, total_rounds, hints_used, completion_time, score, completed_at
            FROM leaderboard 
            ORDER BY score DESC, completion_time ASC, hints_used ASC
            LIMIT ?
        ''', (limit,))
        
        records = cursor.fetchall()
        return records
    except sqlite3.Error as e:
        print(f"리더보드 조회 오류: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_leaderboard_count():
    """리더보드 총 기록 수"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM leaderboard')
        count = cursor.fetchone()[0]
        return count
    except sqlite3.Error as e:
        print(f"리더보드 카운트 오류: {e}")
        return 0
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_database() 