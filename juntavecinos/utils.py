from geopy.geocoders import GoogleV3

def get_coordinates(address):
    # Inicializar el geolocalizador de Google
    geolocator = GoogleV3(api_key='AIzaSyBaJCDgENwAxLaz7IGBjo4BGkL_luzVbNY')

    # Obtener las coordenadas a partir de la dirección
    location = geolocator.geocode(address)

    if location:
        return location.latitude, location.longitude
    else:
        return None, None