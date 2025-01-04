
import unittest

class Inventory:

    def __init__(self):
        """
        Initializes the inventory with an empty stock dictionary.
        """
        self.stock = {}
    from d_Inventory_update_stock import update_stock

class TestInventoryUpdateStock(unittest.TestCase):
    def setUp(self):
        self.inventory = Inventory()
    def test_add_new_product(self):
        # Test adding a new product with positive quantity
        self.inventory.update_stock("Apple", 10)
        self.assertEqual(self.inventory.stock["Apple"], 10)
    def test_update_existing_product(self):
        # Test updating an existing product
        self.inventory.update_stock("Apple", 10)
        self.inventory.update_stock("Apple", 5)
        self.assertEqual(self.inventory.stock["Apple"], 15)
    def test_remove_product_stock(self):
        # Test removing stock from an existing product
        self.inventory.update_stock("Apple", 10)
        self.inventory.update_stock("Apple", -5)
        self.assertEqual(self.inventory.stock["Apple"], 5)
    def test_remove_more_than_available(self):
        # Test removing more stock than available, should raise ValueError
        self.inventory.update_stock("Apple", 5)
        with self.assertRaises(ValueError):
            self.inventory.update_stock("Apple", -10)
    def test_remove_stock_from_new_product(self):
        # Test removing stock from a non-existing product, should raise ValueError
        with self.assertRaises(ValueError):
            self.inventory.update_stock("Banana", -5)
    def test_add_zero_quantity(self):
        # Test adding zero quantity should not change the stock
        self.inventory.update_stock("Apple", 0)
        self.assertEqual(self.inventory.stock.get("Apple", 0), 0)
    def test_add_negative_quantity_to_new_product(self):
        # Test adding negative quantity to a new product should raise ValueError
        with self.assertRaises(ValueError):
            self.inventory.update_stock("Orange", -3)

if __name__ == "__main__":
    unittest.main()
