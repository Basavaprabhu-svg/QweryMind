CREATE TABLE IF NOT EXISTS EMPLOYEE (
    employee_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary REAL NOT NULL CHECK (salary >= 0),
    joining_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS CUSTOMER (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS SALES (
    sale_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    sale_date TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id)
);

CREATE INDEX IF NOT EXISTS idx_employee_department ON EMPLOYEE(department);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON SALES(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON SALES(sale_date);

INSERT OR IGNORE INTO EMPLOYEE VALUES
(1, 'Asha Rao', 'Engineering', 85000, '2022-03-14'),
(2, 'Ravi Kumar', 'Sales', 62000, '2021-07-01'),
(3, 'Meera Nair', 'Engineering', 92000, '2020-11-20'),
(4, 'Arjun Shetty', 'HR', 54000, '2023-02-06'),
(5, 'Priya Das', 'Marketing', 68000, '2022-09-12'),
(6, 'Kiran Patil', 'Sales', 71000, '2019-05-27'),
(7, 'Nisha Gowda', 'HR', 59000, '2021-12-03'),
(8, 'Vikram Singh', 'Engineering', 98000, '2018-08-16');

INSERT OR IGNORE INTO CUSTOMER VALUES
(1, 'Northstar Retail', 'North'),
(2, 'Bluewave Stores', 'South'),
(3, 'Cedar Market', 'West'),
(4, 'Urban Basket', 'South'),
(5, 'Greenfield Mart', 'East');

INSERT OR IGNORE INTO SALES VALUES
(1, 1, 12000, '2025-01-12'),
(2, 2, 8500, '2025-01-15'),
(3, 1, 6700, '2025-02-02'),
(4, 3, 15400, '2025-02-18'),
(5, 4, 9900, '2025-03-05'),
(6, 2, 11200, '2025-03-19'),
(7, 5, 4300, '2025-04-02'),
(8, 3, 7200, '2025-04-10'),
(9, 4, 13800, '2025-05-22'),
(10, 1, 5300, '2025-06-01');
