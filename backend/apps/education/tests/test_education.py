import pytest

from education.models import QuizQuestion, UserBadge
from education.services import award_badges, weekly_leaderboard


@pytest.fixture
def quiz_questions(db):
    questions = []
    for i, diff in enumerate(['facile'] * 5):
        questions.append(QuizQuestion.objects.create(
            text=f'Question {i}?',
            difficulty=diff,
            choices=['A', 'B', 'C', 'D'],
            correct_index=0,
            explanation='Parce que.',
            points=5,
        ))
    return questions


@pytest.mark.django_db
def test_quiz_start(auth_client, quiz_questions):
    r = auth_client.post('/api/v1/education/quiz/start/', {
        'difficulty': 'facile', 'count': 3,
    }, format='json')
    assert r.status_code == 200
    assert 'session_id' in r.json()
    assert len(r.json()['questions']) == 3
    assert r.json()['timer_seconds'] == 20


@pytest.mark.django_db
def test_quiz_answer_and_finish(auth_client, quiz_questions, agent_user):
    start = auth_client.post('/api/v1/education/quiz/start/', {
        'difficulty': 'facile', 'count': 2,
    }, format='json')
    sid = start.json()['session_id']
    q = start.json()['questions'][0]
    r = auth_client.post(f'/api/v1/education/quiz/{sid}/answer/', {
        'question_id': q['id'], 'selected_index': 0,
    }, format='json')
    assert r.status_code == 200
    assert r.json()['correct'] is True
    finish = auth_client.post(f'/api/v1/education/quiz/{sid}/finish/', {}, format='json')
    assert finish.status_code == 200
    assert 'final_score' in finish.json()


@pytest.mark.django_db
def test_pedagogical_sheets_api(api_client, db):
    from education.models import PedagogicalSheet
    PedagogicalSheet.objects.create(
        title='Test', theme='nasa', content_fr='Contenu NASA', order=1,
    )
    r = api_client.get('/api/v1/education/sheets/')
    assert r.status_code == 200


@pytest.mark.django_db
def test_quiz_stats_api(api_client, db):
    from django.core.management import call_command
    call_command('seed_quiz_questions', '--force')
    r = api_client.get('/api/v1/education/quiz/stats/')
    assert r.status_code == 200
    data = r.json()
    assert data['by_level']['facile'] >= 100
    assert data['per_level_target'] == 100


@pytest.mark.django_db
def test_leaderboard_api(api_client):
    r = api_client.get('/api/v1/education/quiz/leaderboard/')
    assert r.status_code == 200
    assert 'top_10' in r.json()


@pytest.mark.django_db
def test_award_apprenti_badge(agent_user, db):
    from education.models import QuizSession
    QuizSession.objects.create(
        user=agent_user, difficulty='facile',
        score=25, questions_answered=5, completed=True,
    )
    badges = award_badges(agent_user)
    assert 'apprenti' in badges or UserBadge.objects.filter(user=agent_user, badge='apprenti').exists()


@pytest.mark.django_db
def test_weekly_leaderboard_empty():
    assert weekly_leaderboard() == []
