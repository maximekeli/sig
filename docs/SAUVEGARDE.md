# Sauvegarde & restauration

## Base PostGIS

```bash
docker compose exec db pg_dump -U sig_sols sig_sols -Fc -f /tmp/sig_sols.dump
docker cp dusol_projet-db-1:/tmp/sig_sols.dump ./backups/
```

Restauration :

```bash
docker cp ./backups/sig_sols.dump dusol_projet-db-1:/tmp/
docker compose exec db pg_restore -U sig_sols -d sig_sols --clean /tmp/sig_sols.dump
```

## Médias (vidéos, photos)

Volume Docker `media_data` :

```bash
docker run --rm -v dusol_projet_media_data:/data -v $(pwd)/backups:/backup alpine \
  tar czf /backup/media.tar.gz -C /data .
```

## Fréquence recommandée

- Base : quotidien
- Médias : hebdomadaire
- Tester une restauration sur environnement de staging chaque mois
