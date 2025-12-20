
from typing import Optional
from models.base import engine
from sqlalchemy.orm import Session, joinedload
from models.booking import Booking, StatusEnum
from models.invoice import Invoice
from models.room import Rooms

from models.invoice import PaidEnum
from services.room_service import RoomService
from datetime import date, timedelta

class BookingService():
    def __init__(self) -> None:
        self.room_service = RoomService()

    def get_booking_status(self, today, check_out, duedate, paid_status):
        
        if paid_status == PaidEnum.UNPAID and today > duedate:
            return StatusEnum.CANCELLED
        if check_out < today:
            return StatusEnum.EXPIRED
        return StatusEnum.ACTIVE

    def create_booking(self,customer_id):
        
        ''' 
         overlap check
         stutas
         create booking + invoice
         '''
        try:
            text_check_in = input("Enter check-in date(YYYY-MM-DD):")
            text_check_out = input("Enter check-out (YYYY-MM-DD):")
            total_guest = int(input("Enter total guest:"))

            year, month, day = map(int,text_check_in.split("-"))
            check_in = date(year,month,day)

            year, month, day = map(int,text_check_out.split("-"))
            check_out = date(year,month,day)
        except ValueError:
            print("Wrong format. Can not booking")
            return
        
        today = date.today()
        if check_in < today:
            print("You cannot book in the past.")

        if check_out <= check_in:
            print("check out must be after check in.")
            return
        
        if total_guest < 1 or total_guest > 4:
            print("Total guest must be between 1 - 4 per room.")
            return

        available_room = self.room_service.search_available_room(check_in,check_out,total_guest)
        self.room_service.print_room(available_room)

        if not available_room:
            return
        
        try:
            text_id = input("Enter room id (0 to cancel):")
            room_id= int(text_id)
        except ValueError:
            print("wrong id.")
            return
        
        if room_id == 0:
            return
        
        choosen_room: Optional[Rooms] = None
        for r in available_room:
            if r.id == room_id:
                choosen_room = r
                break

        if not choosen_room:
            print("This room id is not available.")
            return
        
        room_type = choosen_room.room_type

        if total_guest <= room_type.guest_capacity:
            extra_bed = 0
        else:
            extra_bed = total_guest - room_type.guest_capacity

        if extra_bed > room_type.extra_bed:
            print("This room type cannot support that many guests.")
            return

        today = date.today()
        booking_date = today
        
        duedate = booking_date + timedelta(days=10)
        paid_status = PaidEnum.UNPAID
        paid_date = None
        paid_by =  None

        status = self.get_booking_status(
            today=today,
            check_out=check_out,
            duedate=duedate,
            paid_status=paid_status)
        
        nights = (check_out -check_in).days
        amount = float(choosen_room.price)*nights

        with Session(engine) as session:
            booking = Booking(check_in = check_in,
                     check_out = check_out,
                     total_guest = total_guest,
                     extra_bed = extra_bed,
                     status = status,
                     booking_date= booking_date,
                     customer_id = customer_id,
                     room_id= choosen_room.id
            )
            invoice = Invoice(
                amount = amount,
                duedate = duedate,
                is_paid = paid_status,
                paid_date = paid_date,
                paid_by = paid_by,
                booking = booking
            )
            session.add(invoice) #invoice reference booking by using relationship
            session.commit()
            print("Booking successfully.")

    def cancel_customer_booking(self,customer_id):
        print("--------Cancle My booking---------")
        
        with Session(engine)as session:
            booking = (session.query(Booking).where(
                Booking.customer_id == customer_id,
                Booking.is_delete == False,
                Booking.status == StatusEnum.ACTIVE).all())

            if not booking:
                print("No active booking to cancel. ")
                return
            
            for b in booking:
                room = b.room
                room_type= room.room_type

                print(f"\nBooking id:{b.id}")
                print(f"Check in: {b.check_in}    Check out:{b.check_out}")
                print(f"Room Type:{room_type.room_type.value}   Extra bed:{room_type.extra_bed}")
                print(f"Guests:{b.total_guest}")
                
            
            txt = input("Enter booking id to cancel (q to quit):").lower()
            if txt == "q":
                return
            try:
                booking_id = int(txt)
            except ValueError:
                print("Wrong booking id.")
                return
            
            with Session(engine)as session:
                booking = session.get(Booking, booking_id)

                if not booking:
                    print("This booking id is not found. ")
                    return
                
                if booking.is_delete:
                    print("This booking was delete (by soft delete)")
                    return
                
                if booking.status == StatusEnum.CANCELLED:
                    print("This booking already cancelled.")
                    return
                
                invoice = booking.invoice

                if not invoice:
                    print("Invoice not found for this booking.")
                    return
                
                if invoice.is_paid == PaidEnum.PAID:
                    print("This booking was already been paid, can not cancel.")
                    return
            
                if booking.customer_id != customer_id:
                    print("You can cancel only your own booking.")
                    return

                confirm =  input(f"Cancel booking {booking.id} (y/n):").lower()
                if confirm != "y":
                    print("Skip cancellation.")
                    return
                
                booking.status = StatusEnum.CANCELLED
                session.commit()
                print("cancellation successfully.")

    def manual_cancel_booking_admin(self):
        print("--------Manual Cancle booking(Admin)---------")
        input_id = input("input bookind id to cancle (q to go back):")

        if input_id == "q":
            return
        
        try:    
            booking_id = int (input_id)

        except ValueError:
            print("Wrong booking id.")
            return
      
        with Session(engine)as session:
            booking = session.get(Booking, booking_id)

            if not booking:
                print("This booking id is not found. ")
                return
            
            if booking.is_delete:
                print("This booking was delete (by soft delete)")
                return
            
            if booking.status == StatusEnum.CANCELLED:
                print("This booking already cancelled.")
                return
            
            invoice = booking.invoice

            if not invoice:
                print("Invoice not found for this booking.")
                return
            
            if invoice.is_paid == PaidEnum.PAID:
                print("This booking was already been paid.")
                return
            
            confirm =  input(f"Cancel booking {booking.id} (y/n):").lower()
            if confirm != "y":
                print("Skip cancellation.")
                return
            
            booking.status = StatusEnum.CANCELLED
            session.commit()
            print("cancellation successfully.")

    def pay_invoice(self,customer_id):
        print("\n===== My Booking and Invoice =====")  


        with Session(engine) as session:
            invoices = (session.query(Invoice)
                        .join(Booking)
                        .where(Booking.customer_id == customer_id,
                               Invoice.is_paid == PaidEnum.UNPAID,
                               Booking.is_delete==False).all())
            if not invoices:
                print("No unpaid invoices.")
                return

            for i in invoices:
                print(f"Invoice ID:{i.id}  Booking:{i.booking_id}  Amount:{i.amount}  Due:{i.duedate}")

            txt= input("Enter invoice id to pay (q to quit):").lower()
            if txt =="q":
                return
            
            try:
                invoice_id = int(txt)
            except ValueError:
                print("Wrong invoice id.")
                return
            
            invoice = session.get(Invoice,invoice_id)
            if not invoice or invoice.is_paid == PaidEnum.PAID:
                print("Invalid invoice.")
                return
            
            booking = invoice.booking # we are making a new query
            if not booking or booking.customer_id != customer_id:
                print("This invoice does not belong to you.")
                return
            
            if booking.is_delete:
                print("This booking was delete (by soft delete)")
                return

            if booking.status == StatusEnum.CANCELLED:
                print("This booking was cancelled. Payment is not allowed.")
                return

            invoice.is_paid = PaidEnum.PAID
            invoice.paid_date = date.today()
            invoice.paid_by = f"Customer id: {customer_id}"

            
            booking.status = self.get_booking_status(
                today = date.today(),
                check_out= booking.check_out,
                duedate= invoice.duedate,
                paid_status= invoice.is_paid
            )
            session.commit()
            print("Invoice paid successfully.")

    def show_booking(self, customer_id):
        print("\n===== My Booking and Invoice =====")   
        today= date.today()


        with Session (engine) as session:
            bookings = (
                session.query(Booking)
                .options(
                    joinedload(Booking.invoice),
                    joinedload(Booking.room).joinedload(Rooms.room_type)
                    )
                    .where(
                    Booking.customer_id == customer_id,
                    Booking.is_delete == False)
                    .order_by(Booking.id.desc()).all()
            )
            if not bookings:
                print("booking not found.")
                return
            
            
            update = False #update status
            for b in bookings:
                if b.status == StatusEnum.CANCELLED:
                    continue

                invoice = b.invoice
                if invoice:
                    new_status = self.get_booking_status(
                        today= today,
                        check_out= b.check_out,
                        duedate = invoice.duedate,
                        paid_status=invoice.is_paid
                    )
                    if b.status != new_status:
                        b.status = new_status
                        update  = True

            if  update:
                session.commit()

            for b in bookings:
                room = b.room
                room_type= room.room_type

                print(f"\nBooking id:{b.id}")
                print(f"Check in: {b.check_in}    Check out:{b.check_out}")
                print(f"Room Type:{room_type.room_type.value}   Extra bed:{b.extra_bed}")
                print(f"Guests:{b.total_guest}")
                print(f"Status: {b.status.value}")

                invoice = b.invoice
                if invoice:
                    print("-----Invoice-----")
                    print(f"Invoice ID:{invoice.id}")
                    print(f"Duedate: {invoice.duedate}")
                    print(f"Amount: {invoice.amount}  kr.")
                    print(f"Paid status: {invoice.is_paid.value}")
                    print(f"Paid date:{invoice.paid_date}")
                    print(f"Paid by: {invoice.paid_by}")
                else:
                    print("Not invoice for this booking.")