CREATE DATABASE if NOT EXISTS LibraryDB;
USE LibraryDB;

CREATE TABLE Book (
    ID CHAR(8) PRIMARY KEY,
    name VARCHAR(10) NOT NULL,
    author VARCHAR(10),
    price FLOAT,
    status INT DEFAULT 0,
    times INT DEFAULT 0
);

CREATE TABLE Reader (
    ID CHAR(8) PRIMARY KEY,
    name VARCHAR(10),
    age INT,
    address VARCHAR(20)
);

CREATE TABLE Borrow (
    book_ID CHAR(8),
    Reader_ID CHAR(8),
    Borrow_Date DATE,
    Return_Date DATE,
    PRIMARY KEY (book_ID, Reader_ID),
    FOREIGN KEY (book_ID) REFERENCES Book(ID),
    FOREIGN KEY (Reader_ID) REFERENCES Reader(ID)
);
