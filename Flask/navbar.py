from flask_navbar import Nav
from flask_navbar.elements import *

nav = Nav()

@nav.navigation()
def mynavbar():
    return Navbar(
        'Precise Data',
        View('Home', 'all'),
        View('Add Sample', 'addsample')
    )
