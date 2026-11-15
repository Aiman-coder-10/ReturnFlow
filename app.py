from flask import Flask, render_template, request
from database import get_connection

app = Flask(__name__)


# Homepage
@app.route("/")
def home():
    return render_template("index.html")


# Search order
@app.route("/order", methods=["POST"])
def find_order():
    order_id = request.form["order_id"]

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            o.order_id,
            o.order_date,
            o.delivery_date,
            o.order_status,
            c.customer_name,
            oi.item_id,
            oi.quantity,
            oi.unit_price,
            p.product_name,
            p.category
        FROM orders o
        JOIN customers c
            ON o.customer_id = c.customer_id
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN products p
            ON oi.product_id = p.product_id
        WHERE o.order_id = %s
    """

    cursor.execute(query, (order_id,))
    items = cursor.fetchall()

    cursor.close()
    db.close()

    if not items:
        return "Order not found!"

    return render_template("order.html", items=items)


# Start Flask (keep this at the bottom!)
from datetime import date

def check_eligibility(delivery_date, policy):

    days_passed = (date.today() - delivery_date).days

    if days_passed < 0:
        return False, "Order not delivered"

    if not policy["return_allowed"]:
        return False, "Non-returnable category"

    if days_passed > policy["return_days"]:
        return False, "Return period expired"

    return True, "Eligible for return"

def get_policy(category):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM return_policies WHERE category = %s",
        (category,)
    )

    policy = cursor.fetchone()

    cursor.close()
    db.close()

    return policy
@app.route("/return/<int:item_id>")
def return_item(item_id):

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT oi.item_id, oi.order_id,
               p.product_name, p.category,
               o.delivery_date, o.order_status
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE oi.item_id = %s
    """, (item_id,))

    item = cursor.fetchone()

    cursor.close()
    db.close()

    if not item:
        return "Item not found!"

    if item["order_status"] != "Delivered":
        return "Order is not delivered!"

    policy = get_policy(item["category"])

    if not policy:
        return "Return policy not found!"

    eligible, message = check_eligibility(
        item["delivery_date"], policy
    )

    if not eligible:
        return message

    return render_template(
        "return_form.html",
        item=item
    )



   

def check_eligibility(delivery_date, policy):

    days_passed = (
        date.today() - delivery_date
    ).days

    if days_passed < 0:
        return False, "Order not delivered"

    if not policy["return_allowed"]:
        return False, "Non-returnable category"

    if days_passed > policy["return_days"]:
        return False, "Return period expired"

    return True, "Eligible for return"

def get_policy(category):

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM return_policies
        WHERE category = %s
        """,
        (category,)
    )

    policy = cursor.fetchone()

    cursor.close()
    db.close()

    return policy




@app.route("/submit_return", methods=["POST"])
def submit_return():

    item_id = request.form["item_id"]
    reason = request.form["reason_code"]

    allowed_reasons = [
        "DEFECTIVE",
        "WRONG_ITEM",
        "NOT_AS_DESCRIBED",
        "SIZE_ISSUE",
        "CHANGED_MIND"
    ]

    if reason not in allowed_reasons:
        return "Invalid return reason"

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    try:

        # Get item and order details

        cursor.execute("""
            SELECT
                oi.item_id,
                oi.order_id,
                oi.quantity,
                oi.unit_price,
                p.category,
                o.delivery_date,
                o.order_status

            FROM order_items oi

            JOIN products p
            ON oi.product_id = p.product_id

            JOIN orders o
            ON oi.order_id = o.order_id

            WHERE oi.item_id = %s
        """, (item_id,))

        item = cursor.fetchone()

        if not item:
            return "Item not found"

        if item["order_status"] != "Delivered":
            return "Order is not delivered"

        # Check for an existing return

        cursor.execute("""
            SELECT return_id
            FROM returns
            WHERE item_id = %s
        """, (item_id,))

        existing = cursor.fetchone()

        if existing:
            return "Return request already exists"

        # Retrieve return policy

        cursor.execute("""
            SELECT *
            FROM return_policies
            WHERE category = %s
        """, (item["category"],))

        policy = cursor.fetchone()

        if not policy:
            return "Return policy not found"

        # Check eligibility again

        eligible, message = check_eligibility(
            item["delivery_date"],
            policy
        )

        if not eligible:
            return message

        # Calculate refund

        subtotal = (
            item["unit_price"] * item["quantity"]
        )

        if reason in [
            "DEFECTIVE",
            "WRONG_ITEM",
            "NOT_AS_DESCRIBED"
        ]:

            shipping = 0
            restocking = 0

        else:

            shipping = policy["shipping_charge"]
            restocking = policy["restocking_charge"]

        refund = max(
            subtotal - shipping - restocking,
            0
        )

        # Save return request

        cursor.execute("""
            INSERT INTO returns
            (
                order_id,
                item_id,
                reason_code,
                refund_amount,
                return_status,
                request_date
            )

            VALUES (%s, %s, %s, %s, %s, CURDATE())

        """, (
            item["order_id"],
            item_id,
            reason,
            refund,
            "Requested"
        ))

        return_id = cursor.lastrowid

        db.commit()

        return f"""
        <h1>Return Request Submitted!</h1>
        <p>Return ID: {return_id}</p>
        <p>Reason: {reason}</p>
        <p>Refund Amount: ₹{refund}</p>
        <p>Status: Requested</p>
        <a href="/returns">Track Return</a>
        """

    except Exception as e:

        db.rollback()

        return f"Error processing return: {e}"

    finally:

        cursor.close()
        db.close()

@app.route("/returns")
def view_returns():

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM returns
        ORDER BY request_date DESC
    """)

    returns = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "returns.html",
        returns=returns
    )

@app.route("/update_status", methods=["POST"])
def update_status():

    return_id = request.form["return_id"]

    new_status = request.form["status"]

    transitions = {
        "Requested": ["Approved", "Rejected"],
        "Approved": ["Picked Up"],
        "Picked Up": ["Received"],
        "Received": ["Refunded"],
        "Rejected": [],
        "Refunded": []
    }

    allowed_statuses = [
        "Approved",
        "Rejected",
        "Picked Up",
        "Received",
        "Refunded"
    ]

    if new_status not in allowed_statuses:
        return "Invalid status"

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT return_status
        FROM returns
        WHERE return_id = %s
    """, (return_id,))

    record = cursor.fetchone()

    if not record:
        cursor.close()
        db.close()
        return "Return not found"

    current_status = record["return_status"]

    if new_status not in transitions[current_status]:

        cursor.close()
        db.close()

        return "Invalid status transition"

    cursor.execute("""
        UPDATE returns
        SET return_status = %s
        WHERE return_id = %s
    """, (new_status, return_id))

    db.commit()

    cursor.close()
    db.close()

    return "Return status updated successfully"


@app.route("/analytics")
def analytics():

    db = get_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            reason_code,
            COUNT(*) AS total_returns

        FROM returns

        GROUP BY reason_code

        ORDER BY total_returns DESC
    """)

    results = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "dashboard.html",
        results=results
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))

    app.run(
        host="0.0.0.0",
        port=port
    )