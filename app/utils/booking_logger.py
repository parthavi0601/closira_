import os
import csv
from datetime import datetime

BOOKINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "bookings.csv")

def log_booking(booking_details: dict) -> bool:
    """
    Logs booking details to a CSV file.
    Returns True if successfully logged, False otherwise.
    """
    if not booking_details:
        return False
        
    # We expect: name, phone, datetime, service
    # But we will gracefully handle missing ones or extra keys
    
    # Check if we have at least some booking data
    if "name" not in booking_details and "phone" not in booking_details:
        return False

    file_exists = os.path.isfile(BOOKINGS_FILE)
    
    fieldnames = ["Timestamp", "Name", "Phone", "Preferred Date & Time", "Service of Interest"]
    
    try:
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(BOOKINGS_FILE), exist_ok=True)
        
        with open(BOOKINGS_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
                
            row = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Name": booking_details.get("name", ""),
                "Phone": booking_details.get("phone", ""),
                "Preferred Date & Time": booking_details.get("datetime", ""),
                "Service of Interest": booking_details.get("service", "")
            }
            writer.writerow(row)
            
        return True
    except Exception as e:
        print(f"Error saving booking to CSV: {e}")
        return False
