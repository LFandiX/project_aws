DROP DATABASE car_rental;
CREATE DATABASE car_rental;

USE car_rental;

CREATE TABLE user (
    ID_user INT AUTO_INCREMENT PRIMARY KEY,
    name_user VARCHAR(100) NOT NULL,
    email_user VARCHAR(100) UNIQUE NOT NULL,
    password_user VARCHAR(50) NOT NULL,
    username_user VARCHAR(50) UNIQUE NOT NULL,
    role_user ENUM('member', 'admin') DEFAULT 'member'
);

CREATE TABLE car_model (
    ID_model INT AUTO_INCREMENT PRIMARY KEY,
    brand_car VARCHAR(50) NOT NULL,
    year_manufactured YEAR NOT NULL,
    model_car VARCHAR(50) NOT NULL,
    price_car DECIMAL(10, 2) NOT NULL,
    image_car VARCHAR(100) NOT NULL
);

CREATE TABLE car (
    ID_car INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT NOT NULL,
    license_plate VARCHAR(50) NOT NULL,
    availability ENUM('available', 'not available') DEFAULT 'available',
    FOREIGN KEY (model_id) REFERENCES car_model(ID_model)
);

CREATE TABLE rental (
	ID_rental INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    car_id INT NOT NULL,
    rental_date DATE NOT NULL,
    return_date DATE NOT NULL,
    approval_status ENUM('approved', 'rejected', 'pending') DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES user(ID_user),
    FOREIGN KEY (car_id) REFERENCES car(ID_car)
);

CREATE TABLE payment (
	ID_payment INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status ENUM('paid', 'unpaid') DEFAULT 'unpaid',
    FOREIGN KEY (rental_id) REFERENCES rental(ID_rental)
);

SHOW DATABASES;
SHOW TABLES;
DESCRIBE user;

INSERT INTO user (name_user, email_user, password_user, username_user, role_user) VALUES
('Budi Santoso', 'budi@gmail.com', 'budi123', 'budi_s', 'member'),
('Ani Wijaya', 'ani@gmail.com', 'ani123', 'ani_w', 'member'),
('Cahya Pratama', 'cahya@gmail.com', 'cahya123', 'cahya_p', 'admin'),
('Dewi Lestari', 'dewi@gmail.com', 'dewi123', 'dewi_l', 'member'),
('Eko Saputra', 'eko@gmail.com', 'eko123', 'eko_s', 'member');

INSERT INTO car_model (brand_car, year_manufactured, model_car, price_car, image_car) VALUES
('Toyota', 2020, 'Avanza', 25000.00, 'toyota.jpg'),
('Honda', 2021, 'Civic', 35000.00, 'honda.jpg'),
('Suzuki', 2019, 'Ertiga', 1700.00, 'suzuki.jpg'),
('Mitsubishi', 2022, 'Xpander', 30000.00, 'mitsubishi.jpg'),
('Nissan', 2018, 'Livina', 400.00, 'nissan.jpg');

INSERT INTO car (model_id, license_plate, availability) VALUES
(1, 'B 1234 ABC', 'available'),
(2, 'B 5678 DEF', 'not available'),
(3, 'B 9101 GHI', 'available'),
(4, 'B 1213 JKL', 'available'),
(5, 'B 1415 MNO', 'not available');

INSERT INTO rental (user_id, car_id, rental_date, return_date, approval_status) VALUES
(1, 1, '2024-03-01', '2024-03-05', 'approved'),
(2, 2, '2024-03-02', '2024-03-06', 'pending'),
(4, 4, '2024-03-04', '2024-03-08', 'rejected'),
(5, 5, '2024-03-05', '2024-03-09', 'approved'),
(1, 2, '2024-03-06', '2024-03-10', 'pending'),
(2, 3, '2024-03-07', '2024-03-11', 'approved'),
(4, 5, '2024-03-09', '2024-03-13', 'approved'),
(5, 1, '2024-03-10', '2024-03-14', 'pending');

INSERT INTO payment (rental_id, payment_date, amount, payment_method, payment_status) VALUES
(1, '2024-03-02', 1500000.00, 'Credit Card', 'paid'),
(2, '2024-03-03', 2000000.00, 'Bank Transfer', 'unpaid'),
(3, '2024-03-05', 2200000.00, 'Credit Card', 'unpaid'),
(4, '2024-03-06', 2500000.00, 'Cash', 'paid'),
(5, '2024-03-07', 1700000.00, 'E-Wallet', 'unpaid'),
(6, '2024-03-08', 2000000.00, 'Bank Transfer', 'paid'),
(7, '2024-03-10', 2300000.00, 'E-Wallet', 'paid'),
(8, '2024-03-11', 2100000.00, 'Cash', 'paid');


SELECT * FROM user;
SELECT * FROM rental;

SELECT ID_rental FROM rental 
        ORDER BY ID_rental DESC 
        LIMIT 1;

SELECT COUNT(*) FROM user WHERE username_user = 'devlinm';