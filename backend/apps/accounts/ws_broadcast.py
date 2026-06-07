"""Diffusion WebSocket des positions live (groupe sig_sols_live)."""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_live_location(*, user, lat: float, lon: float) -> None:
    layer = get_channel_layer()
    if not layer:
        return
    payload = {
        'type': 'location',
        'user_id': user.pk,
        'username': user.username,
        'role': getattr(user, 'role', ''),
        'lat': lat,
        'lon': lon,
    }
    async_to_sync(layer.group_send)(
        'sig_sols_live',
        {'type': 'live_broadcast', 'payload': payload},
    )
