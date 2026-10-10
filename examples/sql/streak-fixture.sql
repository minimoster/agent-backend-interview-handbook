-- Original synthetic exercise fixture. MySQL 8.0/8.4 + InnoDB.
-- Run ONLY in a fresh, disposable exercise database. No DROP statements.
-- login_at is already normalized to the chosen business time zone.
CREATE TABLE study_users (id BIGINT PRIMARY KEY) ENGINE=InnoDB;
CREATE TABLE study_logins (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    login_at DATETIME(6) NOT NULL,
    INDEX idx_login_user_time(user_id, login_at)
) ENGINE=InnoDB;
INSERT INTO study_users(id) VALUES (1),(2),(3),(4),(5);
INSERT INTO study_logins(id,user_id,login_at) VALUES
(1,1,'2024-02-28 08:00:00'),(2,1,'2024-02-28 21:00:00'),
(3,1,'2024-02-29 08:00:00'),(4,1,'2024-03-01 08:00:00'),
(5,1,'2024-03-03 08:00:00'),
(6,2,'2024-03-01 08:00:00'),(7,2,'2024-03-03 08:00:00'),
(8,2,'2024-03-04 08:00:00'),
(9,4,'2024-12-31 08:00:00'),(10,4,'2025-01-01 08:00:00'),
(11,5,'2024-06-01 08:00:00');
WITH login_days AS (
    SELECT DISTINCT user_id, DATE(login_at) AS login_day FROM study_logins
), numbered AS (
    SELECT user_id, login_day,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_day) AS rn
    FROM login_days
), islands AS (
    SELECT user_id, DATE_SUB(login_day, INTERVAL rn DAY) AS island_key
    FROM numbered
), streaks AS (
    SELECT user_id, island_key, COUNT(*) AS streak_length
    FROM islands GROUP BY user_id, island_key
), longest AS (
    SELECT user_id, MAX(streak_length) AS longest_streak
    FROM streaks GROUP BY user_id
)
SELECT u.id, COALESCE(l.longest_streak,0) AS longest_streak
FROM study_users AS u LEFT JOIN longest AS l ON l.user_id=u.id
ORDER BY u.id;
-- Expected (id,longest_streak): (1,3),(2,2),(3,0),(4,2),(5,1)
