from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .client import OpenWeatherError, fetch_current, fetch_forecast, is_configured


def _parse_lat_lon(request) -> tuple[float, float]:
    try:
        lat = float(request.query_params.get('lat', ''))
        lon = float(request.query_params.get('lon', ''))
    except (TypeError, ValueError) as exc:
        raise ValueError('Paramètres lat et lon requis (nombres).') from exc
    return lat, lon


class OpenWeatherStatusView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        if not is_configured():
            return Response({
                'configured': False,
                'ok': False,
                'message': 'Ajoutez OPENWEATHER_API_KEY dans le fichier .env',
            })
        return Response({
            'configured': True,
            'ok': True,
            'message': 'OpenWeather configuré',
        })


class OpenWeatherCurrentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            lat, lon = _parse_lat_lon(request)
            return Response(fetch_current(lat, lon))
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        except OpenWeatherError as exc:
            return Response({'detail': str(exc)}, status=502)


class OpenWeatherForecastView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            lat, lon = _parse_lat_lon(request)
            return Response(fetch_forecast(lat, lon))
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        except OpenWeatherError as exc:
            return Response({'detail': str(exc)}, status=502)
