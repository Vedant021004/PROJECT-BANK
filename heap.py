import heapq
import datetime

 
user_heaps = {}   # Dictionary to store the heaps of then users with key = email

def clear_heap(email):
    """Resets the in-memory cache for a specific user."""
    global user_heaps
    user_heaps[email] = []



def push_batch(email, item_id, product_name, batch_no, quantity, expiry_date_str, unit_price=0.0):
    """
    Converts the expiry string into a date object and pushes it onto 
    the specific user's private Min-Heap.
    """
    global user_heaps
    if email not in user_heaps:
        user_heaps[email] = []
        
    expiry_date = datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
    
    price = float(unit_price) if unit_price is not None else 0.0
    heap_element = (expiry_date, item_id, product_name, batch_no, quantity, price)
    
    heapq.heappush(user_heaps[email], heap_element)



def get_nearest_expiry(email, product_name):
    """
    Searches the logged-in user's private heap to find their absolute oldest 
    batch matching the requested product name.
    """
    global user_heaps
    if email not in user_heaps or not user_heaps[email]:
        return None
    matching_batches = []
    
    for element in user_heaps[email]:
        if element[2].lower() == product_name.lower():
            matching_batches.append(element)

    if not matching_batches:
        return None
    return min(matching_batches, key=lambda x: x[0])


def remove_batch_from_heap(email, batch_no, product_name):
    """Safely removes a batch from the user's in-memory Min-Heap without database reconnection."""
    global user_heaps
    if email in user_heaps and user_heaps[email]:
        user_heaps[email] = [
            b for b in user_heaps[email]
            if not (b[3] == batch_no and b[2].lower() == product_name.lower())
        ]
        heapq.heapify(user_heaps[email])


def update_batch_quantity_in_heap(email, batch_no, product_name, new_quantity):
    """Updates the remaining quantity of an in-memory batch and restores heap invariant."""
    global user_heaps
    if email in user_heaps and user_heaps[email]:
        new_list = []
        for b in user_heaps[email]:
            if b[3] == batch_no and b[2].lower() == product_name.lower():
                price = b[5] if len(b) > 5 else 0.0
                new_list.append((b[0], b[1], b[2], b[3], new_quantity, price))
            else:
                new_list.append(b)
        user_heaps[email] = new_list
        heapq.heapify(user_heaps[email])



def load_from_db(email, db_path='database.db'):
    """
    Query SQLite on server startup, pull active items for this specific user,
    and build their unique memory Min-Heap structure.
    """
    import sqlite3
    clear_heap(email)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_name, batch_no, quantity, expiry_date, COALESCE(unit_price, 0.0) FROM inventory WHERE user_email=?", (email,))
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        push_batch(
            email=email,
            item_id=row[0],
            product_name=row[1],
            batch_no=row[2],
            quantity=row[3],
            expiry_date_str=row[4],
            unit_price=row[5] if len(row) > 5 else 0.0
        )
    print(f" Successfully cached {len(user_heaps.get(email, []))} batches into the Min-Heap for {email}.")