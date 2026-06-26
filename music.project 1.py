# =============================================================
# Musical Instrument Inventory System
# =============================================================

import json
import os

DATA_FILE = "instruments_data.json"


class Instrument:
    """Represents a musical instrument in the inventory."""

    def __init__(self, instrument_id, name, category, brand, price, quantity, condition="New"):
        self.instrument_id = instrument_id
        self.name = name
        self.category = category
        self.brand = brand
        self.price = price
        self.quantity = quantity
        self.condition = condition

    def to_dict(self):
        """Convert instrument object to dictionary for JSON serialization."""
        return {
            "instrument_id": self.instrument_id,
            "name": self.name,
            "category": self.category,
            "brand": self.brand,
            "price": self.price,
            "quantity": self.quantity,
            "condition": self.condition,
        }

    @staticmethod
    def from_dict(data):
        """Create an Instrument object from a dictionary."""
        return Instrument(
            instrument_id=data["instrument_id"],
            name=data["name"],
            category=data["category"],
            brand=data["brand"],
            price=data["price"],
            quantity=data["quantity"],
            condition=data.get("condition", "New"),
        )

    def __str__(self):
        return (
            f"ID: {self.instrument_id} | {self.name} ({self.brand})\n"
            f"   Category : {self.category}\n"
            f"   Price    : ${self.price:.2f}\n"
            f"   Quantity : {self.quantity}\n"
            f"   Condition: {self.condition}"
        )


class InventorySystem:
    """Manages the collection of musical instruments."""

    CATEGORIES = [
        "String", "Wind", "Percussion", "Keyboard", "Brass", "Electronic"
    ]
    CONDITIONS = ["New", "Good", "Fair", "Poor", "Damaged"]

    def __init__(self):
        self.instruments = {}  # instrument_id -> Instrument
        self.load_data()

    # ---- Core CRUD Operations ----

    def add_instrument(self):
        """Add a new instrument to the inventory."""
        print("\n--- Add New Instrument ---")
        instrument_id = input("Enter Instrument ID: ").strip()
        if instrument_id in self.instruments:
            print(f"Error: Instrument with ID '{instrument_id}' already exists!")
            return

        name = input("Enter Instrument Name (e.g., Acoustic Guitar): ").strip()
        if not name:
            print("Error: Name cannot be empty!")
            return

        print(f"Categories: {', '.join(self.CATEGORIES)}")
        category = input("Enter Category: ").strip().title()
        if category not in self.CATEGORIES:
            print(f"Warning: '{category}' is not a standard category. Added anyway.")

        brand = input("Enter Brand: ").strip()
        if not brand:
            print("Error: Brand cannot be empty!")
            return

        try:
            price = float(input("Enter Price ($): ").strip())
            if price < 0:
                print("Error: Price cannot be negative!")
                return
        except ValueError:
            print("Error: Invalid price! Must be a number.")
            return

        try:
            quantity = int(input("Enter Quantity: ").strip())
            if quantity < 0:
                print("Error: Quantity cannot be negative!")
                return
        except ValueError:
            print("Error: Invalid quantity! Must be an integer.")
            return

        print(f"Conditions: {', '.join(self.CONDITIONS)}")
        condition = input("Enter Condition (default: New): ").strip().title() or "New"
        if condition not in self.CONDITIONS:
            print(f"Warning: '{condition}' is not a standard condition. Added anyway.")

        instrument = Instrument(instrument_id, name, category, brand, price, quantity, condition)
        self.instruments[instrument_id] = instrument
        self.save_data()
        print(f"\nSuccess: '{name}' added to inventory!")

    def view_all_instruments(self):
        """Display all instruments in the inventory."""
        print("\n--- All Instruments in Inventory ---")
        if not self.instruments:
            print("No instruments in inventory.")
            return

        print(f"{'=' * 60}")
        for instrument in self.instruments.values():
            print(instrument)
            print("-" * 60)
        print(f"Total instruments: {len(self.instruments)}")
        print(f"Total stock units: {sum(i.quantity for i in self.instruments.values())}")
        print(f"Total inventory value: ${sum(i.price * i.quantity for i in self.instruments.values()):.2f}")

    def search_instrument(self):
        """Search for an instrument by ID, name, or brand."""
        print("\n--- Search Instrument ---")
        print("1. Search by ID")
        print("2. Search by Name")
        print("3. Search by Brand")
        print("4. Search by Category")
        choice = input("Enter search option (1-4): ").strip()

        results = []

        if choice == "1":
            instrument_id = input("Enter Instrument ID: ").strip()
            instrument = self.instruments.get(instrument_id)
            if instrument:
                results.append(instrument)
        elif choice == "2":
            keyword = input("Enter name keyword: ").strip().lower()
            results = [i for i in self.instruments.values() if keyword in i.name.lower()]
        elif choice == "3":
            keyword = input("Enter brand keyword: ").strip().lower()
            results = [i for i in self.instruments.values() if keyword in i.brand.lower()]
        elif choice == "4":
            category = input("Enter category: ").strip().title()
            results = [i for i in self.instruments.values() if i.category == category]
        else:
            print("Invalid option!")
            return

        if results:
            print(f"\nFound {len(results)} result(s):")
            print("=" * 60)
            for instrument in results:
                print(instrument)
                print("-" * 60)
        else:
            print("No instruments found matching your search.")

    def update_instrument(self):
        """Update an existing instrument's details."""
        print("\n--- Update Instrument ---")
        instrument_id = input("Enter Instrument ID to update: ").strip()
        instrument = self.instruments.get(instrument_id)

        if not instrument:
            print(f"Error: Instrument with ID '{instrument_id}' not found!")
            return

        print(f"Current details:\n{instrument}")
        print("\nEnter new values (press Enter to keep current value):")

        name = input(f"Name [{instrument.name}]: ").strip()
        if name:
            instrument.name = name

        brand = input(f"Brand [{instrument.brand}]: ").strip()
        if brand:
            instrument.brand = brand

        price_input = input(f"Price [{instrument.price}]: ").strip()
        if price_input:
            try:
                new_price = float(price_input)
                if new_price >= 0:
                    instrument.price = new_price
                else:
                    print("Price cannot be negative. Kept old value.")
            except ValueError:
                print("Invalid price. Kept old value.")

        quantity_input = input(f"Quantity [{instrument.quantity}]: ").strip()
        if quantity_input:
            try:
                new_quantity = int(quantity_input)
                if new_quantity >= 0:
                    instrument.quantity = new_quantity
                else:
                    print("Quantity cannot be negative. Kept old value.")
            except ValueError:
                print("Invalid quantity. Kept old value.")

        condition = input(f"Condition [{instrument.condition}]: ").strip().title()
        if condition:
            instrument.condition = condition

        self.save_data()
        print(f"\nSuccess: Instrument '{instrument_id}' updated!")

    def delete_instrument(self):
        """Delete an instrument from the inventory."""
        print("\n--- Delete Instrument ---")
        instrument_id = input("Enter Instrument ID to delete: ").strip()
        instrument = self.instruments.get(instrument_id)

        if not instrument:
            print(f"Error: Instrument with ID '{instrument_id}' not found!")
            return

        print(f"\nInstrument to delete:\n{instrument}")
        confirm = input("\nAre you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            del self.instruments[instrument_id]
            self.save_data()
            print(f"Success: Instrument '{instrument_id}' deleted!")
        else:
            print("Deletion cancelled.")

    # ---- Reports ----

    def category_report(self):
        """Display a summary report grouped by category."""
        print("\n--- Inventory Report by Category ---")
        if not self.instruments:
            print("No instruments in inventory.")
            return

        categories = {}
        for instrument in self.instruments.values():
            cat = instrument.category
            if cat not in categories:
                categories[cat] = {"count": 0, "units": 0, "value": 0.0}
            categories[cat]["count"] += 1
            categories[cat]["units"] += instrument.quantity
            categories[cat]["value"] += instrument.price * instrument.quantity

        print(f"{'Category':<15} {'Types':<8} {'Units':<8} {'Total Value':<15}")
        print("=" * 46)
        for cat, data in sorted(categories.items()):
            print(f"{cat:<15} {data['count']:<8} {data['units']:<8} ${data['value']:<14.2f}")

    def low_stock_alert(self, threshold=5):
        """Display instruments with stock below a threshold."""
        print(f"\n--- Low Stock Alert (below {threshold} units) ---")
        low_stock = [i for i in self.instruments.values() if i.quantity < threshold]

        if low_stock:
            for instrument in low_stock:
                print(instrument)
                print("-" * 60)
            print(f"Total low-stock items: {len(low_stock)}")
        else:
            print("All instruments are sufficiently stocked!")

    # ---- Data Persistence ----

    def save_data(self):
        """Save inventory data to a JSON file."""
        data = {iid: inst.to_dict() for iid, inst in self.instruments.items()}
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        """Load inventory data from a JSON file."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                self.instruments = {iid: Instrument.from_dict(d) for iid, d in data.items()}
            except (json.JSONDecodeError, KeyError):
                print("Warning: Could not load saved data. Starting with empty inventory.")
                self.instruments = {}
        else:
            self.instruments = {}

    # ---- Main Menu ----

    def display_menu(self):
        """Display the main menu."""
        print("\n" + "=" * 50)
        print("  MUSICAL INSTRUMENT INVENTORY SYSTEM")
        print("=" * 50)
        print("  1. Add Instrument")
        print("  2. View All Instruments")
        print("  3. Search Instrument")
        print("  4. Update Instrument")
        print("  5. Delete Instrument")
        print("  6. Category Report")
        print("  7. Low Stock Alert")
        print("  8. Exit")
        print("=" * 50)

    def run(self):
        """Run the inventory system main loop."""
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-8): ").strip()

            if choice == "1":
                self.add_instrument()
            elif choice == "2":
                self.view_all_instruments()
            elif choice == "3":
                self.search_instrument()
            elif choice == "4":
                self.update_instrument()
            elif choice == "5":
                self.delete_instrument()
            elif choice == "6":
                self.category_report()
            elif choice == "7":
                try:
                    threshold = int(input("Enter low stock threshold (default 5): ").strip() or "5")
                except ValueError:
                    threshold = 5
                self.low_stock_alert(threshold)
            elif choice == "8":
                self.save_data()
                print("\nThank you for using the Musical Instrument Inventory System!")
                break
            else:
                print("Invalid choice! Please enter a number between 1 and 8.")


# ---- Entry Point ----
if __name__ == "__main__":
    system = InventorySystem()
    system.run()

