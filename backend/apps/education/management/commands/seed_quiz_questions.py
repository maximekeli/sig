"""Charge 100 questions par niveau (facile, moyen, difficile) depuis quiz_bank."""
from django.core.management.base import BaseCommand

from education.models import QuizQuestion
from education.quiz_bank import QUESTIONS_PER_LEVEL, build_all_questions

POINTS = {
    QuizQuestion.Difficulty.EASY: 5,
    QuizQuestion.Difficulty.MEDIUM: 10,
    QuizQuestion.Difficulty.HARD: 15,
}


def _clean_text(text):
    if text.startswith('[') and '] ' in text:
        return text.split('] ', 1)[-1]
    return text


class Command(BaseCommand):
    help = f'Charge {QUESTIONS_PER_LEVEL} questions par niveau (facile, moyen, difficile).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Supprime les questions existantes et recharge la banque.',
        )

    def handle(self, *args, **options):
        if options['force']:
            deleted, _ = QuizQuestion.objects.all().delete()
            self.stdout.write(f'Supprimé {deleted} question(s).')

        banks = build_all_questions()
        created = 0
        updated = 0

        for difficulty, questions in banks.items():
            if len(questions) < QUESTIONS_PER_LEVEL:
                self.stderr.write(
                    self.style.WARNING(
                        f'{difficulty}: seulement {len(questions)} questions générées '
                        f'(attendu {QUESTIONS_PER_LEVEL})',
                    ),
                )
            for idx, q in enumerate(questions[:QUESTIONS_PER_LEVEL]):
                text = _clean_text(q['text'])
                obj, was_created = QuizQuestion.objects.update_or_create(
                    text=text,
                    difficulty=difficulty,
                    defaults={
                        'choices': q['choices'],
                        'correct_index': q['correct_index'],
                        'explanation': q['explanation'],
                        'is_nasa_topic': q.get('is_nasa_topic', False),
                        'points': POINTS.get(difficulty, 5),
                        'is_active': True,
                    },
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        total = QuizQuestion.objects.count()
        by_level = {
            d: QuizQuestion.objects.filter(difficulty=d, is_active=True).count()
            for d in ('facile', 'moyen', 'difficile')
        }
        self.stdout.write(
            self.style.SUCCESS(
                f'Quiz : {created} créées, {updated} mises à jour — '
                f'total {total} (facile={by_level["facile"]}, '
                f'moyen={by_level["moyen"]}, difficile={by_level["difficile"]})',
            ),
        )
