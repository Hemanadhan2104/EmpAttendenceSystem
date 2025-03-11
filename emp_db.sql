CREATE DATABASE employee_attendance;
USE employee_attendance;
select * from attendance;
select * from employees;
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    date DATE DEFAULT (CURDATE()),
    time TIME DEFAULT (CURTIME()),
    status ENUM('Present', 'Absent', 'Late'),
    location VARCHAR(255),
    ip_address VARCHAR(255),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
ALTER TABLE employees MODIFY password VARCHAR(255);
ALTER TABLE attendance ADD COLUMN department VARCHAR(255);


INSERT INTO employees (name, department, email, password) 
VALUES 
('Hemanath', 'HR', 'hemanath@gmail.com', 'password123');

