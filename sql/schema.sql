
CREATE DATABASE IF NOT EXISTS retention_db;

USE retention_db;

CREATE TABLE IF NOT EXISTS customers (
    customer_id     VARCHAR(20) PRIMARY KEY,
    country         VARCHAR(100),
    first_purchase  DATE,
    last_purchase   DATE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id  INT AUTO_INCREMENT PRIMARY KEY,
    invoice_no      VARCHAR(20),
    stock_code      VARCHAR(20),
    description     VARCHAR(255),
    quantity        INT,
    invoice_date    DATETIME,
    unit_price      DECIMAL(10,2),
    customer_id     VARCHAR(20),
    country         VARCHAR(100),
    line_total      Decimal(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX idx_invoice_stock (invoice_no, stock_code)
);

CREATE TABLE IF NOT EXISTS rfm_features (
    customer_id     VARCHAR(20) PRIMARY KEY,
    recency_days    INT,
    frequency       INT,
    monetary        DECIMAL(12,2),
    avg_days_between_orders DECIMAL(12, 2),
    avg_order_value DECIMAL(12,2),
    estimated_clv   DECIMAL(12,2),
    recency_ratio   DECIMAL(12, 4),
    is_churned      TINYINT(1),
    computed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS churn_predictions (
    customer_id       VARCHAR(20) PRIMARY KEY,
    churn_probability DECIMAL(5,4),
    model_version     VARCHAR(20),
    predicted_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS retention_actions (
    action_id       INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     VARCHAR(20),
    email_subject   VARCHAR(255),
    email_body      TEXT,
    suggested_offer VARCHAR(255),
    status          ENUM('draft','approved','sent') DEFAULT 'draft',
    generated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
