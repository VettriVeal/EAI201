print("Welcome to the Vacuum Cleaner Control Program!")
print("Available commands: start, stop, left, right, dock")
print("Type 'exit' to quit.\n")

while True:
    command = input("Enter command: ").lower()

    if command == "exit":
        print("Your room is cleaned! Goodbye.")
        break
    elif command == "start":
        print("Vacuum started cleaning.")
    elif command == "stop":
        print("Vacuum stopped.")
    elif command == "left":
        print("Vacuum moved left.")
    elif command == "right":
        print("Vacuum moved right.")
    elif command == "dock":
        print("Vacuum returned to dock.")
    else:
        print("Invalid command. Please try again.")
