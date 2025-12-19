

from services.admin_sevice import AdminService
from services.booking_service import BookingService
from services.customer_service import CustomerService
from services.room_service import RoomService

class Menu():

    def __init__(self):
        self.customer_service = CustomerService()
        self.booking_service = BookingService()
        self.admin_service = AdminService()

        self.main_menu()

    def main_menu(self):
        while True:
            print("============================")
            print("          Main Menu         ")
            print("============================")
            print("1) Customer")
            print("2) Admin")
            print("q) Exit")
            print("============================")
            choice = input("Enter number in menu( q to quit):").strip()

            if choice == "1":
                self.customer_menu()
            elif choice == "2":
                self.admin_menu()
            elif choice == "q".lower():
                break
            else:
                print("Wrong enter, must enter 1, 2 or q to quit.")
                continue

    def customer_menu(self):
        while True:
            print("============================")
            print("       Customer Menu        ")
            print("============================")
            print("1) Register")
            print("2) Login")
            print("q) Go back")
            print("============================")
            choice = input("Enter number in menu( q to quit):").strip()

            if choice == "1":
                self.customer_service.register_customer()
                

            elif choice == "2":
                customer = self.customer_service.login_customer()
                if customer:
                    self.login_customer_menu(customer.id)

            elif choice == "q".lower():
                break
            else:
                print("Wrong enter, must enter 1, 2 or q to quit.")
                continue

    def login_customer_menu(self, customer_id):
        while True:
            print("============================")
            print("   Welcome to the system     ")
            print("============================")
            print("1) Check Date/Booking hotel")
            print("2) View Booking")
            print("3) Cancellation Booking")
            print("4) Pay Invoice")
            print("q) log out")
            print("============================")
            choice = input("Enter number in menu( q to quit):").strip()

            if choice == "1":
                self.booking_service.create_booking(customer_id)
            elif choice == "2":
                self.booking_service.show_booking(customer_id)
            elif choice == "3":
                self.booking_service.cancel_customer_booking(customer_id)
            elif choice == "4":
                self.booking_service.pay_invoice(customer_id)
            elif choice == "q".lower():
                print("Logged out.")
                break
            else:
                print("Wrong enter, must enter 1 - 4 or q to quit.")
                continue


    def admin_menu(self):
        while True:
            
            self.admin_service.auto_show_unpaind_booking()
            print("============================")
            print("         Admin Menu         ")
            print("============================")
            print("1) Manage Customers")
            print("2) Manage Bookings")
            print("3) Statistic")
            print("q) Go back")
            choice = input("Enter number in menu( q to quit):").strip()

            if choice == "1":
                self.admin_service.manage_customer()
            elif choice == "2":
                self.admin_service.manage_booking()
            elif choice == "3":
                self.admin_service.statistic_menu()
            elif choice == "q".lower():
                break
            else:
                print("Wrong enter, must enter 1 - 3 or q to quit.")
                continue