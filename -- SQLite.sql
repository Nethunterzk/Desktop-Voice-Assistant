-- SQLite
CREATE TABLE commands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    command VARCHAR(255) NOT NULL,
    response TEXT NOT NULL
);