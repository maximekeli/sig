import pytest
from django.contrib.gis.geos import Point
from django.utils import timezone

from accounts.models import UserLocation
from accounts.services import list_live_locations, upsert_user_location


@pytest.mark.django_db
def test_upsert_location(auth_client, agent_user):
    r = auth_client.post('/api/v1/auth/location/', {
        'lat': 6.35, 'lon': 1.25, 'accuracy_m': 12, 'is_sharing': True,
    }, format='json')
    assert r.status_code == 200
    assert r.json()['lat'] == pytest.approx(6.35, abs=0.001)
    assert UserLocation.objects.filter(user=agent_user).exists()


@pytest.mark.django_db
def test_upsert_outside_bbox(auth_client):
    r = auth_client.post('/api/v1/auth/location/', {
        'lat': 3.0, 'lon': 1.0,
    }, format='json')
    assert r.status_code == 400


@pytest.mark.django_db
def test_live_locations(auth_client, agent_user, admin_user):
    upsert_user_location(agent_user, 1.25, 6.35)
    upsert_user_location(admin_user, 1.30, 6.40)
    r = auth_client.get('/api/v1/auth/locations/live/')
    assert r.status_code == 200
    assert r.json()['count'] >= 1


@pytest.mark.django_db
def test_delete_location(auth_client, agent_user):
    upsert_user_location(agent_user, 1.25, 6.35)
    assert auth_client.delete('/api/v1/auth/location/').status_code == 204
    assert not UserLocation.objects.filter(user=agent_user).exists()


@pytest.mark.django_db
def test_get_my_location_404(auth_client):
    assert auth_client.get('/api/v1/auth/location/').status_code == 404


@pytest.mark.django_db
def test_get_my_location_ok(auth_client, agent_user):
    upsert_user_location(agent_user, 1.25, 6.35)
    r = auth_client.get('/api/v1/auth/location/')
    assert r.status_code == 200
    assert r.json()['username'] == 'test_agent'


@pytest.mark.django_db
def test_live_locations_include_self(auth_client, agent_user):
    upsert_user_location(agent_user, 1.25, 6.35)
    r = auth_client.get('/api/v1/auth/locations/live/?include_self=1')
    assert r.status_code == 200
    assert r.json()['count'] >= 1


@pytest.mark.django_db
def test_user_location_str(agent_user):
    loc = upsert_user_location(agent_user, 1.25, 6.35)
    assert agent_user.username in str(loc)


@pytest.mark.django_db
def test_stale_locations_excluded(agent_user, admin_user):
    upsert_user_location(agent_user, 1.25, 6.35)
    loc = UserLocation.objects.get(user=agent_user)
    UserLocation.objects.filter(pk=loc.pk).update(
        updated_at=timezone.now() - timezone.timedelta(hours=2),
    )
    upsert_user_location(admin_user, 1.30, 6.40)
    assert list_live_locations().count() == 1
