
import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from models import room_type
from models.base import engine
from models.customer import Customers
from models.room import Rooms
from models.room_type import RoomType,RoomtypeEnum
from models.booking import Booking, StatusEnum
from models.invoice import Invoice, PaidEnum

class Seeding(): 

    @staticmethod
    def seed_customer():
                

        with Session(engine) as session:
            if session.query(Customers).count() > 0:
                print("Customer already seeded.")
                return

            customer1 = Customers(first_name="Anna",
                                  last_name="Larsson",
                                  birth_date=date(1965,8,16,),
                                  telephone="0849951234",
                                  address="Stockholm",
                                  email="anna@gmail.com")
            
            customer2 = Customers(first_name="Marry",
                                  last_name="Svensson",
                                  birth_date=date(1983,5,5,),
                                  telephone="0611234567",
                                  address="Västerås",
                                  email="marry@gmail.com")
            
            customer3 = Customers(first_name="Tomus",
                                  last_name="Lissidan",
                                  birth_date=date(1996,3,21,),
                                  telephone="0995565522",
                                  address="Eskilstuna",
                                  email="tomus@gmail.com")
            
            customer4 = Customers(first_name="Christina",
                                  last_name="Handerson",
                                  birth_date=date(2003,3,11,),
                                  telephone="0762223333",
                                  address="Malmö",
                                  email="christina@gmail.com")

            session.add_all([customer1,customer2,customer3,customer4])
            session.commit()
            print("Customer seed completed.")
        
            customers = session.query(Customers).all()
            for c in customers:
                print(c)

    @staticmethod                
    def seed_room_type():
        with Session(engine) as session:
            count = session.query(RoomType).count()
            if count > 0:
                print("room type already seeded.")
                return
            
            single = RoomType(
                room_type = RoomtypeEnum.SINGLE,
                extra_bed = 0,
                guest_capacity=2)
            
            doubble = RoomType(
                    room_type = RoomtypeEnum.DOUBLE,
                    extra_bed = 2,
                    guest_capacity =2
                )
            session.add_all([single,doubble])
            session.commit()
            print("room_type seeding completed.")

        

    @staticmethod
    def seed_room():
        
        with Session(engine) as session:
            if session.query(Rooms).count()>0:
                print("Rooms already seeded.")
                return 
            
            single_type = session.query(RoomType).where(
                RoomType.room_type == RoomtypeEnum.SINGLE).first()
            
            double_type = session.query(RoomType).where(
                RoomType.room_type == RoomtypeEnum.DOUBLE).first()

            if not single_type or not double_type:
                print("need sigle and double type before seeding rooms.")
                return
            
            room1 = Rooms(room_no = "101",floor=1,price=750.0,room_type_id= single_type.id)
            room2 = Rooms(room_no = "102",floor=1,price=750.0,room_type_id= single_type.id)
            room3 = Rooms(room_no = "201",floor=2,price=1200.0,room_type_id= double_type.id)
            room4 = Rooms(room_no = "202",floor=2,price=1200.0,room_type_id= double_type.id)

            session.add_all([room1,room2,room3,room4])
            session.commit()
            print("Rooms seeding completed.")

            room = session.query(Rooms).all()
            for r in room:
                print(r)


    @staticmethod
    def seed_booking_and_invoice(num_booking = 500):
        
        with Session(engine) as session:
            # if session.query(Booking).count() > 0:
            #     print("booking already seeded.")
            #     return
            
            customers = session.query(Customers).all()
            rooms = session.query(Rooms).all()

            if not customers or  not rooms:
                print(" must seed customer and room before.")
                return
            
            today = date.today()
            start_date = today - timedelta(days=365)

            amount= [750.0,1200.0,1300.0,1400.0]

            

            for _ in range(num_booking):
                random_customer = random.choice(customers)
                random_room = random.choice(rooms)

                #random check in
                check_in = start_date + timedelta(days=random.randint(0,364))
                nights = random.randint(1,7)
                check_out = check_in + timedelta(days=nights)
                
                booking_date = check_in - timedelta(days=random.randint(0,14))
                if booking_date < start_date:
                    booking_date = start_date

                if check_out < today:
                    status = random.choice([
                        StatusEnum.ACTIVE,
                        StatusEnum.CANCELLED,
                        StatusEnum.EXPIRED
                    ])    
                else:
                    status = StatusEnum.ACTIVE

                deadline_pay = booking_date + timedelta(days=10)

                paid_status = random.choice([PaidEnum.PAID, PaidEnum.UNPAID])

                if paid_status == PaidEnum.PAID:
                    paid_date = booking_date+timedelta(days=random.randint(0,10))
                    paid_by = f"{random_customer.first_name} {random_customer.last_name}"

                else:
                    paid_date = None
                    paid_by = None
                
                if paid_status == PaidEnum.UNPAID and today > deadline_pay:
                    status = StatusEnum.CANCELLED

                elif  (status == StatusEnum.ACTIVE) and (check_out < today):
                    status= StatusEnum.EXPIRED

                room_type = random_room.room_type
                total_guest = random.randint(1, room_type.guest_capacity + room_type.extra_bed)

                if total_guest <= room_type.guest_capacity:
                    extra_bed = 0
                else:
                    extra_bed = total_guest - room_type.guest_capacity

                overlap = session.query(Booking).where(
                    Booking.room_id==random_room.id, Booking.is_delete == False,
                    Booking.status != StatusEnum.CANCELLED,
                    Booking.check_in < check_out, Booking.check_out> check_in
                ).first()

                if overlap:
                    #if this room have booking, skip this round
                    continue
                
                random_creat_at= start_date + timedelta(days=random.randint(0, 365))

                booking = Booking(check_in = check_in,
                     check_out = check_out,
                     total_guest = total_guest,
                     extra_bed = extra_bed,
                     status = status,
                     booking_date= booking_date,
                     customer_id = random_customer.id,
                     room_id= random_room.id,
                     create_at = random_creat_at
                     )
                     
                
                session.add(booking)
                session.flush()
                print(booking)
                invoice = Invoice(
                    amount = random.choice(amount),
                    duedate = deadline_pay,
                    is_paid = paid_status,
                    paid_date = paid_date,
                    paid_by = paid_by,
                    booking = booking
                    )
                
                # invoice.booking no join needed
               
                session.add(invoice)
                
            session.commit()


  