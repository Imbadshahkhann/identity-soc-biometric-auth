import sys
import database
import auth

def show_menu():
    print("\n--- BIOMETRIC AUTHENTICATION SYSTEM ---")
    print("1. Register new user")
    print("2. Login")
    print("3. Exit")
    print("---------------------------------------")

def main():
    print("Initializing system...")
    database.init_db()
    
    while True:
        show_menu()
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            username = input("Enter a new username to register: ").strip()
            if not username:
                print("Username cannot be empty.")
                continue
            auth.register_user(username)
            
        elif choice == '2':
            username = input("Enter your username to login: ").strip()
            if not username:
                print("Username cannot be empty.")
                continue
            auth.login_user(username)
            
        elif choice == '3':
            print("Exiting securely...")
            sys.exit(0)
            
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
