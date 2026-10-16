"""Purchase order tracker for a stores department.

Places orders with suppliers, marks deliveries as received, notifies the
warehouse and clears fulfilled orders out of the table.
"""

import sqlite3


def create_connection():
    """Open an in-memory database and create the orders table."""
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE orders ("
        "id INTEGER PRIMARY KEY, supplier TEXT, item TEXT, "
        "quantity INTEGER, received INTEGER, remarks TEXT)"
    )
    return connection


def total_quantity(connection):
    """Return the total quantity across every order on the books."""
    row = connection.execute(
        "SELECT COALESCE(SUM(quantity), 0) FROM orders"
    ).fetchone()
    return row[0]


def place_order(connection, supplier, item, quantity):
    """Record an order and return the running total quantity ordered."""
    connection.execute(
        "INSERT INTO orders (supplier, item, quantity, received) "
        "VALUES (?, ?, ?, 0)",
        (supplier, item, quantity),
    )
    return total_quantity(connection)


def mark_received(connection, order_id, remarks):
    """Mark an order as delivered and store the delivery remarks."""
    connection.execute(
        "UPDATE orders SET received = 1, remarks = ? WHERE id = ?",
        (remarks, order_id),
    )


def notify_warehouse(supplier):
    """Tell the warehouse that a delivery from this supplier is due."""
    print("notifying warehouse about " + supplier)


def cleanup(connection):
    """Delete fulfilled orders, reporting any database error."""
    try:
        connection.execute("DELETE FROM orders WHERE received = 1")
    except sqlite3.Error as error:
        print("cleanup failed:", error)


def pending_count(connection):
    """Return how many orders are still awaiting delivery."""
    row = connection.execute(
        "SELECT COUNT(*) FROM orders WHERE received = 0"
    ).fetchone()
    return row[0]


def main():
    """Run a short demonstration of the order tracker."""
    connection = create_connection()
    place_order(connection, "Acme Steel", "rods", 40)
    place_order(connection, "Bolt Co", "bolts", 500)
    mark_received(connection, 1, "ok")
    notify_warehouse("Acme")
    print(pending_count(connection), total_quantity(connection))
    cleanup(connection)


main()
