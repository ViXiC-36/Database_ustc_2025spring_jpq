USE librarydb
-- 3. procedure
DELIMITER //

DROP PROCEDURE IF EXISTS update_book_id//
CREATE PROCEDURE update_book_id(IN old_id CHAR(8), IN new_id CHAR(8))
BEGIN
    -- old id cannot be super id
    IF LEFT(old_id, 2) = '00' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '不允许修改超级ID';
    END IF;
    -- new id cannot be super id
    IF LEFT(new_id, 2) = '00' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = '不允许将普通ID修改为超级ID';
    END IF;

    -- update if legal
    UPDATE Book SET ID = new_id WHERE ID = old_id;
END//
DELIMITER ;
# call update_book_id ('00b00001', '23');

-- 4. trigger
DELIMITER //

DROP TRIGGER IF EXISTS borrow_trigger//
CREATE TRIGGER borrow_trigger
AFTER INSERT ON Borrow
FOR EACH ROW
BEGIN
    UPDATE Book
    SET status = 1, times = times + 1
    WHERE ID = NEW.book_ID;
END//
DELIMITER ;

DELIMITER //
DROP TRIGGER IF EXISTS return_trigger//
CREATE TRIGGER return_trigger
AFTER UPDATE ON Borrow
FOR EACH ROW
BEGIN
    IF OLD.Return_Date IS NULL AND NEW.Return_Date IS NOT NULL THEN
        UPDATE Book
        SET status = 0
        WHERE ID = NEW.book_ID;
    END IF;
END//
DELIMITER ;
-- insert into Borrow value('00b00002', 'r3', '2025-4-11', null);
update borrow set return_date = '2025-4-19' where book_id = '00b00002' and return_date is null;
select *from Book;
