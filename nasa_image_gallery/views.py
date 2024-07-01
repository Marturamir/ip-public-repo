# capa de vista/presentación
# si se necesita algún dato (lista, valor, etc), esta capa SIEMPRE se comunica con services_nasa_image_gallery.py

from django.shortcuts import redirect, render
from .layers.services import services_nasa_image_gallery
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,logout as logout_de_django,login as login_de_django
from django.http import HttpResponse
from .layers.services import services_nasa_image_gallery
from .layers.dao import repositories
from .layers.generic import nasa_card
from django.contrib import messages
from django.contrib.auth.models import User


# función que invoca al template del índice de la aplicación.
def index_page(request):
    return render(request, 'index.html')

# auxiliar: retorna 2 listados -> uno de las imágenes de la API y otro de los favoritos del usuario.
def getAllImagesAndFavouriteList(request):
    images = []
    favourite_list = []

    busqueda_var=request.POST.get('query', '')

    if(busqueda_var==''):
        images = services_nasa_image_gallery.getAllImages(input=None)
        favourite_list = services_nasa_image_gallery.getAllFavouritesByUser(request)
    else:
        images = services_nasa_image_gallery.getAllImages(input=busqueda_var)
        favourite_list = services_nasa_image_gallery.getAllFavouritesByUser(request)

    return images, favourite_list

# función principal de la galería.
def home(request):
    # llama a la función auxiliar getAllImagesAndFavouriteList() y obtiene 2 listados: uno de las imágenes de la API y otro de favoritos por usuario*.
    # (*) este último, solo si se desarrolló el opcional de favoritos; caso contrario, será un listado vacío [].
    #images = services_nasa_image_gallery.getAllImages(input=None)
    images = []
    favourite_list = []

    images,favourite_list=getAllImagesAndFavouriteList(request)

    return render(request, 'home.html', {'images': images, 'favourite_list': favourite_list} )


# función utilizada en el buscador.
def search(request):
    images, favourite_list = getAllImagesAndFavouriteList(request)
    search_msg = request.POST.get('query', '')

    # si el usuario no ingresó texto alguno, debe refrescar la página; caso contrario, debe filtrar aquellas imágenes que posean el texto de búsqueda.
    if search_msg == '':
        print('No se escribio en el input de busqueda')
        return redirect('home')
    else:
        '''Si se escribio en el input se envian las imagenes obtenidas de la funcion "getAllImagesAndFavouriteList"
        y se vuelve a renderizar el template home.hmtl'''
        return render(request, 'home.html', {'images': images} )
       

def login(request):
    if(request.method == "POST"):
        #Se obtienen los valores del formulario
        username=request.POST.get('username')
        password=request.POST.get('password')

        '''Se usa el modelo User de Django el cual verifica si el usuario
        existe en la base de datos,en este caso comprueba en la base de datos 'db.sqlite.3' '''
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "El nombre de usuario no existe.")
            return redirect('login')

        '''Se utiliza la funcion authenticate para verificar,si la contraseña es correcta
        para el username que se paso'''
        user = authenticate(username=username, password=password)

        if(user is not None):
            print("Usuario autorizado")
            
            '''
            Se inicia la sesion pasandole el objeto user como parametro,esto lo que hace es añadir
            a la sesion actual(por eso se le pasa el request como parametro)el objeto usuario.
            Esto con elfin de por ejemplo verificar en los templates si el usuario esta autenticado 
            (Ejemplo: -> {% if request.user.is_authenticated %} )
            En el caso de las views con el decorador @login_required se verifica que el usuario este logueado,
            sino no se le deja acceder a la view.
            Tener en cuenta que @login_required solamente verifica si hay un
            usuario en la sesion,no comprueba ni contraseñas ni nombres de usuarios,por ese motivo es que antes
            de añadirlo a la sesion se usa la funcion authenticate proporcionado por Django
            '''
            login_de_django(request, user)
            return redirect('home')
        else:
            messages.error(request, "Contraseña incorrecta")
            return redirect('login')
           
        
    if(request.method == "GET"):
        return render(request, 'registration/login.html')
        
# las siguientes funciones se utilizan para implementar la sección de favoritos: traer los favoritos de un usuario, guardarlos, eliminarlos y desloguearse de la app.
@login_required
def getAllFavouritesByUser(request):
    favourite_list = []
    favourite_list=services_nasa_image_gallery.getAllFavouritesByUser(request)
    return render(request, 'favourites.html', {'favourite_list': favourite_list})


@login_required
def saveFavourite(request):
    title=request.POST.get('title')
    description=request.POST.get('description')
    image_url=request.POST.get('image_url')
    date=request.POST.get('date')
    user=request.user
    
    card = nasa_card.NASACard(title=title,description=description,image_url=image_url,date=date,user=user)
    
    favr=repositories.saveFavourite(card)
    
    return redirect('home')


@login_required
def deleteFavourite(request):
    services_nasa_image_gallery.deleteFavourite(request)
    return redirect('favoritos')


@login_required
def exit(request):
    print("Cerrando sesion del usuario ...")
    #Se destruye la sesion y se redirige nuevamente al login
    logout_de_django(request)
    return redirect('login')