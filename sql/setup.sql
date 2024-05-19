CREATE TABLE books (
    id INT PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    price DECIMAL(5, 2),
    image_url VARCHAR(255)
);

CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    book_id INT,
    FOREIGN KEY (book_id) REFERENCES books(id)
);
