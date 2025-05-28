import os
import sys
import time

# Add the project root to the path so we can import our app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from management.database_utils import check_database_exists, init_database, create_sample_data
from management.views import (
    view_all_products,
    view_all_locations,
    view_inventory_by_product,
    view_inventory_by_location,
    view_low_stock_items,
    search_products,
    update_stock_menu,
    view_all_users
)


def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_title():
    """Display a pretty title banner"""
    print("\033[1;36m")  # Cyan, bold text
    print("=" * 70)
    print("""
    ███████╗ █████╗ ███████╗████████╗ █████╗ ██████╗ ██╗
    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║
    █████╗  ███████║███████╗   ██║   ███████║██████╔╝██║
    ██╔══╝  ██╔══██║╚════██║   ██║   ██╔══██║██╔═══╝ ██║
    ██║     ██║  ██║███████║   ██║   ██║  ██║██║     ██║
    ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝                                                  
    """)
    print("=" * 70)
    print("\033[0m")  # Reset text formatting
    
    print("\033[1;33m" + "INVENTORY MANAGEMENT SYSTEM".center(70) + "\033[0m")
    print("Robust API for inventory tracking".center(70))
    print("\033[1;32m" + "A Pluralsight Course".center(70) + "\033[0m")
    print("\033[3m" + "by Nertil Poci".center(70) + "\033[0m")
    print()
    print("\033[1;34m" + "Database Management Tool".center(70) + "\033[0m")
    print("=" * 70)
    print()


def main_menu():
    """Display the main interactive menu"""
    while True:
        clear_screen()
        display_title()
        
        print("\nMAIN MENU:")
        print("1. View all products")
        print("2. View all locations")
        print("3. View inventory by product")
        print("4. View inventory by location")
        print("5. View low stock items")
        print("6. Search products")
        print("7. Update stock")
        print("8. View all users")
        print("-" * 30)
        print("9. Initialize database")
        print("10. Create sample data")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            clear_screen()
            view_all_products()
        elif choice == "2":
            clear_screen()
            view_all_locations()
        elif choice == "3":
            clear_screen()
            view_inventory_by_product()
        elif choice == "4":
            clear_screen()
            view_inventory_by_location()
        elif choice == "5":
            clear_screen()
            view_low_stock_items()
        elif choice == "6":
            clear_screen()
            search_products()
        elif choice == "7":
            clear_screen()
            update_stock_menu()
        elif choice == "8":
            clear_screen()
            view_all_users()
        elif choice == "9":
            clear_screen()
            display_title()
            print("Database Initialization")
            print("======================")
            
            db_exists = check_database_exists()
            if db_exists:
                recreate = input("Database already exists. Recreate? (y/n): ").lower()
                if recreate == 'y':
                    init_database(force_recreate=True)
                else:
                    print("Keeping existing database.")
            else:
                init_database()
                
            input("\nPress Enter to continue...")
        elif choice == "10":
            clear_screen()
            display_title()
            print("Creating Sample Data")
            print("===================")
            
            if check_database_exists():
                recreate = input("Create or recreate sample data? (y/n): ").lower()
                if recreate == 'y':
                    create_sample_data(force_recreate=True)
            else:
                print("Database doesn't exist yet. Please initialize it first.")
                
            input("\nPress Enter to continue...")
        elif choice == "0":
            clear_screen()
            display_title()
            print("\nThank you for using the Inventory Management System.")
            time.sleep(1)
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)


if __name__ == "__main__":
    try:
        # Check dependencies
        try:
            import tabulate
        except ImportError:
            print("The 'tabulate' package is required for this script.")
            print("Please install it with: pip install tabulate")
            sys.exit(1)
            
        # Run the interactive menu
        main_menu()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)