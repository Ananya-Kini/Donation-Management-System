CREATE DATABASE IF NOT EXISTS mini; 
USE mini;
CREATE TABLE Donor (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(15),
    address TEXT
);


CREATE TABLE FieldWorker (
    field_worker_id INT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(15),
    region VARCHAR(255)
);


CREATE TABLE Child (
    child_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    age INT,
    gender VARCHAR(10),
    education_status VARCHAR(255),
    field_worker_id INT,
    FOREIGN KEY (field_worker_id) REFERENCES FieldWorker(field_worker_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);


CREATE TABLE Inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255),
    quantity INT,
    `condition` VARCHAR(255),  -- Using backticks since `condition` is a reserved word
    field_worker_id INT,
    FOREIGN KEY (field_worker_id) REFERENCES FieldWorker(field_worker_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);


CREATE TABLE Sponsorship (
    sponsorship_id INT PRIMARY KEY,
    donor_id INT,
    child_id INT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50),
    FOREIGN KEY (donor_id) REFERENCES Donor(donor_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (child_id) REFERENCES Child(child_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);


CREATE TABLE ChildLogs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT,
    child_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger: to check if child name alr exists when fieldworker is creating a new child profile
DELIMITER //
CREATE TRIGGER after_child_insert
AFTER INSERT ON Child
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM Child WHERE name = NEW.name AND child_id != NEW.child_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: A child with this name already exists.';
    ELSE
        INSERT INTO ChildLogs (child_id, child_name)
        VALUES (NEW.child_id, NEW.name);
    END IF;
END //
DELIMITER ;

-- Function: to count number of children under the responsibility of a fieldworker
DELIMITER //
CREATE FUNCTION CountChildrenForFieldWorker(fieldworker_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total_children INT;
    SELECT COUNT(*) INTO total_children
    FROM Child
    WHERE field_worker_id = fieldworker_id;
    RETURN total_children;
END //
DELIMITER ;


