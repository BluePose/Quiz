from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
import os
import random
import database

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# 이미지 업로드 설정
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 배경음악 설정
MUSIC_FOLDER = 'static/music'
ALLOWED_MUSIC_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}
MAX_SINGLE_FILE_SIZE = 50 * 1024 * 1024  # 개별 파일 최대 50MB
MAX_TOTAL_UPLOAD_SIZE = 500 * 1024 * 1024  # 대량 업로드 시 총 500MB까지

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MUSIC_FOLDER'] = MUSIC_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_TOTAL_UPLOAD_SIZE  # 전체 요청 크기 제한

# 폴더가 없으면 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MUSIC_FOLDER, exist_ok=True)

def allowed_file(filename):
    """허용된 파일 확장자인지 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_music_file(filename):
    """허용된 음악 파일 확장자인지 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_MUSIC_EXTENSIONS

def get_random_background_music():
    """랜덤 배경음악 파일 경로 반환"""
    try:
        music_files = [f for f in os.listdir(MUSIC_FOLDER) 
                      if allowed_music_file(f)]
        if music_files:
            return random.choice(music_files)
        return None
    except:
        return None

@app.route('/')
def index():
    """메인 페이지 - 게임 시작 화면"""
    return render_template('game/start.html')

@app.route('/dashboard')
def dashboard():
    """대시보드 페이지"""
    total_quizzes = database.get_quiz_count()
    quizzes_without_images = len(database.get_quizzes_without_images())
    
    return render_template('dashboard.html', 
                         total_quizzes=total_quizzes,
                         quizzes_without_images=quizzes_without_images)

# 퀴즈 목록 페이지는 관리자 콘솔로 통합됨
@app.route('/quiz/list')
def quiz_list():
    """퀴즈 목록 페이지 - 관리자 콘솔로 리다이렉트"""
    return redirect(url_for('admin_console'))

@app.route('/quiz/add')
def add_quiz_page():
    """퀴즈 추가 페이지"""
    return render_template('add_quiz.html')

@app.route('/quiz/add', methods=['POST'])
def add_quiz():
    """퀴즈 추가 처리"""
    try:
        room_name = request.form.get('room_name', '').strip()
        background_description = request.form.get('background_description', '').strip()
        question = request.form.get('question', '').strip()
        hint = request.form.get('hint', '').strip()
        answer = request.form.get('answer', '').strip()
        
        if not all([room_name, background_description, question, hint, answer]):
            flash('모든 필드를 입력해주세요.', 'error')
            return redirect(url_for('add_quiz_page'))
        
        quiz_id = database.add_quiz(room_name, background_description, question, hint, answer)
        flash(f'퀴즈가 성공적으로 추가되었습니다! (ID: {quiz_id})', 'success')
        return redirect(url_for('quiz_detail', quiz_id=quiz_id))
        
    except Exception as e:
        flash(f'퀴즈 추가 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('add_quiz_page'))

@app.route('/quiz/<int:quiz_id>')
def quiz_detail(quiz_id):
    """퀴즈 상세 페이지"""
    quiz = database.get_quiz_by_id(quiz_id)
    if not quiz:
        flash('퀴즈를 찾을 수 없습니다.', 'error')
        return redirect(url_for('admin_console'))
    
    # 다음/이전 퀴즈 ID 가져오기
    prev_quiz_id, next_quiz_id = database.get_next_prev_quiz_ids(quiz_id)
    
    return render_template('quiz_detail.html', quiz=quiz, 
                         prev_quiz_id=prev_quiz_id, next_quiz_id=next_quiz_id)

@app.route('/quiz/<int:quiz_id>/edit')
def edit_quiz_page(quiz_id):
    """퀴즈 편집 페이지"""
    quiz = database.get_quiz_by_id(quiz_id)
    if not quiz:
        flash('퀴즈를 찾을 수 없습니다.', 'error')
        return redirect(url_for('admin_console'))
    
    # 다음/이전 퀴즈 ID 가져오기
    prev_quiz_id, next_quiz_id = database.get_next_prev_quiz_ids(quiz_id)
    
    return render_template('edit_quiz.html', quiz=quiz, 
                         prev_quiz_id=prev_quiz_id, next_quiz_id=next_quiz_id)

@app.route('/quiz/<int:quiz_id>/update', methods=['POST'])
def update_quiz_route(quiz_id):
    """퀴즈 업데이트 처리"""
    try:
        quiz = database.get_quiz_by_id(quiz_id)
        if not quiz:
            flash('퀴즈를 찾을 수 없습니다.', 'error')
            return redirect(url_for('admin_console'))
            
        room_name = request.form.get('room_name', '').strip()
        background_description = request.form.get('background_description', '').strip()
        question = request.form.get('question', '').strip()
        hint = request.form.get('hint', '').strip()
        answer = request.form.get('answer', '').strip()
        
        if not all([room_name, background_description, question, hint, answer]):
            flash('모든 필드를 입력해주세요.', 'error')
            return redirect(url_for('edit_quiz_page', quiz_id=quiz_id))
        
        # 기존 이미지 경로 유지
        current_image_path = quiz[6]  # image_path는 인덱스 6
        
        success = database.update_quiz(quiz_id, room_name, background_description, 
                                     question, hint, answer, current_image_path)
        
        if success:
            flash('퀴즈가 성공적으로 수정되었습니다!', 'success')
        else:
            flash('퀴즈 수정에 실패했습니다.', 'error')
            
        return redirect(url_for('quiz_detail', quiz_id=quiz_id))
        
    except Exception as e:
        flash(f'퀴즈 수정 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('edit_quiz_page', quiz_id=quiz_id))

@app.route('/quiz/<int:quiz_id>/delete', methods=['POST'])
def delete_quiz_route(quiz_id):
    """퀴즈 삭제 처리"""
    try:
        quiz = database.get_quiz_by_id(quiz_id)
        if not quiz:
            flash('퀴즈를 찾을 수 없습니다.', 'error')
            return redirect(url_for('admin_console'))
        
        # 이미지 파일이 있다면 삭제
        if quiz[6]:  # image_path
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], quiz[6])
            if os.path.exists(image_path):
                os.remove(image_path)
        
        success = database.delete_quiz(quiz_id)
        
        if success:
            flash('퀴즈가 성공적으로 삭제되었습니다.', 'success')
        else:
            flash('퀴즈 삭제에 실패했습니다.', 'error')
            
    except Exception as e:
        flash(f'퀴즈 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('admin_console'))

@app.route('/quiz/<int:quiz_id>/upload-image', methods=['POST'])
def upload_quiz_image(quiz_id):
    """퀴즈 이미지 업로드 처리"""
    try:
        quiz = database.get_quiz_by_id(quiz_id)
        if not quiz:
            return jsonify({'success': False, 'message': '퀴즈를 찾을 수 없습니다.'})
        
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': '이미지 파일이 선택되지 않았습니다.'})
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': '이미지 파일이 선택되지 않았습니다.'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': f'허용되지 않는 파일 형식입니다. ({", ".join(ALLOWED_EXTENSIONS)}만 가능)'})
        
        # 기존 이미지 파일 삭제
        old_image_path = quiz[6]  # image_path
        if old_image_path:
            old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_image_path)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        
        # 새 파일명 생성 (quiz_id를 포함하여 고유하게)
        if file.filename and '.' in file.filename:
            file_extension = file.filename.rsplit('.', 1)[1].lower()
        else:
            file_extension = 'png'  # 기본 확장자
        new_filename = f'quiz_{quiz_id}_scene.{file_extension}'
        
        # 파일 저장
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(file_path)
        
        # 데이터베이스 업데이트
        success = database.update_quiz_image(quiz_id, new_filename)
        
        if success:
            return jsonify({
                'success': True, 
                'message': '이미지가 성공적으로 업로드되었습니다!',
                'image_path': new_filename
            })
        else:
            # 파일은 저장되었지만 DB 업데이트 실패 시 파일 삭제
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'success': False, 'message': '데이터베이스 업데이트에 실패했습니다.'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'이미지 업로드 중 오류가 발생했습니다: {str(e)}'})

@app.route('/admin')
def admin_console():
    """관리자 콘솔 페이지"""
    all_quizzes = database.get_all_quizzes()
    quizzes_without_images = database.get_quizzes_without_images()
    
    # 배경음악 파일 목록 가져오기
    music_files = []
    try:
        music_files = [f for f in os.listdir(MUSIC_FOLDER) 
                      if allowed_music_file(f)]
    except:
        music_files = []
    
    return render_template('admin_console.html', 
                         all_quizzes=all_quizzes,
                         quizzes_without_images=quizzes_without_images,
                         music_files=music_files)

@app.route('/admin/music/bulk-upload', methods=['POST'])
def bulk_upload_music():
    """대량 배경음악 업로드 처리"""
    try:
        if 'music_files' not in request.files:
            return jsonify({'success': False, 'message': '파일이 선택되지 않았습니다.'})
        
        files = request.files.getlist('music_files')
        
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'message': '파일이 선택되지 않았습니다.'})
        
        uploaded_count = 0
        error_messages = []
        
        for file in files:
            if file and file.filename:
                # 파일 확장자 검증
                if not allowed_music_file(file.filename):
                    error_messages.append(f'{file.filename}: 지원하지 않는 파일 형식입니다.')
                    continue
                
                # 파일 크기 검증
                file.seek(0, 2)  # 파일 끝으로 이동
                file_size = file.tell()
                file.seek(0)  # 파일 시작으로 복귀
                
                if file_size > MAX_SINGLE_FILE_SIZE:
                    error_messages.append(f'{file.filename}: 파일 크기가 50MB를 초과합니다.')
                    continue
                
                # 파일명 보안 처리
                filename = secure_filename(file.filename)
                
                # 중복 파일명 처리
                base_name, ext = os.path.splitext(filename)
                counter = 1
                original_filename = filename
                
                while os.path.exists(os.path.join(MUSIC_FOLDER, filename)):
                    filename = f"{base_name}_{counter}{ext}"
                    counter += 1
                
                try:
                    file.save(os.path.join(MUSIC_FOLDER, filename))
                    uploaded_count += 1
                except Exception as e:
                    error_messages.append(f'{original_filename}: 업로드 실패 - {str(e)}')
        
        # 결과 메시지 구성
        if uploaded_count > 0:
            success_message = f'{uploaded_count}개 파일이 성공적으로 업로드되었습니다.'
            if error_messages:
                success_message += f' (실패: {len(error_messages)}개)'
            
            return jsonify({
                'success': True, 
                'message': success_message,
                'uploaded_count': uploaded_count,
                'errors': error_messages
            })
        else:
            return jsonify({
                'success': False, 
                'message': '업로드된 파일이 없습니다.',
                'errors': error_messages
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'업로드 중 오류가 발생했습니다: {str(e)}'})

@app.route('/admin/music/delete/<filename>', methods=['POST'])
def delete_music(filename):
    """배경음악 삭제"""
    try:
        file_path = os.path.join(app.config['MUSIC_FOLDER'], secure_filename(filename))
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'success': True, 'message': '배경음악이 삭제되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '파일을 찾을 수 없습니다.'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'음악 삭제 중 오류가 발생했습니다: {str(e)}'})

@app.route('/api/random-music')
def get_random_music():
    """랜덤 배경음악 API"""
    music_file = get_random_background_music()
    if music_file:
        return jsonify({'success': True, 'music_file': music_file})
    else:
        return jsonify({'success': False, 'message': '배경음악이 없습니다.'})

# ==================== 플레이어 게임 라우트 ====================

@app.route('/play')
def game_start():
    """게임 시작 화면"""
    return render_template('game/start.html')

@app.route('/play/enter', methods=['POST'])
def game_enter():
    """게임 입장 - 새 게임 세션 시작"""
    # 게임 세션 초기화
    session['game_active'] = True
    session['current_round'] = 1
    session['total_rounds'] = random.randint(5, 20)  # 5~20 라운드 랜덤
    session['lives'] = 3  # 목숨 3개
    session['hints_used'] = 0  # 사용한 힌트 수
    session['max_hints'] = 5  # 최대 힌트 수
    session['completed_quiz_ids'] = []  # 완료한 퀴즈 ID들
    session['current_quiz_id'] = None
    
    # 첫 번째 퀴즈 선택
    return redirect(url_for('game_play'))

@app.route('/play/game')
def game_play():
    """게임 플레이 화면"""
    if not session.get('game_active'):
        return redirect(url_for('game_start'))
    
    # 현재 라운드가 총 라운드를 초과하면 클리어
    if session['current_round'] > session['total_rounds']:
        return redirect(url_for('game_clear'))
    
    # 목숨이 0이면 게임 오버
    if session['lives'] <= 0:
        return redirect(url_for('game_over'))
    
    # 새 퀴즈 선택 (이미 완료한 퀴즈 제외)
    all_quizzes = database.get_all_quizzes()
    available_quizzes = [q for q in all_quizzes if q[0] not in session['completed_quiz_ids']]
    
    if not available_quizzes:
        # 모든 퀴즈를 다 풀었으면 처음부터 다시
        session['completed_quiz_ids'] = []
        available_quizzes = all_quizzes
    
    current_quiz = random.choice(available_quizzes)
    session['current_quiz_id'] = current_quiz[0]
    
    return render_template('game/play.html', 
                         quiz=current_quiz,
                         current_round=session['current_round'],
                         total_rounds=session['total_rounds'],
                         lives=session['lives'],
                         hints_used=session['hints_used'],
                         max_hints=session['max_hints'])

@app.route('/play/answer', methods=['POST'])
def game_answer():
    """답 제출 처리"""
    if not session.get('game_active'):
        return jsonify({'success': False, 'message': '게임이 활성화되지 않았습니다.'})
    
    user_answer = request.form.get('answer', '').strip()
    quiz_id = session.get('current_quiz_id')
    
    if not user_answer:
        return jsonify({'success': False, 'message': '답을 입력해주세요.'})
    
    quiz = database.get_quiz_by_id(quiz_id)
    if not quiz:
        return jsonify({'success': False, 'message': '퀴즈를 찾을 수 없습니다.'})
    
    correct_answer = quiz[5]  # 정답
    
    # 대소문자 구분 없이 비교 (영어 답변 고려)
    if user_answer.lower() == correct_answer.lower():
        # 정답!
        session['completed_quiz_ids'].append(quiz_id)
        session['current_round'] += 1
        
        if session['current_round'] > session['total_rounds']:
            # 게임 클리어
            return jsonify({
                'success': True, 
                'correct': True,
                'message': '정답입니다!',
                'redirect': url_for('game_clear')
            })
        else:
            # 다음 라운드로
            return jsonify({
                'success': True, 
                'correct': True,
                'message': '정답입니다! 다음 방으로 이동합니다...',
                'redirect': url_for('game_play')
            })
    else:
        # 오답
        session['lives'] -= 1
        
        if session['lives'] <= 0:
            # 게임 오버
            return jsonify({
                'success': True,
                'correct': False,
                'message': f'틀렸습니다. 정답은 "{correct_answer}"입니다.',
                'lives': session['lives'],
                'redirect': url_for('game_over')
            })
        else:
            # 목숨 하나 차감
            return jsonify({
                'success': True,
                'correct': False,
                'message': f'틀렸습니다. 남은 목숨: {session["lives"]}개',
                'lives': session['lives']
            })

@app.route('/play/hint', methods=['POST'])
def game_hint():
    """힌트 요청 처리"""
    if not session.get('game_active'):
        return jsonify({'success': False, 'message': '게임이 활성화되지 않았습니다.'})
    
    if session['hints_used'] >= session['max_hints']:
        return jsonify({'success': False, 'message': '더 이상 힌트를 사용할 수 없습니다.'})
    
    quiz_id = session.get('current_quiz_id')
    quiz = database.get_quiz_by_id(quiz_id)
    
    if not quiz:
        return jsonify({'success': False, 'message': '퀴즈를 찾을 수 없습니다.'})
    
    session['hints_used'] += 1
    
    return jsonify({
        'success': True,
        'hint': quiz[4],  # 힌트
        'hints_used': session['hints_used'],
        'max_hints': session['max_hints']
    })

@app.route('/play/clear')
def game_clear():
    """게임 클리어 화면"""
    if not session.get('game_active'):
        return redirect(url_for('game_start'))
    
    total_rounds = session.get('total_rounds', 0)
    hints_used = session.get('hints_used', 0)
    
    # 게임 세션 종료
    session['game_active'] = False
    
    return render_template('game/clear.html', 
                         total_rounds=total_rounds,
                         hints_used=hints_used)

@app.route('/play/over')
def game_over():
    """게임 오버 화면"""
    current_round = session.get('current_round', 1)
    total_rounds = session.get('total_rounds', 0)
    
    # 게임 세션 종료
    session['game_active'] = False
    
    return render_template('game/over.html',
                         current_round=current_round,
                         total_rounds=total_rounds)

if __name__ == '__main__':
    import os

    # Render에서는 환경변수 PORT로 포트를 넘겨줌
    port = int(os.environ.get("PORT", 5000))

    # 배포 시에는 init_database()를 여기서 호출하지 않고,
    # 별도 스크립트나 첫 요청 시에만 한 번 돌리는 것도 고려.

    # 데이터베이스 초기화
    database.init_database()
    
    # 샘플 퀴즈 자동 로드 (퀴즈가 없을 때만)
    if database.get_quiz_count() == 0:
        try:
            from add_sample_data import add_sample_quizzes
            add_sample_quizzes()
            print("✅ 샘플 퀴즈가 자동으로 로드되었습니다!")
        except Exception as e:
            print(f"⚠️ 샘플 퀴즈 로드 실패: {e}")
    
    print("🎮 방탈출 게임이 시작되었습니다!")
    print("🌐 게임 시작: http://localhost:5000")
    print("⚙️ 관리자: http://localhost:5000/dashboard")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 