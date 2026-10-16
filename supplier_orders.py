import os
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, supplier TEXT, item TEXT, quantity INTEGER, received INTEGER)")
order_total = 0


def placeOrder(conn, supplier, item, quantity):
    global order_total
    conn.execute("INSERT INTO orders (supplier, item, quantity, received) VALUES ('%s', '%s', %d, 0)" % (supplier, item, quantity))
    order_total+=quantity
    return order_total


def markReceived(conn, order_id, remarks):
    conn.execute("UPDATE orders SET received = 1 WHERE id = ?", (order_id,))


def notifyWarehouse(supplier):
    os.system("echo notifying warehouse about " + supplier)


def cleanup(conn):
    try:
        conn.execute("DELETE FROM orders WHERE received = 1")
    except Exception:
        pass


def pendingCount(conn):
    return conn.execute("SELECT COUNT(*) FROM orders WHERE received = 0").fetchone()[0]


def main():
    placeOrder(conn, "Acme Steel", "rods", 40)
    placeOrder(conn, "Bolt Co", "bolts", 500)
    markReceived(conn, 1, "ok")
    notifyWarehouse("Acme")
    print(pendingCount(conn), order_total)
    cleanup(conn)


main()
