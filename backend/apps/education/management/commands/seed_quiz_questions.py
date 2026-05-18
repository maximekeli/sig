"""Charge 100 questions par niveau (facile, moyen, difficile) depuis quiz_bank."""
from django.core.management.base import BaseCommand

from education.models import QuizQuestion
from education.quiz_bank import QUESTIONS_PER_LEVEL, build_all_questions

POINTS = {
    'facile': 5,
    'moyen': 10,
    'difficile': 15,
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
        banks = build_all_questions()

        if options['force']:
            deleted, _ = QuizQuestion.objects.all().delete()
            self.stdout.write(f'Supprimé {deleted} question(s).')

        created = 0
        for difficulty, questions in banks.items():
            existing = QuizQuestion.objects.filter(difficulty=difficulty).count()
            if existing >= QUESTIONS_PER_LEVEL and not options['force']:
                self.stdout.write(f'{difficulty}: déjà {existing} questions — ignoré.')
                continue

            if options['force']:
                QuizQuestion.objects.filter(difficulty=difficulty).delete()

            batch = []
            for idx, q in enumerate(questions[:QUESTIONS_PER_LEVEL]):
                text = _clean_text(q['text'])
                # Garantir l'unicité si le libellé est répété dans la banque
                if QuizQuestion.objects.filter(text=text, difficulty=difficulty).exists():
                    text = f'{text} (Q{idx + 1})'
                batch.append(QuizQuestion(
                    text=text,
                    difficulty=difficulty,
                    choices=q['choices'],
                    correct_index=q['correct_index'],
                    explanation=q['explanation'],
                    is_nasa_topic=q.get('is_nasa_topic', False),
                    points=POINTS.get(difficulty, 5),
                    is_active=True,
                ))
            QuizQuestion.objects.bulk_create(batch, ignore_conflicts=False)
            created += len(batch)

        by_level = {
            d: QuizQuestion.objects.filter(difficulty=d, is_active=True).count()
            for d in ('facile', 'moyen', 'difficile')
        }
        total = QuizQuestion.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Quiz : {created} insérées — total {total} '
                f'(facile={by_level["facile"]}, moyen={by_level["moyen"]}, '
                f'difficile={by_level["difficile"]})',
            ),
        )
