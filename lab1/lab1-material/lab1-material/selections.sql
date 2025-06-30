USE librarydb;

# 1.  查询读者Rose的读者号和地址； 
SELECT ID, address 
FROM Reader
WHERE name = 'Rose';

# 2. 查询读者Rose所借阅读书（包括已还和未还图书）的图书名和借期；
SELECT Book.name, Borrow.Borrow_Date
FROM Book, Borrow, Reader
WHERE Book.ID = Borrow.book_ID
  AND Reader.ID = Borrow.Reader_ID
  AND Reader.name = 'Rose';

# 3.  查询未借阅图书的读者姓名；  
SELECT DISTINCT Reader.name
FROM Reader, Borrow
WHERE Reader.ID NOT IN (
    SELECT Reader_ID
    FROM Borrow
);

# 4. 查询 Ullman 所写的书的书名和单价；
SELECT name, price
FROM Book
WHERE author = 'Ullman';    

# 5. 查询读者“李林”借阅未还的图书的图书号和图书名；
SELECT Book.ID, Book.name
FROM Book, Borrow, Reader
WHERE Book.ID = Borrow.book_ID
  AND Reader.ID = Borrow.Reader_ID
  AND Reader.name = '李林'
  AND Borrow.Return_Date IS NULL;

# 6. 查询借阅图书数目超过 3 本的读者姓名
SELECT Reader.name
FROM Reader, Borrow
WHERE Reader.ID = Borrow.Reader_ID
GROUP BY Reader.ID
HAVING COUNT(Borrow.book_ID) > 3;

# 7. 查询没有借阅读者“李林”所借的任何一本书的读者姓名和读者号
SELECT DISTINCT R.name, R.ID
FROM Reader R
WHERE R.ID NOT IN (
    SELECT DISTINCT B_other.Reader_ID   # 涉及这些书的所有记录
    FROM Borrow B_other, Borrow B_lilin
    WHERE B_lilin.Reader_ID = ( # by Lilin borrowed books
        SELECT ID FROM Reader WHERE name = '李林'
    ) # lilin的借书记录
      AND B_lilin.book_ID = B_other.book_ID # 涉及这些书的所有记录
);

# 8. 查询书名中包含“MySQL”的图书书名及图书号；
SELECT name, ID
FROM Book
WHERE name LIKE '%MySQL%';

# 9. 查询2021 年借阅图书数目排名前10名的读者号、姓名、年龄以及借阅图书数；
SELECT Reader.ID, Reader.name, Reader.age, COUNT(Borrow.book_ID) AS borrow_count
FROM Reader, Borrow
WHERE Reader.ID = Borrow.Reader_ID
  AND YEAR(Borrow.Borrow_Date) = 2021
GROUP BY Reader.ID
ORDER BY borrow_count DESC
LIMIT 10;

#10.  创建一个读者借书信息的视图，该视图包含读者号、姓名、所借图书号、图书名和借期；
DROP VIEW IF EXISTS Reader_Book_Info;
CREATE VIEW Reader_Book_Info AS
SELECT Reader.ID AS Reader_ID, Reader.name AS Reader_Name, Book.ID AS Book_ID, Book.name AS Book_Name, Borrow.Borrow_Date
FROM Reader, Book, Borrow
WHERE Reader.ID = Borrow.Reader_ID
  AND Book.ID = Borrow.book_ID;
# 并使用该视图查询最近一年所有读者的读者号以及所借阅的不同图书数；
SELECT Reader_ID, COUNT(DISTINCT Book_ID) AS book_count
FROM Reader_Book_Info
WHERE Borrow_Date >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
GROUP BY Reader_ID;