def grade(marks):
    grades = {
        "A+": (90, 100),
        "A": (75, 89),
        "B": (60, 74),
        "C": (40, 59),
        "F": (0, 39)
    }
    for g, (low, high) in grades.items():
        if low <= marks <= high:
            return g

def student_grading():
    results = {}
    n = int(input("Enter number of subjects: "))

    for i in range(1, n + 1):
        subject = input(f"Enter subject {i} name: ")
        marks = int(input(f"Enter marks for {subject}: "))
        results[subject] = grade(marks)

    print("\n--- Report Card ---")
    for subject, grade_letter in results.items():
        print(f"{subject}: {grade_letter}")

student_grading()
