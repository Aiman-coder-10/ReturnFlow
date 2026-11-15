CREATE DATABASE returnflow;

USE returnflow;
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(15)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE,
    delivery_date DATE,
    order_status VARCHAR(30),

    FOREIGN KEY (customer_id)
    REFERENCES customers(customer_id)
);

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);

CREATE TABLE order_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (order_id)
    REFERENCES orders(order_id),

    FOREIGN KEY (product_id)
    REFERENCES products(product_id),

    UNIQUE (order_id, product_id)
);

CREATE TABLE return_policies (
    policy_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) UNIQUE NOT NULL,
    return_days INT NOT NULL,
    return_allowed BOOLEAN NOT NULL,
    shipping_charge DECIMAL(10,2) DEFAULT 0,
    restocking_charge DECIMAL(10,2) DEFAULT 0
);

CREATE TABLE returns (
    return_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    reason_code VARCHAR(50) NOT NULL,
    refund_amount DECIMAL(10,2) NOT NULL,
    return_status VARCHAR(30) DEFAULT 'Requested',
    request_date DATE NOT NULL,

    FOREIGN KEY (order_id)
    REFERENCES orders(order_id),

    FOREIGN KEY (item_id)
    REFERENCES order_items(item_id),

    UNIQUE (item_id)
);

INSERT INTO customers
(customer_name, email, phone)
VALUES
('Rahul', 'rahul@gmail.com', '9876543210'),
('Priya', 'priya@gmail.com', '9876543211'),
('Arjun', 'arjun@gmail.com', '9876543212');

INSERT INTO orders
VALUES
(1001, 1, '2026-11-01', '2026-11-10', 'Delivered'),
(1002, 2, '2026-11-02', '2026-11-11', 'Delivered'),
(1003, 3, '2026-11-03', '2026-11-12', 'Delivered');

INSERT INTO products
(product_name, category, price)
VALUES
('Wireless Headphones', 'Electronics', 2000),
('Cotton Shirt', 'Clothing', 1000),
('Face Wash', 'Personal Care', 300),
('Mixer Grinder', 'Home Appliances', 3000);

INSERT INTO order_items
(order_id, product_id, quantity, unit_price)
VALUES
(1001, 1, 1, 2000),
(1001, 2, 2, 1000),
(1002, 3, 1, 300),
(1003, 4, 1, 3000);

INSERT INTO return_policies
(category, return_days, return_allowed,
 shipping_charge, restocking_charge)
VALUES
('Electronics', 7, TRUE, 50, 100),
('Clothing', 15, TRUE, 0, 0),
('Personal Care', 0, FALSE, 0, 0),
('Home Appliances', 10, TRUE, 50, 100);

