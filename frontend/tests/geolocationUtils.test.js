import { describe, it } from 'vitest';
import assert from 'node:assert/strict';
import {
  parseLiveUsers,
  peerLocationStyle,
  positionToPayload,
  selfLocationStyle,
} from '../js/core/geolocationUtils.js';

describe('geolocationUtils', () => {
  it('positionToPayload extracts coords', () => {
    const p = positionToPayload({
      coords: { latitude: 6.35, longitude: 1.25, accuracy: 10, heading: 90 },
    });
    assert.equal(p.lat, 6.35);
    assert.equal(p.lon, 1.25);
    assert.equal(p.accuracy_m, 10);
    assert.equal(p.heading, 90);
  });

  it('parseLiveUsers maps API response', () => {
    const users = parseLiveUsers({
      users: [{ user_id: 1, username: 'a', display_name: 'Agent', role: 'agent', lat: 6, lon: 1 }],
    });
    assert.equal(users.length, 1);
    assert.equal(users[0].displayName, 'Agent');
  });

  it('marker styles differ by role', () => {
    assert.notEqual(selfLocationStyle().fillColor, peerLocationStyle('agent').fillColor);
    assert.notEqual(peerLocationStyle('admin').fillColor, peerLocationStyle('agent').fillColor);
  });
});
