--CREATE DATABASE momentz_db;
--GO
USE momentz_db;
GO
-- Create Users table
CREATE TABLE Users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    bio NVARCHAR(MAX),
    picture_url VARCHAR(255),
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Create Posts table
CREATE TABLE Posts (
    post_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    content NVARCHAR(MAX) NOT NULL,
    image_url VARCHAR(255),
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) 
);

-- Create Likes table
CREATE TABLE Likes (
    like_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    post_id INT NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (post_id) REFERENCES Posts(post_id),
    CONSTRAINT UC_Like UNIQUE (user_id, post_id)
);

-- Create Comments table
CREATE TABLE Comments (
    comment_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    post_id INT NOT NULL,
    content NVARCHAR(MAX) NOT NULL,
    parent_comment_id INT,
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (post_id) REFERENCES Posts(post_id),
    FOREIGN KEY (parent_comment_id) REFERENCES Comments(comment_id) 
);

-- Create Followers table
CREATE TABLE Followers (
    follower_id INT IDENTITY(1,1) PRIMARY KEY,
    follower_user_id INT NOT NULL,
    following_user_id INT NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (follower_user_id) REFERENCES Users(user_id),
    FOREIGN KEY (following_user_id) REFERENCES Users(user_id),
    CONSTRAINT UC_Follower UNIQUE (follower_user_id, following_user_id)
);

-- Create Messages table
CREATE TABLE Messages (
    message_id INT IDENTITY(1,1) PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    content NVARCHAR(MAX) NOT NULL,
    sent_at DATETIME2 DEFAULT GETDATE(),
    is_read BIT DEFAULT 0,
    FOREIGN KEY (sender_id) REFERENCES Users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES Users(user_id) 
);

-- Create Notifications table
CREATE TABLE Notifications (
    notification_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    related_user_id INT NOT NULL,
    related_post_id INT,
    notification_type VARCHAR(20) NOT NULL,
    content NVARCHAR(255),
    created_at DATETIME2 DEFAULT GETDATE(),
    is_read BIT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ,
    FOREIGN KEY (related_user_id) REFERENCES Users(user_id) ,
    FOREIGN KEY (related_post_id) REFERENCES Posts(post_id)
);


INSERT INTO Users (username, email, password_hash, full_name, bio, picture_url)
VALUES 
('cyberfox', 'fox@example.com', 'hashed_pw1', 'Fox Cyber', 'Exploring the dark side of the net', NULL),
('bytegirl', 'byte@example.com', 'hashed_pw2', 'Byte Girl', 'Code & chaos.', NULL),
('rootedcat', 'cat@example.com', 'hashed_pw3', 'Root Cat', 'I purr and I pwn.', NULL),
('shellhunter', 'shell@example.com', 'hashed_pw4', 'Shell Hunter', 'Always on the hunt.', NULL),
('packetman', 'packet@example.com', 'hashed_pw5', 'Packet Man', 'Sniffing packets since birth.', NULL),
('ghostwriter', 'ghost@example.com', 'hashed_pw6', 'Ghost Writer', 'Silently watching.', NULL),
('ne0n', 'neon@example.com', 'hashed_pw7', 'Neon Light', 'Hacking in style.', NULL),
('bitstorm', 'storm@example.com', 'hashed_pw8', 'Bit Storm', 'Digital rebellion.', NULL),
('reconqueen', 'queen@example.com', 'hashed_pw9', 'Recon Queen', 'Map, probe, infiltrate.', NULL),
('mahshid', 'mahshid@example.com', 'hashed_pw10', 'Mahshid Shirani', 'Cybersecurity and justice!', NULL);


INSERT INTO Posts (user_id, content, image_url)
VALUES
(1, 'Just bypassed a WAF, life is good.', NULL),
(2, 'My custom Linux setup is complete ??', NULL),
(3, 'I found a 0-day in a router firmware.', NULL),
(4, 'Who else loves reverse shells?', NULL),
(5, 'Captured a beautiful packet dump.', NULL),
(6, 'Steganography is my aesthetic.', NULL),
(7, 'Booted into a custom OS from USB.', NULL),
(8, 'Script kiddies don’t read RFCs ??', NULL),
(9, 'Wrote a Python tool to scrape login portals.', NULL),
(10, 'Writing my paper on VPN privacy leaks!', NULL);


INSERT INTO Likes (user_id, post_id)
VALUES
(2, 1),
(3, 1),
(4, 2),
(5, 3),
(6, 4),
(1, 5),
(7, 6),
(8, 7),
(9, 8),
(10, 9);


INSERT INTO Comments (user_id, post_id, content, parent_comment_id)
VALUES
(2, 1, 'Awesome, share the technique?', NULL),
(3, 1, 'Legend!', NULL),
(4, 2, 'Screenshot or it didn’t happen.', NULL),
(5, 3, 'Can you disclose it responsibly?', NULL),
(6, 4, 'Yesss! My favorite topic.', NULL),
(7, 5, 'How big was the dump?', NULL),
(1, 6, 'Show us the steg result.', NULL),
(8, 7, 'Custom OS? Tell me more!', NULL),
(9, 8, 'RFCs are life.', NULL),
(10, 9, 'Respect for open source tools.', NULL);


INSERT INTO Followers (follower_user_id, following_user_id)
VALUES
(2, 1),
(3, 1),
(4, 2),
(5, 2),
(6, 3),
(1, 4),
(7, 5),
(8, 6),
(9, 7),
(10, 1);


INSERT INTO Messages (sender_id, receiver_id, content)
VALUES
(1, 2, 'Did you see my latest post?'),
(2, 3, 'How do you find CTF challenges?'),
(3, 4, 'Wanna collab on a reverse engineering project?'),
(4, 5, 'Check this vulnerability!'),
(5, 6, 'Packet traces are clean.'),
(6, 1, 'Let’s chat about opsec later.'),
(7, 8, 'That OS boot trick was amazing!'),
(8, 9, 'Wanna write a tool together?'),
(9, 10, 'Are you publishing that VPN paper soon?'),
(10, 1, 'Hey Mad, awesome work on that script!');

-------------------------------------------------------------------Functions
CREATE FUNCTION IsFollowing (
    @follower_user_id INT,
    @following_user_id INT
)
RETURNS BIT
AS
BEGIN
    DECLARE @result BIT = 0;

    IF EXISTS (
        SELECT 1 FROM Followers WHERE follower_user_id = @follower_user_id AND following_user_id = @following_user_id
    )
        SET @result = 1;

    RETURN @result;
END


---------------------------
CREATE FUNCTION GetUnreadNotifications (@user_id INT)
RETURNS TABLE
AS
RETURN (
    SELECT notification_id, related_user_id, related_post_id, notification_type, content, created_at
    FROM Notifications
    WHERE user_id = @user_id AND is_read = 0
);
-----------------------------

CREATE FUNCTION GetLastMessages (@user_id INT)
RETURNS TABLE
AS
RETURN (
    SELECT M1.*
    FROM Messages M1
    INNER JOIN (
        SELECT 
            CASE 
                WHEN sender_id = @user_id THEN receiver_id 
                ELSE sender_id 
            END AS other_user_id,
            MAX(sent_at) AS latest
        FROM Messages
        WHERE sender_id = @user_id OR receiver_id = @user_id
        GROUP BY CASE 
                    WHEN sender_id = @user_id THEN receiver_id 
                    ELSE sender_id 
                 END
    ) M2 ON (
        (M1.sender_id = @user_id AND M1.receiver_id = M2.other_user_id OR
         M1.sender_id = M2.other_user_id AND M1.receiver_id = @user_id)
        AND M1.sent_at = M2.latest
    )
);
-----------------------------------------Triggers

DROP TRIGGER trg_DeletePost_Cleanup;

CREATE TRIGGER trg_DeletePost_Cleanup
ON Posts
INSTEAD OF DELETE
AS
BEGIN
    DELETE FROM Comments WHERE post_id IN (SELECT post_id FROM DELETED);
    DELETE FROM Likes WHERE post_id IN (SELECT post_id FROM DELETED);
    DELETE FROM Notifications WHERE related_post_id IN (SELECT post_id FROM DELETED);
    DELETE FROM Posts WHERE post_id IN (SELECT post_id FROM DELETED);
END;



--------------------
CREATE TRIGGER trg_NotifyOnLike
ON Likes
AFTER INSERT
AS
BEGIN
    INSERT INTO Notifications (user_id, related_user_id, related_post_id, notification_type, content)
    SELECT 
        P.user_id,            -- Post owner
        L.user_id,            -- Who liked
        L.post_id,
        'like',
        CONCAT(U.username, ' liked your post.')
    FROM INSERTED L
    JOIN Posts P ON L.post_id = P.post_id
    JOIN Users U ON L.user_id = U.user_id
    WHERE L.user_id != P.user_id; -- avoid self-notification
END;

-------------------
CREATE TRIGGER trg_NotifyOnComment
ON Comments
AFTER INSERT
AS
BEGIN
    INSERT INTO Notifications (user_id, related_user_id, related_post_id, notification_type, content)
    SELECT 
        P.user_id, 
        C.user_id, 
        C.post_id,
        'comment',
        CONCAT(U.username, ' commented on your post.')
    FROM INSERTED C
    JOIN Posts P ON C.post_id = P.post_id
    JOIN Users U ON C.user_id = U.user_id
    WHERE C.user_id != P.user_id;
END;

------------------------
CREATE TRIGGER trg_AutoNotifyOnFollow
ON Followers
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO Notifications (user_id, related_user_id, related_post_id, notification_type, content, created_at, is_read)
    SELECT 
        i.following_user_id, 
        i.follower_user_id, 
        NULL, 
        'follow', 
        u.username + ' started following you.', 
        GETDATE(), 
        0
    FROM inserted i
    JOIN Users u ON u.user_id = i.follower_user_id;
END;
-----------------
CREATE TRIGGER trg_AutoNotifyOnMessage
ON Messages
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO Notifications (user_id, related_user_id, related_post_id, notification_type, content, created_at, is_read)
    SELECT 
        i.receiver_id, 
        i.sender_id, 
        NULL, 
        'message', 
        u.username + ' sent you a message.', 
        GETDATE(), 
        0
    FROM inserted i
    JOIN Users u ON u.user_id = i.sender_id;
END;

-------------------
CREATE TRIGGER trg_DeleteUser_Cleanup
ON Users
INSTEAD OF DELETE
AS
BEGIN
    DELETE FROM Notifications WHERE user_id IN (SELECT user_id FROM DELETED)
       OR related_user_id IN (SELECT user_id FROM DELETED);

    DELETE FROM Followers WHERE follower_user_id IN (SELECT user_id FROM DELETED)
       OR following_user_id IN (SELECT user_id FROM DELETED);

    DELETE FROM Messages WHERE sender_id IN (SELECT user_id FROM DELETED)
       OR receiver_id IN (SELECT user_id FROM DELETED);

    DELETE FROM Comments WHERE user_id IN (SELECT user_id FROM DELETED);

    DELETE FROM Likes WHERE user_id IN (SELECT user_id FROM DELETED);

    DELETE FROM Posts WHERE user_id IN (SELECT user_id FROM DELETED);

    DELETE FROM Users WHERE user_id IN (SELECT user_id FROM DELETED);
END;


---------------------------------------------------Views
CREATE VIEW UserProfileView AS
SELECT 
    U.user_id,
    U.username,
    U.full_name,
    U.bio,
    U.picture_url,
    U.created_at,
    (SELECT COUNT(*) FROM Posts P WHERE P.user_id = U.user_id) AS post_count,
    (SELECT COUNT(*) FROM Followers F WHERE F.following_user_id = U.user_id) AS followers_count,
    (SELECT COUNT(*) FROM Followers F WHERE F.follower_user_id = U.user_id) AS following_count
FROM Users U;


----------------------------

CREATE VIEW UserFeedView AS
SELECT
    F.follower_user_id AS viewer_user_id,
    P.post_id,
    P.user_id AS author_id,
    U.username AS author_username,
    U.full_name AS author_full_name,
    P.content,
    P.image_url,
    P.created_at,
    (SELECT COUNT(*) FROM Likes L WHERE L.post_id = P.post_id) AS like_count,
    (SELECT COUNT(*) FROM Comments C WHERE C.post_id = P.post_id) AS comment_count
FROM Followers F
JOIN Posts P ON F.following_user_id = P.user_id
JOIN Users U ON U.user_id = P.user_id;


-----------------------
CREATE VIEW UserInboxView AS
SELECT 
    M.message_id,
    M.receiver_id AS user_id,
    M.sender_id,
    U.username AS sender_username,
    M.content,
    M.sent_at,
    M.is_read
FROM Messages M
JOIN Users U ON U.user_id = M.sender_id;

----------------------------
CREATE VIEW PostEngagementView AS
WITH DistinctLikes AS (
    SELECT DISTINCT post_id, CAST(username AS NVARCHAR(MAX)) AS username
    FROM Likes L
    JOIN Users U ON L.user_id = U.user_id
)
SELECT
    P.post_id,
    CAST(P.content AS NVARCHAR(MAX)) AS content,
    P.user_id AS author_id,
    CAST(U.username AS NVARCHAR(MAX)) AS author_username,
    P.created_at,
    COUNT(DISTINCT L.like_id) AS total_likes,
    COUNT(DISTINCT C.comment_id) AS total_comments,
    STRING_AGG(DL.username, ', ') AS liked_by_users
FROM Posts P
JOIN Users U ON U.user_id = P.user_id
LEFT JOIN Likes L ON L.post_id = P.post_id
LEFT JOIN Comments C ON C.post_id = P.post_id
LEFT JOIN DistinctLikes DL ON DL.post_id = P.post_id
GROUP BY P.post_id, CAST(P.content AS NVARCHAR(MAX)), P.user_id, CAST(U.username AS NVARCHAR(MAX)), P.created_at;


---------------------------------------------------------Sample

-- Insert a new user
INSERT INTO Users (username, email, password_hash, full_name, bio, picture_url)
VALUES ('testuser', 'testuser@example.com', 'hashed_pw_test', 'Test User', 'Just another tester.', NULL);

-- Insert a new post by the new user
INSERT INTO Posts (user_id, content, image_url)
VALUES (11, 'Testing post for triggers and functions.', NULL);

-- Insert a like for the new post
INSERT INTO Likes (user_id, post_id)
VALUES (1, 11);

-- Insert a comment on the new post
INSERT INTO Comments (user_id, post_id, content, parent_comment_id)
VALUES (2, 11, 'Great post! Keep it up!', NULL);

-- Follow the new user
INSERT INTO Followers (follower_user_id, following_user_id)
VALUES (1, 11);

-- Send a message to the new user
INSERT INTO Messages (sender_id, receiver_id, content)
VALUES (1, 11, 'Nice post!');

-- Send a notification related to the new post
INSERT INTO Notifications (user_id, related_user_id, related_post_id, notification_type, content)
VALUES (11, 1, 11, 'like', 'User1 liked your post.');





-----------------------------------Testing functions

-- Should return 1 (true)
SELECT dbo.IsFollowing(2, 1) AS IsFollowing_2_to_1;

-- Should return 0 (false)
SELECT dbo.IsFollowing(1, 2) AS IsFollowing_1_to_2;

INSERT INTO Notifications (
    user_id,            -- The recipient of the notification
    related_user_id,    -- The user who triggered the action
    related_post_id,    -- The post involved (optional depending on type)
    notification_type,
    content
) VALUES (
    1,                  -- user_id (recipient)
    2,                  -- related_user_id (actor)
    1,                  -- related_post_id
    'like',             -- notification_type
    'bytegirl liked your post.'  -- content
);
SELECT * FROM dbo.GetUnreadNotifications(1);



-- Mark one notification as unread for testing (if none exist, insert first)
UPDATE Notifications SET is_read = 0 WHERE user_id = 1;

-- Get unread notifications for user_id = 1
SELECT * FROM dbo.GetUnreadNotifications(1);

-- Fetch latest message per conversation for user_id = 1
SELECT * FROM dbo.GetLastMessages(1);



------------------------- Testing triggers-----------------------------------------------------------
SELECT * FROM Notifications WHERE related_post_id = 11;


DELETE FROM Posts WHERE post_id = 11;

SELECT * FROM Likes WHERE post_id = 11;
SELECT * FROM Comments WHERE post_id = 11;
SELECT * FROM Notifications WHERE related_post_id = 11;





-- Like a post to trigger notification
INSERT INTO Likes (user_id, post_id) VALUES (3, 2);  -- User 3 likes post 2 (owned by user 2)

-- Check for notification (should notify user 2)
SELECT * FROM Notifications WHERE user_id = 2 AND related_post_id = 2 AND notification_type = 'like';

-- Comment on a post to trigger notification
INSERT INTO Comments (user_id, post_id, content) VALUES (4, 2, 'Nice setup!');

-- Check for notification (should notify user 2)
SELECT * FROM Notifications WHERE user_id = 2 AND related_post_id = 2 AND notification_type = 'comment';



-----------------------------------------Testing views----------------------------------------------------

SELECT * FROM UserProfileView WHERE username = 'cyberfox';
-- Should show posts by users followed by user_id = 2
SELECT * FROM UserFeedView WHERE viewer_user_id = 2;
SELECT * FROM UserInboxView WHERE user_id = 2;
SELECT * FROM PostEngagementView ORDER BY total_likes DESC;





----------------------Stored procedures-----------------
CREATE PROCEDURE sp_AddComment
    @userId INT,
    @postId INT,
    @content TEXT,
    @parentCommentId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- Validate 
    IF NOT EXISTS (SELECT 1 FROM Users WHERE user_id = @userId)
    BEGIN
        RAISERROR ('Invalid user ID.', 16, 1);
        RETURN;
    END;
    IF NOT EXISTS (SELECT 1 FROM Posts WHERE post_id = @postId)
    BEGIN
        RAISERROR ('Invalid post ID.', 16, 1);
        RETURN;
    END;
    IF @parentCommentId IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Comments WHERE comment_id = @parentCommentId)
    BEGIN
        RAISERROR ('Invalid parent comment ID.', 16, 1);
        RETURN;
    END;



    INSERT INTO Comments (user_id, post_id, content, parent_comment_id)
    VALUES (@userId, @postId, @content, @parentCommentId);

END;


EXEC sp_AddComment @userId = 1, @postId = 2, @content = 'Replying to your comment!', @parentCommentId = 1;
SELECT * FROM Comments WHERE post_id = 2 AND user_id = 1; 


---------------
CREATE PROCEDURE sp_FollowUser
    @followerUserId INT,
    @followingUserId INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Validate 
    IF NOT EXISTS (SELECT 1 FROM Users WHERE user_id = @followerUserId)
    BEGIN
        RAISERROR ('Invalid follower user ID.', 16, 1);
        RETURN;
    END;
    IF NOT EXISTS (SELECT 1 FROM Users WHERE user_id = @followingUserId)
    BEGIN
        RAISERROR ('Invalid following user ID.', 16, 1);
        RETURN;
    END;
    IF @followerUserId = @followingUserId
    BEGIN
        RAISERROR ('Users cannot follow themselves.', 16, 1);
        RETURN;
    END;
    IF EXISTS (SELECT 1 FROM Followers WHERE follower_user_id = @followerUserId AND following_user_id = @followingUserId)
    BEGIN
        RAISERROR ('User is already following this user.', 16, 1);
        RETURN;
    END;


    INSERT INTO Followers (follower_user_id, following_user_id)
    VALUES (@followerUserId, @followingUserId);

END;


EXEC sp_FollowUser @followerUserId = 1, @followingUserId = 8;
SELECT * FROM Followers WHERE follower_user_id = 1 AND following_user_id = 8;

---------------
CREATE PROCEDURE sp_LikePost
    @userId INT,
    @postId INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Validate 
    IF NOT EXISTS (SELECT 1 FROM Users WHERE user_id = @userId)
    BEGIN
        RAISERROR ('Invalid user ID.', 16, 1);
        RETURN;
    END;
    IF NOT EXISTS (SELECT 1 FROM Posts WHERE post_id = @postId)
    BEGIN
        RAISERROR ('Invalid post ID.', 16, 1);
        RETURN;
    END;
    IF EXISTS (SELECT 1 FROM Likes WHERE user_id = @userId AND post_id = @postId)
    BEGIN
        RAISERROR ('User has already liked this post.', 16, 1);
        RETURN;
    END;


    INSERT INTO Likes (user_id, post_id)
    VALUES (@userId, @postId);


END;


EXEC sp_LikePost @userId = 4, @postId = 10;
SELECT * FROM Likes WHERE user_id = 4 AND post_id = 10;

---------------
CREATE PROCEDURE sp_SendMessage
    @senderId INT,
    @receiverId INT,
    @content TEXT
AS
BEGIN
    SET NOCOUNT ON;

    -- Validate 
    IF NOT EXISTS (SELECT 1 FROM Users WHERE user_id = @senderId)
    BEGIN
        RAISERROR ('Invalid sender ID.', 16, 1);
        RETURN;
    END;
    IF NOT EXISTS (SELECT 1 FROM Users WHERE user_id = @receiverId)
    BEGIN
        RAISERROR ('Invalid receiver ID.', 16, 1);
        RETURN;
    END;
    IF @content IS NULL OR LEN(@content) = 0
    BEGIN
        RAISERROR ('Message content cannot be empty.', 16, 1);
        RETURN;
    END;


    INSERT INTO Messages (sender_id, receiver_id, content)
    VALUES (@senderId, @receiverId, @content);


END;


EXEC sp_SendMessage @senderId = 5, @receiverId = 2, @content = 'Hey, loved your Linux setup post!';
SELECT * FROM Messages WHERE sender_id = 5 AND receiver_id = 2;

---------------
CREATE PROCEDURE sp_MarkNotificationsAsRead
    @userId INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Validate 
    IF NOT EXISTS (SELECT 1 FROM Users WHERE user_id = @userId)
    BEGIN
        RAISERROR ('Invalid user ID.', 16, 1);
        RETURN;
    END;

    UPDATE Notifications
    SET is_read = 1
    WHERE user_id = @userId AND is_read = 0;

    -- Return the number of notifications marked as read
    SELECT @@ROWCOUNT AS NotificationsMarkedRead;
END;


EXEC sp_MarkNotificationsAsRead @userId = 1;
SELECT * FROM Notifications WHERE user_id = 1 AND is_read = 1; 
