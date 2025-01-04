def update_stock(self, product, quantity):
    """
    Updates the stock for a product.
    Args:
        product (str): The name of the product.
        quantity (int): The quantity to add (positive) or remove (negative).
    Raises:
        ValueError: If quantity is negative and results in stock below zero.
    """
    # Check if the product is already in stock
    if product in self.stock:
        # Calculate the new stock level
        new_quantity = self.stock[product] + quantity
        # Raise an error if the new quantity is negative
        if new_quantity < 0:
            raise ValueError(f"Cannot reduce {product} stock below zero.")
        # Update the stock with the new quantity
        self.stock[product] = new_quantity
    else:
        # If the product is not in stock, ensure the quantity is not negative
        if quantity < 0:
            raise ValueError(f"Cannot set negative stock for a new product: {product}.")
        # Add the product to the stock
        self.stock[product] = quantity