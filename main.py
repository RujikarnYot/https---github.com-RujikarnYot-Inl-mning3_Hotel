

from menu import Menu
from seeding import Seeding

if __name__ == '__main__':
    choice = input("Run seeding? (y/n): ").strip().lower()

    if choice == "y":
        Seeding.seed_room_type()
        Seeding.seed_room()
        Seeding.seed_customer()
        Seeding.seed_booking_and_invoice(1000)

    Menu()

  
