
'''
auto_cancel_unpaid_booking
delete/restore booking
edit/delete customer
show admin dashboards
'''
from sqlalchemy import func,extract
from sqlalchemy.orm import Session, joinedload
from models.booking import Booking, StatusEnum
from models.invoice import Invoice, PaidEnum
from models.room import Rooms
from models.room_type import RoomType,RoomtypeEnum
from models.customer import Customers
from services.booking_service import BookingService
from services.customer_service import CustomerService
from datetime import date
from models.base import engine

class AdminService():
    def __init__(self) -> None:
        self.customer_service = CustomerService()
        self.booking_service = BookingService()

    def auto_show_unpaind_booking(self):
        '''
        show unpaid invoices
        if today > duedate(unpaind more than 10 days deadline), auto status is CANCELLED
        '''
        print("\n======= Admin : Unpaid Invoices =======")
        print("")
        today = date.today()
        update = 0

        with Session(engine) as session:
            invoices = (
                session.query(Invoice)
                .options(joinedload(Invoice.booking))
                .where(Invoice.is_paid == PaidEnum.UNPAID)
                .order_by(Invoice.duedate.asc()).all()
            )
            if not invoices:
                print("No unpaid invoice.")
                return

            for i in invoices:
                b = i.booking
                if not b:
                    continue

                if b.is_delete:
                    continue

                overdue = today > i.duedate
                txt = "OVERDUE" if overdue else "ONTIME"
                print(f"Invoice no.{i.id}  booking: {b.id}  amount:{i.amount}  duedate:{i.duedate} [{txt}]")

                if overdue and b.status == StatusEnum.ACTIVE:
                    b.status = StatusEnum.CANCELLED
                    update +=1

            if update > 0:
                session.commit()
                print(f"Auto cancelled overdue booking:{update}")

    #------------Manage customer------------
    def manage_customer(self):
        '''
        list customer
        choice id
        edit/delete
        '''
        print("\n======= Admin : Manage Customer =======")
        self.customer_service.list_customer()

        txt_id = input("Enter customer id ( q to quit):").strip()
        
        if txt_id.lower() == "q":
            return
        
        customer_id = txt_id
        
        while True:
            print("1) Edit customer")
            print("2) Delete customer")
            print("q) go back.")
            choice = input("Enter your choice(1,2 or q to quite):")

            if choice == "1":
                self.customer_service.edit_customer(customer_id)
            
            elif choice == "2":
                self.customer_service.delete_customer(customer_id)

            elif choice == "q":
                break
            else:
                print("Must choice 1,2 or q to quit.")

    #--------------manage booking------------
    def manage_booking(self):
        '''
        show booking
        choice for soft delete or cancel
        '''
        print("\n======= Admin : Manage Booking =======")
        self.list_booking_summary()

        while True:
            print("1) Cancel booking")
            print("2) Delete booking")
            print("q) go back.")
            choice = input("Enter your choice(1,2 or q to quite):")

            if choice == "1":
                self.booking_service.manual_cancel_booking_admin()
            
            elif choice == "2":
                self.soft_delete_booking()
            
            elif choice == "q":
                break
            else:
                print("Must choice 1,2 or q to quit.")
            
    def list_booking_summary(self):
        with Session(engine) as session:
            bookings = (session.query(Booking)
                        .where(Booking.is_delete == False)
                        .order_by(Booking.id.desc()).limit(10).all())
            
            if not bookings:
                print("No Booking found.")
                return
            
            print("Last newest 10 bookings:")
            for b in bookings:
                print(f"Booking id:{b.id}  customer:{b.customer_id}  check-in: {b.check_in} - {b.check_out} (status:{b.status.value})")

    def soft_delete_booking(self):
        print("\n======= Admin : Soft delete Booking =======")
        txt = input("Enter booking id to delete (q to quit):").lower()
        if txt == "q":
            return
        
        try:
            booking_id = int(txt)
        except ValueError:
            print("Wrong booking id.")
            return
        
        with Session(engine) as session:
            booking = session.get(Booking,booking_id)
            if not booking:
                print("Booking not found.")
                return
            
            if booking.is_delete:
                print("This booking already delete.")
                return
            
            confirm = input(f"Delete booking: {booking_id} (soft delete) y/n ?").lower()
            if confirm != "y":
                print("Skip delete.")
                return
            
            booking.soft_delete()
            session.commit()
            print("Soft delete successfully.")

    

#----------------statistic-------------

    def statistic_menu(self):
        while True:
            print("\n-------- Statistics --------")
            print("1) Total Customer Booking")
            print("2) Total monthly income")
            print("3) Most popular room")
            print("q) go back")
            choice = input("choose 1-3 or q to quit:").lower()
            
            if choice == "1":
                self.total_customer_booking()
            elif choice == "2":
                self.total_monthly_income()
            elif choice == "3":
                self.most_popular_room()
            elif choice == "q":
                break
            else:
                print("must choice 1-3 or q to quit.")

                

    def total_customer_booking(self):
        print("\n======= Total Customer Booking =======")

        with Session(engine) as session:
            count_rows = (session.query(Booking.customer_id,
                                        func.count(Booking.id).label("total_booking"))
                        .where(Booking.is_delete == False)
                        .group_by(Booking.customer_id)
                        .order_by(func.count(Booking.id).desc())
                        .limit(10).all())
            
            if not count_rows:
                print("No bookings data.")
                return
            
            index = 1
            for customer_id, total in count_rows:
                customer = session.get(Customers, customer_id)
    
                if customer:
                    print(f"{index}) {customer.first_name} {customer.last_name}  booking total: {total}")
                else:
                    print(f"{index}) Unknow Customer  booking total:{total}") #in case delete customer by mistake or something wrong when test
                index +=1


    def total_monthly_income(self):
        month_list = {1: "January", 2:"February", 3:"March", 4:"April",5:"May", 6:"June",
                      7:"July", 8:"August", 9:"September", 10:"October", 11:"November", 12:"December"}
        
        print("\n======= Total monthly income =======")
        txt = input("Enter year (YYYY) or q to quit:").lower()
        if txt == "q":
            return
        
        try:
            year = int(txt)
        except ValueError:
            print("Wrong year.")
            return
        with Session(engine) as session:
            count_rows = (session.query(extract("month", Invoice.paid_date).label("month"),
                                 func.sum(Invoice.amount).label("total_income"))
                        .where(Invoice.is_paid == PaidEnum.PAID,
                              Invoice.paid_date != None,
                              extract("year", Invoice.paid_date)==year)
                              .group_by(extract("month", Invoice.paid_date))
                              .order_by(extract("month", Invoice.paid_date)).all())
            if not count_rows:
                print("No income data for this year.")
                return
            
            print(f"Income report {year}:")
            for month_no, total in count_rows:
                month_name = month_list[int(month_no)]
                print(f"{month_name} : {total} kr.")
            

    def most_popular_room(self):
        print("\n======= Most Popular Room =======")

       
        with Session(engine) as session:
            count_rows = (session.query(Rooms.room_no,RoomType.room_type,
                                        func.count(Booking.id).label("total_booking"))
                        .join(Booking, Booking.room_id == Rooms.id)
                        .join(RoomType, Rooms.room_type_id == RoomType.id)
                        .where(Booking.is_delete == False)
                        .group_by(Rooms.id,Rooms.room_no,RoomType.room_type)
                        .order_by(func.count(Booking.id).desc())
                        .limit(5).all())
        
            if not count_rows:
                print("No bookings data.")
                return
            
            index = 1
            for room_no, room_type, total in count_rows:
                
                print(f"{index}) Room No:{room_no}  Room Type:{room_type.value}   booking total: {total}")
                index +=1
                    