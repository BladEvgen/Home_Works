import os 


def email_check(email: str) -> bool:
    return False

def password_check(password: str) -> bool:
    return False


def main():
    email = input("Enter your email address: ")
    passwd = input("Enter your password: ")
    
    if email_check(email) and password_check(passwd): 
        print("Valid")

    

if __name__ == '__main__':
    main()