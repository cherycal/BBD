from menu import Menu
from models.database import Database

__author__ = 'chance'
Database.initialize()

menu = Menu()

menu.run_menu()



