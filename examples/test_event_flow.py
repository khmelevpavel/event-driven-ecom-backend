"""
Example script to test the event-driven flow of the e-commerce backend.

This script demonstrates:
1. Creating a product
2. Creating an order (which triggers payment processing and inventory update)
3. Viewing events and notifications

Make sure all services are running before executing this script.
"""

import requests
import time
import json

# Service URLs
PRODUCTS_URL = "http://localhost:8001"
ORDERS_URL = "http://localhost:8002"
PAYMENTS_URL = "http://localhost:8003"
EVENTS_URL = "http://localhost:8004"


def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    print(f"{'='*60}\n")


def main():
    print("🚀 Starting Event-Driven E-commerce Backend Test\n")
    
    # Step 1: Create a product
    print("Step 1: Creating a product...")
    product_data = {
        "name": "Laptop",
        "description": "High-performance laptop",
        "price": 999.99,
        "stock": 100,
        "category": "Electronics"
    }
    product_response = requests.post(
        f"{PRODUCTS_URL}/api/v1/products/",
        json=product_data
    )
    print_response("Product Created", product_response)
    
    if product_response.status_code != 201:
        print("❌ Failed to create product. Exiting.")
        return
    
    product = product_response.json()
    product_id = product["id"]
    
    # Wait a bit for event processing
    time.sleep(2)
    
    # Step 2: Create an order
    print("Step 2: Creating an order (this will trigger payment and inventory update)...")
    order_data = {
        "user_id": 123,
        "items": [
            {
                "product_id": product_id,
                "quantity": 2,
                "price": 999.99
            }
        ],
        "shipping_address": "123 Main St, City, Country"
    }
    order_response = requests.post(
        f"{ORDERS_URL}/api/v1/orders/",
        json=order_data
    )
    print_response("Order Created", order_response)
    
    if order_response.status_code != 201:
        print("❌ Failed to create order. Exiting.")
        return
    
    order = order_response.json()
    order_id = order["id"]
    
    # Wait for event processing (payment, inventory update, notifications)
    print("\n⏳ Waiting for event processing (payment, inventory update, notifications)...")
    time.sleep(5)
    
    # Step 3: Check payment status
    print("Step 3: Checking payment status...")
    payments_response = requests.get(
        f"{PAYMENTS_URL}/api/v1/payments/order/{order_id}"
    )
    print_response("Payments for Order", payments_response)
    
    # Step 4: Check updated product inventory
    print("Step 4: Checking updated product inventory...")
    product_check = requests.get(
        f"{PRODUCTS_URL}/api/v1/products/{product_id}"
    )
    print_response("Product Inventory", product_check)
    
    # Step 5: Check order status
    print("Step 5: Checking order status...")
    order_check = requests.get(
        f"{ORDERS_URL}/api/v1/orders/{order_id}"
    )
    print_response("Order Status", order_check)
    
    # Step 6: View event logs
    print("Step 6: Viewing event logs...")
    events_response = requests.get(
        f"{EVENTS_URL}/api/v1/events/logs?limit=10"
    )
    print_response("Event Logs", events_response)
    
    # Step 7: View notifications
    print("Step 7: Viewing notifications for user...")
    notifications_response = requests.get(
        f"{EVENTS_URL}/api/v1/events/notifications?user_id=123"
    )
    print_response("Notifications", notifications_response)
    
    print("\n✅ Event flow test completed!")
    print("\nEvent Flow Summary:")
    print("1. Product created → 'product.created' event published")
    print("2. Order created → 'order.created' event published")
    print("3. Payments service consumed 'order.created' → Payment processed → 'payment.processed' event published")
    print("4. Products service consumed 'order.created' → Inventory updated → 'inventory.updated' event published")
    print("5. Orders service consumed 'payment.processed' → Order status updated to 'confirmed'")
    print("6. Events service consumed all events → Logged events and created notifications")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("Make sure all services are running:")
        print("  docker-compose up -d")
        print("  or")
        print("  make up")
    except Exception as e:
        print(f"\n❌ Error: {e}")

