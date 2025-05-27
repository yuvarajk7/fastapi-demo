from tabulate import tabulate

from app.db.session import SessionLocal
from app.crud import product_repository, location_repository, inventory_repository


def view_all_products():
    """Display all products in a formatted table"""
    db = SessionLocal()
    try:
        products = product_repository.get_all(db)
        
        if not products:
            print("No products found in the database.")
            return
        
        # Format data for tabulate
        headers = ["ID", "Name", "SKU", "Price", "Description"]
        table_data = []
        for p in products:
            # Truncate description if it's too long
            desc = p.description[:50] + "..." if p.description and len(p.description) > 50 else p.description
            table_data.append([p.id, p.name, p.sku, f"${float(p.price):.2f}", desc])
        
        # Print table using tabulate function, not module
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\nTotal: {len(products)} products")
        
    except Exception as e:
        print(f"Error viewing products: {e}")
    finally:
        db.close()
    
    input("\nPress Enter to continue...")


def view_all_locations():
    """Display all locations with their inventory counts"""
    db = SessionLocal()
    try:
        locations_with_stock = location_repository.get_all_with_stock_counts(db)
        
        if not locations_with_stock:
            print("No locations found in the database.")
            return
        
        # Format data for tabulate
        headers = ["ID", "Name", "Address", "Capacity", "Current Stock", "Utilization %"]
        table_data = []
        for loc, stock in locations_with_stock:
            # Calculate utilization percentage
            utilization = (stock / loc.capacity * 100) if loc.capacity > 0 else 0
            
            # Truncate address if it's too long
            address = loc.address[:30] + "..." if loc.address and len(loc.address) > 30 else loc.address
            
            table_data.append([
                loc.id, 
                loc.name, 
                address, 
                loc.capacity, 
                stock, 
                f"{utilization:.1f}%"
            ])
        
        # Print table
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\nTotal: {len(locations_with_stock)} locations")
        
    except Exception as e:
        print(f"Error viewing locations: {e}")
    finally:
        db.close()
    
    input("\nPress Enter to continue...")


def view_inventory_by_product():
    """View inventory details for a specific product"""
    db = SessionLocal()
    try:
        # First get all products for selection
        products = product_repository.get_all(db)
        
        if not products:
            print("No products found in the database.")
            return
        
        # Show product selection menu
        print("\nSelect a product to view inventory:")
        for i, p in enumerate(products, 1):
            print(f"{i}. {p.name} (SKU: {p.sku})")
        
        # Get user selection
        while True:
            try:
                selection = int(input("\nEnter product number (0 to cancel): "))
                if selection == 0:
                    return
                if 1 <= selection <= len(products):
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get selected product
        product = products[selection - 1]
        
        # Get inventory for this product
        inventory = inventory_repository.get_by_product(db, product.id)
        
        if not inventory:
            print(f"\nNo inventory found for {product.name}.")
            return
        
        # Format data for tabulate
        headers = ["Location", "Quantity", "Reorder Point", "Status"]
        table_data = []
        total_quantity = 0
        
        for inv, loc in inventory:
            status = "LOW STOCK" if inv.quantity < inv.reorder_point else "OK"
            table_data.append([
                loc.name,
                inv.quantity,
                inv.reorder_point,
                status
            ])
            total_quantity += inv.quantity
        
        # Print product details and inventory
        print(f"\nProduct: {product.name} (SKU: {product.sku})")
        print(f"Price: ${float(product.price):.2f}")
        if product.description:
            print(f"Description: {product.description}")
        
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\nTotal quantity across all locations: {total_quantity}")
        
    except Exception as e:
        print(f"Error viewing inventory: {e}")
    finally:
        db.close()
    
    input("\nPress Enter to continue...")


def view_inventory_by_location():
    """View inventory details for a specific location"""
    db = SessionLocal()
    try:
        # First get all locations for selection
        locations = location_repository.get_all(db)
        
        if not locations:
            print("No locations found in the database.")
            return
        
        # Show location selection menu
        print("\nSelect a location to view inventory:")
        for i, loc in enumerate(locations, 1):
            print(f"{i}. {loc.name}")
        
        # Get user selection
        while True:
            try:
                selection = int(input("\nEnter location number (0 to cancel): "))
                if selection == 0:
                    return
                if 1 <= selection <= len(locations):
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get selected location
        location = locations[selection - 1]
        
        # Get inventory for this location
        inventory = inventory_repository.get_by_location(db, location.id)
        
        if not inventory:
            print(f"\nNo inventory found at {location.name}.")
            return
        
        # Get location with stock count for capacity info
        loc_with_stock = location_repository.get_with_stock_count(db, location.id)
        if loc_with_stock:
            loc, total_stock = loc_with_stock
            capacity = loc.capacity
            utilization = (total_stock / capacity * 100) if capacity > 0 else 0
        else:
            total_stock = 0
            capacity = location.capacity
            utilization = 0
        
        # Format data for tabulate
        headers = ["Product", "SKU", "Quantity", "Reorder Point", "Status"]
        table_data = []
        
        for inv, prod in inventory:
            status = "LOW STOCK" if inv.quantity < inv.reorder_point else "OK"
            table_data.append([
                prod.name,
                prod.sku,
                inv.quantity,
                inv.reorder_point,
                status
            ])
        
        # Print location details and inventory
        print(f"\nLocation: {location.name}")
        print(f"Address: {location.address}")
        print(f"Capacity: {capacity} units")
        print(f"Current stock: {total_stock} units ({utilization:.1f}% utilized)")
        
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\nTotal products at this location: {len(inventory)}")
        
    except Exception as e:
        print(f"Error viewing inventory: {e}")
    finally:
        db.close()
    
    input("\nPress Enter to continue...")


def view_low_stock_items():
    """View all inventory items with quantity below reorder point"""
    db = SessionLocal()
    try:
        low_stock = inventory_repository.get_low_stock_items(db)
        
        if not low_stock:
            print("No low stock items found.")
            return
        
        # Format data for tabulate
        headers = ["Product", "SKU", "Location", "Quantity", "Reorder Point", "Deficit"]
        table_data = []
        
        for inv, prod, loc in low_stock:
            deficit = inv.reorder_point - inv.quantity
            table_data.append([
                prod.name,
                prod.sku,
                loc.name,
                inv.quantity,
                inv.reorder_point,
                deficit
            ])
        
        # Sort by deficit (highest first)
        table_data.sort(key=lambda x: x[5], reverse=True)
        
        # Print table
        print("\nLOW STOCK ITEMS:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\nTotal: {len(low_stock)} items below reorder point")
        
    except Exception as e:
        print(f"Error viewing low stock items: {e}")
    finally:
        db.close()
    
    input("\nPress Enter to continue...")


def search_products():
    """Search products by name, description, or SKU"""
    db = SessionLocal()
    try:
        search_term = input("\nEnter search term: ")
        if not search_term:
            print("Search canceled.")
            return
            
        results = product_repository.search(db, search_term)
        
        if not results:
            print(f"No products found matching '{search_term}'.")
            return
        
        # Format data for tabulate
        headers = ["ID", "Name", "SKU", "Price", "Description"]
        table_data = []
        for p in results:
            # Truncate description if it's too long
            desc = p.description[:50] + "..." if p.description and len(p.description) > 50 else p.description
            table_data.append([p.id, p.name, p.sku, f"${float(p.price):.2f}", desc])
        
        # Print table
        print(f"\nSearch results for '{search_term}':")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\nTotal: {len(results)} products found")
        
    except Exception as e:
        print(f"Error searching products: {e}")
    finally:
        db.close()
    
    input("\nPress Enter to continue...")


def update_stock_menu():
    """Menu to update stock for a product at a location"""
    db = SessionLocal()
    try:
        # Get products
        products = product_repository.get_all(db)
        if not products:
            print("No products found in the database.")
            return
            
        # Get locations
        locations = location_repository.get_all(db)
        if not locations:
            print("No locations found in the database.")
            return
        
        # Select product
        print("\nSelect a product:")
        for i, p in enumerate(products, 1):
            print(f"{i}. {p.name} (SKU: {p.sku})")
        
        while True:
            try:
                product_selection = int(input("\nEnter product number (0 to cancel): "))
                if product_selection == 0:
                    return
                if 1 <= product_selection <= len(products):
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        product = products[product_selection - 1]
        
        # Select location
        print("\nSelect a location:")
        for i, loc in enumerate(locations, 1):
            print(f"{i}. {loc.name}")
        
        while True:
            try:
                location_selection = int(input("\nEnter location number (0 to cancel): "))
                if location_selection == 0:
                    return
                if 1 <= location_selection <= len(locations):
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        location = locations[location_selection - 1]
        
        # Check current stock
        inventory_item = inventory_repository.get(db, product.id, location.id)
        current_quantity = inventory_item.quantity if inventory_item else 0
        
        print(f"\nCurrent stock of {product.name} at {location.name}: {current_quantity}")
        
        # Get quantity change
        while True:
            try:
                print("\nEnter quantity change:")
                print("  - Positive number to add stock")
                print("  - Negative number to remove stock")
                print("  - Or enter 'set' followed by a number to set absolute value")
                
                input_value = input("> ")
                
                if input_value.lower().startswith('set '):
                    try:
                        # Set absolute value
                        new_quantity = int(input_value[4:])
                        if new_quantity < 0:
                            print("Quantity cannot be negative.")
                            continue
                            
                        # Set new quantity
                        inventory_repository.set_stock(
                            db=db,
                            product_id=product.id,
                            location_id=location.id,
                            quantity=new_quantity
                        )
                        print(f"Stock set to {new_quantity}.")
                        break
                    except ValueError:
                        print("Please enter a valid number after 'set'.")
                else:
                    try:
                        # Change quantity
                        quantity_change = int(input_value)
                        
                        # Check if removing more than available
                        if quantity_change < 0 and abs(quantity_change) > current_quantity:
                            print(f"Cannot remove {abs(quantity_change)} units. Only {current_quantity} available.")
                            continue
                            
                        # Update stock
                        result = inventory_repository.update_stock(
                            db=db,
                            product_id=product.id,
                            location_id=location.id,
                            quantity_change=quantity_change
                        )
                        
                        if result:
                            print(f"Stock updated successfully. New quantity: {result.quantity}")
                        else:
                            print("Stock update failed.")
                        
                        break
                    except ValueError:
                        print("Please enter a valid number or 'set' followed by a number.")
            except Exception as e:
                print(f"Error: {str(e)}")
        
    except Exception as e:
        print(f"Error updating stock: {e}")
    finally:
        db.close()
    
    input("\nPress Enter to continue...")