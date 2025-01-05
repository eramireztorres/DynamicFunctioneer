def calculate_average(numbers):
    """
    Calculates the average of a list of numbers.

    Args:
        numbers (list of float): A list of numeric values.

    Returns:
        float: The average of the list.
    """
    # Ensure the list is not empty
    if not numbers:
        return 0.0

    # Calculate the sum and divide by the length
    return sum(numbers) / len(numbers)