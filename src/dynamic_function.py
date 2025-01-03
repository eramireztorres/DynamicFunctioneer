def calculate_average(numbers):
    if not numbers:
        return 0.0
    else:
        return sum(numbers) / len(numbers) if len(numbers) > 0 else 0.0