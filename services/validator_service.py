

class Validator():
   
    @staticmethod
    def is_valid_first_name(first_name):
        try:
            first_name = first_name.strip()
            return (
                2 <= len(first_name) <= 255
                and first_name.isalpha() 
                and first_name.isascii()
                )
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_last_name(last_name):
        try:
            last_name = last_name.strip()
            return (
                    2 <= len(last_name) <= 255
                    and last_name.isalpha() 
                    and last_name.isascii()
                    )
        except ValueError:
            return False
        
    @staticmethod
    def is_valid_email(email):
        try:
            email = email.strip()
            return (
                    1 <= len(email) <= 255
                    and "@" in email and "."in email 
                    and email.count("@") ==1
                    and not email.startswith("@")
                    and not email.endswith("@")
                    )
        except TypeError:
            return False
    