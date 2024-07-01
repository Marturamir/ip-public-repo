# capa de servicio/lógica de negocio

from ..transport import transport
from ..dao import repositories
from ..generic import mapper
from django.contrib.auth import get_user

def getAllImages(input=None):
    # obtiene un listado de imágenes desde transport.py y lo guarda en un json_collection.
    # ¡OJO! el parámetro 'input' indica si se debe buscar por un valor introducido en el buscador.
    #response_json_api=transport.getAllImages(input=None)

    json_collection = []
    #Guarda las cards
    images = []

    if(input==None):
        json_collection=transport.getAllImages(input=None)
    else:
        json_collection=transport.getAllImages(input=input)

    # recorre el listado de objetos JSON, lo transforma en una NASACard y lo agrega en el listado de images. Ayuda: ver mapper.py.
    #for objectjson in json_collection:
    for objectjson in json_collection:
        card = mapper.fromRequestIntoNASACard(objectjson)
        images.append(card)

    return images


def getImagesBySearchInputLike(input):
    return getAllImages(input)


# añadir favoritos (usado desde el template 'home.html')
def saveFavourite(request):
    fav = '' # transformamos un request del template en una NASACard.
    fav.user = '' # le seteamos el usuario correspondiente.

    return repositories.saveFavourite(fav) # lo guardamos en la base.


# usados en el template 'favourites.html'
def getAllFavouritesByUser(request):
    if not request.user.is_authenticated:
        return []
    else:
        user = get_user(request)

        favourite_list = [] # buscamos desde el repositorio TODOS los favoritos del usuario (variable 'user').
        favourite_list=repositories.getAllFavouritesByUser(user)
        mapped_favourites = []

        for favourite in favourite_list:
            nasa_card = mapper.fromRepositoryIntoNASACard(favourite) # transformamos cada favorito en una NASACard, y lo almacenamos en nasa_card.
            mapped_favourites.append(nasa_card)

        return mapped_favourites


def deleteFavourite(request):
    favId = request.POST.get('id')
    return repositories.deleteFavourite(favId) # borramos un favorito por su ID.