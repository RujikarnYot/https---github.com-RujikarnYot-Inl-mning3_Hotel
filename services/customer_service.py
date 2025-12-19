

from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from models.booking import Booking
from models.customer import Customers
from models.base import engine
from services.validator_service import Validator


class CustomerService():
    def __init__(self):
        self.logged_in_customer: Optional[Customers] = None

    def get_valid_first_name(self):
        while True:
            name = input("Enter first name (q to quit):")
            if name =="q":
                return None
            if Validator.is_valid_first_name(name):
                return name
            print("First name is not valid, try again")


    def get_valid_last_name(self):
        while True:
            name = input("Enter last name (q to quit):")
            if name =="q":
                return None
            if Validator.is_valid_last_name(name):
                return name
            print("Last name is not valid, try again")

    def get_valid_email(self):
        while True:
            name = input("Enter email (q to quit):")
            if name =="q":
                return None
            if Validator.is_valid_email(name):
                return name
            print("Email is not valid, try again")

    def get_birth_date(self):
        while True:
            text = input("Enter birth date (YYYY-MM-DD) (q to quit):")
            if text =="q":
                return None
            try:
                year, month, day =map(int,text.split("-"))
                return date(year, month, day)
            except ValueError:
                print("Wrong format, try again.")


    def register_customer(self):
        print("\n===== Register Customer =====")       
        first_name = self.get_valid_first_name()
        if first_name is None:
            return
        
        last_name = self.get_valid_last_name()
        if last_name is None:
            return
        
        birth_date = self.get_birth_date()
        if birth_date is None:
            return
             
        telephone = input("Enter Phone number: ")
        address = input("Enter address:")    
    
        email = self.get_valid_email()
        if email is None:
            return
        
        with Session(engine) as session:
            exist = session.query(Customers).where(Customers.email==email).first()
            if exist:
                print("This email already exists.")
                return
            
            customer = Customers(
                first_name = first_name,
                last_name = last_name,
                birth_date = birth_date,
                telephone = telephone,
                address = address,
                email = email
            )
            session.add(customer)
            session.commit()
            print("Customer registered successfully.")

    def login_customer(self):
        print("\n===== Login =====")

        email = input("Enter your email (q to quit):")
        if email == "q":
            return None
        
        
        if not Validator.is_valid_email(email):
            print("Email format is not valid.")
            return None

        with Session(engine) as session:
            customer = session.query(Customers).where(Customers.email==email).first()
            if not customer:
                print("Customer not found.")
                return None
            
            if not customer.birth_date:
                print("Birth date missing. Contact admin.")
                return None
        
            #check age >= 18
            today = date.today()
            age = today.year - customer.birth_date.year
            if (today.month, today.day) < (customer.birth_date.month, customer.birth_date.day):
                age -=1
            if age < 18:
                print("Sorry, you must be at least 18 years old to book the hotel.")
                return None
            
            self.logged_in_customer = customer
            print(f"Welcome {customer.first_name}!")
            return customer
        
    def list_customer(self):
        print("\n===== Customer List =====")    
        with Session(engine) as session:
            customers = (session.query(Customers)
            .where(Customers.is_delete == False)
            .order_by(Customers.id.asc()).all())

            if not customers:
                print("Customer not found.")
                return
            
            for c in customers:
                print(f"ID:{c.id}   Customer Name:{c.first_name} {c.last_name}  email:{c.email} tel:{c.telephone} address:{c.address}")

    def edit_customer(self,customer_id):
        print("\n===== Edit Customer =====") 
        with Session(engine) as session: 
            customer = session.get(Customers, customer_id)          
            if not customer:
                print("Customer not found.")
                return
            
            print(f"Current:{customer.first_name} {customer.last_name} | {customer.email} | {customer.telephone} | {customer.address}")

            new_first = input("New first name(Enter to skip):").strip()
            if new_first:
                if Validator.is_valid_first_name(new_first):
                    customer.first_name = new_first
                else:
                    print("First name not valid. skip update.")

            new_last = input("New last name(Enter to skip):").strip()
            if new_last:
                if Validator.is_valid_last_name(new_last):
                    customer.last_name = new_last
                else:
                    print("Last name not valid. skip update.")

            new_email = input("New Email(Enter to skip):").strip()
            if new_email:
                if not Validator.is_valid_email(new_email):
                    print("Email not valid. skip update.")
                    
                else:
                    exist = session.query(Customers).where(Customers.email == new_email,
                                                           Customers.id != customer_id).first()
                    if exist:
                        print("This email already exists. Skip update.")
                    else:
                        customer.email = new_email

            new_telephone = input("New telephone number(Enter to skip):").strip()
            if new_telephone:
                customer.telephone = new_telephone

            new_add = input("New Address(Enter to skip):").strip()
            if new_add:
                customer.address = new_add
            
            session.commit()
            print("Customer update successfully.")

    def delete_customer(self,customer_id):
        print("\n===== Delete Customer =====") 
        with Session(engine) as session:
            have_booking =session.query(Booking).where(
                Booking.customer_id == customer_id,
                Booking.is_delete == False
            ).first()

            if have_booking:
                print("Cannot delete customer: customer has booking history.")
                return
            
            customer = session.get(Customers,customer_id)
            if not customer:
                print("Customer not found")
                return
            
            if customer.is_delete:
                print("Customer already delete.")
                return

            confirm = input(f"Delete customer: {customer.first_name} {customer.last_name}? (y/n):").lower()
            if confirm != "y":
                print("Skip delete.")
                return
            customer.soft_delete()
            session.commit()
            print("Customer deleted.")
