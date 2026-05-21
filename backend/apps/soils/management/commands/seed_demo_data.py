"""Seed demo data — L4: ≥150 points, 10 zones, quiz, NASA catalog."""
import random
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.core.management.base import BaseCommand

from soils.models import AdministrativeZone, SoilPoint

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed SIG-SOLS demo dataset (Maritime Togo pilot)'

    def add_arguments(self, parser):
        parser.add_argument('--noinput', action='store_true')

    def handle(self, *args, **options):
        from nasa.ingestion import ingest_all

        if SoilPoint.objects.count() >= 150:
            self.stdout.write('Données déjà présentes — seed ignoré.')
            return

        self._users()
        zones = self._zones()
        self._soil_points(zones)
        ingest_all()
        self._nasa_snapshots()
        self._education()
        from ml_predict.pipeline import train_and_save
        train_and_save()
        self.stdout.write(self.style.SUCCESS('Seed complete.'))

    def _users(self):
        defaults = [
            ('admin', 'admin123', User.Role.ADMIN, True, True),
            ('agent1', 'agent123', User.Role.AGENT, False, True),
            ('agent2', 'agent123', User.Role.AGENT, False, True),
            ('public1', 'public123', User.Role.PUBLIC, False, False),
        ]
        for i in range(1, 17):
            defaults.append((f'agent_pilot_{i}', 'pilot123', User.Role.AGENT, False, True))
        for username, password, role, is_super, is_staff in defaults:
            if User.objects.filter(username=username).exists():
                continue
            u = User(username=username, role=role, is_superuser=is_super, is_staff=is_staff)
            u.set_password(password)
            if username.startswith('agent_pilot'):
                pilot_num = username.split('_')[-1]
                u.pseudonym = f'Agent{pilot_num}'
                u.organization = 'DISIA Pilote'
            u.save()

    def _zones(self):
        zones = []
        min_lon, min_lat, max_lon, max_lat = 0.95, 6.05, 1.75, 6.75
        for i in range(8):
            x = min_lon + (max_lon - min_lon) * (i % 4) / 4
            y = min_lat + (max_lat - min_lat) * (i // 4) / 2
            poly = Polygon((
                (x, y), (x + 0.15, y), (x + 0.15, y + 0.2), (x, y + 0.2), (x, y),
            ))
            z, _ = AdministrativeZone.objects.get_or_create(
                code=f'CANTON-M{i+1:02d}',
                defaults={
                    'name': f'Canton Maritime {i+1}',
                    'zone_type': 'canton',
                    'geometry': MultiPolygon(poly),
                },
            )
            zones.append(z)
        for i in range(2):
            poly = Polygon((
                (1.0 + i * 0.3, 6.2), (1.25 + i * 0.3, 6.2),
                (1.25 + i * 0.3, 6.45), (1.0 + i * 0.3, 6.45), (1.0 + i * 0.3, 6.2),
            ))
            z, _ = AdministrativeZone.objects.get_or_create(
                code=f'DEG-M{i+1}',
                defaults={
                    'name': f'Zone dégradée {i+1}',
                    'zone_type': 'degraded',
                    'geometry': MultiPolygon(poly),
                },
            )
            zones.append(z)
        region_poly = Polygon((
            (0.9, 6.0), (1.8, 6.0), (1.8, 6.8), (0.9, 6.8), (0.9, 6.0),
        ))
        AdministrativeZone.objects.get_or_create(
            code='REG-MARITIME',
            defaults={
                'name': 'Région Maritime',
                'zone_type': 'region',
                'geometry': MultiPolygon(region_poly),
            },
        )
        return zones

    def _soil_points(self, zones):
        from soils.models import SoilPoint

        rng = random.Random(42)
        soil_types = ['argileux', 'sableux', 'limoneux', 'tourbeux', 'calcaire']
        fert_classes = ['faible', 'moyenne', 'elevee']
        cantons = [z for z in zones if z.zone_type == 'canton']
        for i in range(165):
            lon = rng.uniform(1.0, 1.7)
            lat = rng.uniform(6.1, 6.7)
            ph = round(rng.uniform(4.2, 8.8), 2)
            ndvi = round(rng.uniform(0.15, 0.85), 3)
            score = min(1.0, (ph - 4) / 4 * 0.35 + ndvi * 0.65)
            if score < 0.4:
                fc = 'faible'
            elif score < 0.7:
                fc = 'moyenne'
            else:
                fc = 'elevee'
            SoilPoint.objects.create(
                location=Point(lon, lat, srid=4326),
                ph=ph,
                humidity_pct=round(rng.uniform(12, 75), 1),
                soil_type=rng.choice(soil_types),
                fertility_class=rng.choice(fert_classes) if i % 5 == 0 else fc,
                fertility_score=round(score, 3),
                slope_pct=round(rng.uniform(0, 18), 2),
                ndvi_3m_avg=ndvi,
                smap_moisture_avg=round(rng.uniform(0.08, 0.42), 3),
                elevation_m=round(rng.uniform(0, 100), 1),
                source=rng.choice(['ICAT', 'IER', 'DPA', 'terrain', 'Université Lomé']),
                producer='DISIA Pilote',
                collected_at=date.today() - timedelta(days=rng.randint(30, 900)),
                zone=rng.choice(cantons) if cantons else None,
                is_validated=True,
            )

    def _nasa_snapshots(self):
        from soils.models import SoilPoint, SoilPointNasaSnapshot

        for p in SoilPoint.objects.all()[:80]:
            for months_ago in range(6):
                d = date.today() - timedelta(days=months_ago * 30)
                SoilPointNasaSnapshot.objects.get_or_create(
                    soil_point=p,
                    product='MOD13Q1_NDVI',
                    observed_at=d,
                    defaults={'value': (p.ndvi_3m_avg or 0.4) + random.uniform(-0.1, 0.1)},
                )

    def _education(self):
        from education.models import PedagogicalSheet, QuizQuestion
        from education.sheets_data import EXTRA_PEDAGOGICAL_SHEETS

        sheets = [
            (
                'Importance des sols',
                'importance',
                'Aperçu : fonctions des sols (production, filtration, carbone, biodiversité), indicateurs '
                'simples au champ et liens avec la sécurité alimentaire. '
                'Utilisez le bouton « Télécharger le PDF » pour le manuel complet (vingt pages et plus), '
                'détaillé chapitre par chapitre.',
            ),
            (
                'Types de sols au Togo',
                'types',
                'Aperçu : ferrugineux tropicaux, hydromorphes, matériaux sableux côtiers, contraintes '
                'paillage / drainage / fertilisation. Le document PDF associé développe chaque grande '
                'classe avec profils, textures et exemples d’aménagement.',
            ),
            (
                'Bonnes pratiques agricoles',
                'practices',
                'Aperçu : rotations, couvertures, réduction du labour, compost, chaulage raisonné, gestion '
                'de l’eau, agroforesterie. La version PDF regroupe plus de quarante micro-chapitres '
                'opérationnels et des listes de contrôle pour le terrain.',
            ),
            (
                'Comprendre les données NASA',
                'nasa',
                'Aperçu : NDVI (MODIS), humidité SMAP, précipitations GPM, catalogues STAC Earthdata, '
                'bonnes pratiques de citation. Le PDF complet forme pas à pas à la chaîne '
                '« produit satellite → extraction → interprétation agronomique ».',
            ),
            (
                'Érosion et dégradation',
                'erosion',
                'Aperçu : facteurs hydrologiques, ruissellement, techniques de conservation des sols, '
                'ouvrages et gouvernance locale. Le manuel PDF détaille diagnostics, seuils d’alerte '
                'et plans pluriannuels.',
            ),
        ]
        for title, theme, order, content in EXTRA_PEDAGOGICAL_SHEETS:
            sheets.append((title, theme, content))

        for order, (title, theme, content) in enumerate(sheets):
            PedagogicalSheet.objects.update_or_create(
                title=title,
                defaults={'theme': theme, 'content_fr': content, 'order': order},
            )

        if QuizQuestion.objects.filter(difficulty='facile').count() >= 100:
            return
        from django.core.management import call_command
        call_command('seed_quiz_questions')
