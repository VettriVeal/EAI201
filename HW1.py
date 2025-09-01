import time

def vacuum_cleaner():
    print("Welcome to SmartVac 3000 - Automatic Vacuum Cleaner\n")
    room_size = input("Enter the room size (small / medium / large): ").lower()
    room_shape = input("Enter the room shape (square / rectangle / circular): ").lower()
    dust_location = input("Where is most of the dust located? (center / sides / entrance): ").lower()
    dust_quantity = input("How much dust is there? (less / medium / large): ").lower()
    dock_option = input("Should the vacuum dock itself after cleaning? (yes / no): ").lower()
    print("\nInitializing Cleaning Process...\n")
    print(f"Room Size: {room_size}")
    print(f"Room Shape: {room_shape}")
    print(f"Dust Location: {dust_location}")
    print(f"Dust Quantity: {dust_quantity}")
    print("Status: Cleaning...\n")
    time.sleep(3)
    print("Cleaning is completed.")
    if dock_option == "yes":
        print("Returning to docking station...")
        time.sleep(3)
        print("Docked successfully.")
    else:
        print("Staying in current location. Docking skipped.")

    print("\nThank you for using SmartVac 3000.")

vacuum_cleaner()
