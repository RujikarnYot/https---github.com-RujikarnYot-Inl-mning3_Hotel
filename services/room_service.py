from urllib import request
from sqlalchemy.orm import Session, joinedload
from models.booking import Booking, StatusEnum
from models.room_type import RoomType
from models.room import Rooms
from models.base import engine



class RoomService():
    def search_available_room(self,check_in,check_out,total_guest):# -> list[Room]
        
        available_room = []
    

        with Session(engine) as session:
            rooms = (session.query(Rooms)
                     .options(joinedload(Rooms.room_type)) 
                     .join(RoomType, Rooms.room_type_id == RoomType.id)
                     .where((RoomType.guest_capacity + RoomType.extra_bed)>= total_guest)
                     .all()
                     )
            for room in rooms:
                overlap_count = (
                    session.query(Booking)
                    .where(Booking.room_id == room.id,
                    Booking.check_in < check_out,
                    Booking.check_out > check_in,
                    Booking.is_delete == False,
                    Booking.status == StatusEnum.ACTIVE
                    ).count())
            
                if overlap_count == 0:
                    available_room.append(room)

        return available_room


    def print_room(self, available_room):
        if not available_room:
            print("No rooms available.")
            return
        
        print("Available room:")
        for r in available_room:
            
            print(f"Room id:{r.id} room no:{r.room_no} floor:{r.floor} price: {r.price}")