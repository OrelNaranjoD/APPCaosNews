from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from ..models import Noticia
import requests
import sys


# Diccionario para almacenar en caché los datos del clima
cache_clima = {}


def obtener_tiempo_chile():
    """Función utilitaria para obtener datos del clima de ciudades chilenas"""
    from django.conf import settings
    es_modo_prueba = (
        'test' in sys.argv or
        hasattr(settings, 'TESTING') and settings.TESTING or
        getattr(settings, 'DISABLE_EXTERNAL_APIS', False)
    )

    if es_modo_prueba:
        resultados_prueba = [
            {
                "ciudad": "Santiago",
                "temperatura": 18.5,
                "temperatura_min": 12.0,
                "temperatura_max": 24.0,
                "tiempo": "cielo claro",
                "icono": "test-icon",
            },
            {
                "ciudad": "Antofagasta",
                "temperatura": 22.0,
                "temperatura_min": 18.0,
                "temperatura_max": 26.0,
                "tiempo": "pocas nubes",
                "icono": "test-icon",
            },
        ]
        print("🧪 Usando datos de clima de prueba (APIs externas deshabilitadas)")
        return resultados_prueba

    url = "https://api.openweathermap.org/data/2.5/weather?"
    api_key = "cda050505a9bfed7a75a0663acda7e5a"
    ciudades_chile = ["Santiago", "Antofagasta", "Vina del Mar", "Concepcion", "Temuco"]

    resultados = []

    for ciudad in ciudades_chile:
        if ciudad in cache_clima:
            ciudad_info = cache_clima[ciudad]
            resultados.append(ciudad_info)
        else:
            params = {
                "appid": api_key,
                "q": ciudad + ",cl",
                "units": "metric",
                "lang": "es",
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                ciudad_info = {
                    "ciudad": data["name"],
                    "temperatura": data["main"]["temp"],
                    "temperatura_min": data["main"]["temp_min"],
                    "temperatura_max": data["main"]["temp_max"],
                    "tiempo": data["weather"][0]["description"],
                    "icono": data["weather"][0]["icon"],
                }
                resultados.append(ciudad_info)
                cache_clima[ciudad] = ciudad_info
            else:
                print(
                    f"Error en la solicitud para la ciudad {ciudad}: {response.status_code}"
                )

    return resultados


def test(request):
    """Vista para pruebas y desarrollo"""
    return render(request, "test.html")
