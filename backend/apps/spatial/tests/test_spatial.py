import pytest

from spatial import services


@pytest.mark.django_db
def test_proximity_search(sample_soil_point):
    results = services.proximity_search(1.25, 6.35, 5000)
    assert len(results) >= 1
    assert results[0]['distance_m'] >= 0


@pytest.mark.django_db
def test_proximity_api(api_client, sample_soil_point):
    r = api_client.get('/api/v1/spatial/proximity/?lon=1.25&lat=6.35&radius_m=5000')
    assert r.status_code == 200
    assert r.json()['count'] >= 1


@pytest.mark.django_db
def test_proximity_missing_params(api_client):
    r = api_client.get('/api/v1/spatial/proximity/')
    assert r.status_code == 400


@pytest.mark.django_db
def test_intersection_api(auth_client, sample_zone):
    geom = {
        'type': 'Polygon',
        'coordinates': [[[1.1, 6.2], [1.4, 6.2], [1.4, 6.4], [1.1, 6.4], [1.1, 6.2]]],
    }
    r = auth_client.post('/api/v1/spatial/intersection/', {'geometry': geom}, format='json')
    assert r.status_code == 200
    assert r.json()['count'] >= 1


@pytest.mark.django_db
def test_buffer_api(auth_client):
    geom = {'type': 'Point', 'coordinates': [1.25, 6.35]}
    r = auth_client.post('/api/v1/spatial/buffer/', {
        'geometry': geom, 'distance_m': 500,
    }, format='json')
    assert r.status_code == 200
    assert 'buffer' in r.json()


@pytest.mark.django_db
def test_area_api(auth_client):
    geom = {
        'type': 'Polygon',
        'coordinates': [[[1.0, 6.0], [1.01, 6.0], [1.01, 6.01], [1.0, 6.01], [1.0, 6.0]]],
    }
    r = auth_client.post('/api/v1/spatial/area/', {'geometry': geom}, format='json')
    assert r.status_code == 200
    assert r.json()['area_m2'] > 0


@pytest.mark.django_db
def test_vulnerability_zoning(sample_soil_point):
    data = services.vulnerability_zoning()
    assert len(data) >= 1
    assert data[0]['vulnerability'] in ('faible', 'moyenne', 'elevee')


@pytest.mark.django_db
def test_vulnerability_api(api_client, sample_soil_point):
    r = api_client.get('/api/v1/spatial/vulnerability/')
    assert r.status_code == 200


@pytest.mark.django_db
def test_smap_correlation_insufficient_data():
    result = services.smap_correlation()
    assert 'sample_size' in result


@pytest.mark.django_db
def test_parcel_analyze_polygon(auth_client, sample_soil_point, sample_zone):
    geom = {
        'type': 'Polygon',
        'coordinates': [[[1.1, 6.2], [1.4, 6.2], [1.4, 6.4], [1.1, 6.4], [1.1, 6.2]]],
    }
    r = auth_client.post('/api/v1/spatial/parcel/analyze/', {
        'geometry': geom,
        'use_ml': True,
    }, format='json')
    assert r.status_code == 200
    data = r.json()
    assert 'area' in data
    assert 'vulnerability' in data
    assert 'nasa' in data
    assert data['soil_points']['count'] >= 0


@pytest.mark.django_db
def test_parcel_analyze_by_zone_code(auth_client, sample_zone):
    r = auth_client.post('/api/v1/spatial/parcel/analyze/', {
        'zone_code': sample_zone.code,
    }, format='json')
    assert r.status_code == 200
    assert r.json()['zone_code'] == sample_zone.code


@pytest.mark.django_db
def test_parcel_zones_list(api_client, sample_zone):
    r = api_client.get('/api/v1/spatial/parcel/zones/')
    assert r.status_code == 200
    assert r.json()['count'] >= 1


@pytest.mark.django_db
def test_parcel_zones_geojson(api_client, sample_zone):
    r = api_client.get('/api/v1/spatial/parcel/zones/geojson/')
    assert r.status_code == 200
    data = r.json()
    assert data['type'] == 'FeatureCollection'
    assert len(data['features']) >= 1


@pytest.mark.django_db
def test_parcel_live_by_zone(api_client, sample_zone):
    r = api_client.get(
        f'/api/v1/spatial/parcel/live/?zone_code={sample_zone.code}&use_ml=0',
    )
    assert r.status_code == 200
    body = r.json()
    assert body['zone_code'] == sample_zone.code
    assert 'geometry_geojson' in body
    assert 'health_index' in body
    assert 'soil_points_map' in body


@pytest.mark.django_db
def test_ndvi_timeseries_empty(api_client, sample_soil_point):
    r = api_client.get(f'/api/v1/spatial/ndvi-timeseries/{sample_soil_point.id}/')
    assert r.status_code == 200
    assert 'series' in r.json()
