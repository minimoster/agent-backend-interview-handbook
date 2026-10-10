"""Original deterministic exercise checks; standard library only.

These checks run SQLite equivalents and a Python reference, NOT MySQL.
They do not validate InnoDB locks, deadlocks, query plans, or transaction recovery.
"""
from datetime import date
import json
import platform
import sqlite3

con = sqlite3.connect(":memory:")
con.executescript("""
CREATE TABLE study_users(id INTEGER PRIMARY KEY);
CREATE TABLE study_logins(id INTEGER PRIMARY KEY,user_id INTEGER,login_at TEXT);
INSERT INTO study_users VALUES(1),(2),(3),(4),(5);
INSERT INTO study_logins VALUES
(1,1,'2024-02-28 08:00:00'),(2,1,'2024-02-28 21:00:00'),
(3,1,'2024-02-29 08:00:00'),(4,1,'2024-03-01 08:00:00'),
(5,1,'2024-03-03 08:00:00'),(6,2,'2024-03-01 08:00:00'),
(7,2,'2024-03-03 08:00:00'),(8,2,'2024-03-04 08:00:00'),
(9,4,'2024-12-31 08:00:00'),(10,4,'2025-01-01 08:00:00'),
(11,5,'2024-06-01 08:00:00');
""")
checks = []
def check(name, actual, expected):
    assert actual == expected, (name, actual, expected)
    checks.append({"name": name, "passed": True})

streak_sql = """
WITH login_days AS (
 SELECT DISTINCT user_id,date(login_at) AS login_day FROM study_logins
), numbered AS (
 SELECT user_id,login_day,ROW_NUMBER() OVER(
  PARTITION BY user_id ORDER BY login_day) AS rn FROM login_days
), islands AS (
 SELECT user_id,date(login_day,'-' || rn || ' day') AS island_key FROM numbered
), streaks AS (
 SELECT user_id,island_key,COUNT(*) AS streak_length FROM islands
 GROUP BY user_id,island_key
), longest AS (
 SELECT user_id,MAX(streak_length) AS longest_streak FROM streaks GROUP BY user_id
)
SELECT u.id,COALESCE(l.longest_streak,0) FROM study_users u
LEFT JOIN longest l ON l.user_id=u.id ORDER BY u.id;
"""
expected = [(1,3),(2,2),(3,0),(4,2),(5,1)]
check("streak_sqlite_duplicate_leap_gap_year_empty_single",con.execute(streak_sql).fetchall(),expected)
reference = []
for (uid,) in con.execute("SELECT id FROM study_users ORDER BY id"):
    days = sorted({date.fromisoformat(x[0][:10]) for x in con.execute(
        "SELECT login_at FROM study_logins WHERE user_id=?", (uid,))})
    previous, current, longest = None, 0, 0
    for day in days:
        current = current + 1 if previous is not None and (day-previous).days == 1 else 1
        longest = max(longest,current)
        previous = day
    reference.append((uid,longest))
check("streak_independent_python_reference",reference,expected)
con.execute("DELETE FROM study_logins")
check("streak_all_empty",con.execute(streak_sql).fetchall(),[(n,0) for n in range(1,6)])

con.executescript("""
CREATE TABLE exam_scores(id INTEGER PRIMARY KEY,student_name TEXT,score INTEGER);
INSERT INTO exam_scores VALUES(1,'Learner A',95),(2,'Learner B',95),(3,'Learner C',88);
CREATE TABLE study_departments(id INTEGER PRIMARY KEY,name TEXT);
INSERT INTO study_departments VALUES(1,'Platform'),(2,'Empty');
CREATE TABLE study_employees(id INTEGER PRIMARY KEY,department_id INTEGER,salary INTEGER);
INSERT INTO study_employees VALUES(1,1,6000),(2,1,NULL);
CREATE TABLE study_orders(id INTEGER PRIMARY KEY,user_id INTEGER,paid_at TEXT,status TEXT,amount INTEGER);
INSERT INTO study_orders VALUES
(1,1,'2025-01-01 00:00:00','paid',600),
(2,1,'2025-12-31 23:59:59.999999','paid',500),
(3,1,'2026-01-01 00:00:00','paid',9000),
(4,2,'2025-06-01 00:00:00','paid',1000),
(5,2,'2025-06-02 00:00:00','cancelled',8000);
CREATE TABLE study_profiles(id INTEGER PRIMARY KEY,created_at TEXT,status TEXT,age INTEGER);
INSERT INTO study_profiles VALUES
(1,'2025-01-01 00:00:00','active',18),
(2,'2025-01-01 00:00:00','active',20),
(3,'2025-01-02 00:00:00','active',30),
(4,'2025-01-03 00:00:00','inactive',40),
(5,'2025-01-04 00:00:00','active',17);
""")
check("ranking_ties_and_unique_order",con.execute("""
 SELECT id,ROW_NUMBER() OVER(ORDER BY score DESC,id),
 RANK() OVER(ORDER BY score DESC),DENSE_RANK() OVER(ORDER BY score DESC)
 FROM exam_scores ORDER BY score DESC,id
""").fetchall(),[(1,1,1,1),(2,2,1,1),(3,3,3,2)])
check("department_empty_and_null_salary",con.execute("""
 SELECT d.id,COUNT(e.id),COUNT(e.salary),AVG(e.salary)
 FROM study_departments d LEFT JOIN study_employees e ON e.department_id=d.id
 GROUP BY d.id,d.name ORDER BY d.id
""").fetchall(),[(1,2,1,6000.0),(2,0,0,None)])
check("annual_half_open_total_threshold_and_status",con.execute("""
 SELECT u.id,COUNT(o.id),SUM(o.amount) FROM study_users u
 JOIN study_orders o ON o.user_id=u.id WHERE o.status='paid'
 AND o.paid_at>='2025-01-01 00:00:00' AND o.paid_at<'2026-01-01 00:00:00'
 GROUP BY u.id HAVING SUM(o.amount)>1000 ORDER BY SUM(o.amount) DESC,u.id
""").fetchall(),[(1,2,1100)])
first = con.execute("""SELECT id,created_at FROM study_profiles
 WHERE status='active' AND age>=18 ORDER BY created_at DESC,id DESC LIMIT 2""").fetchall()
check("stable_pagination_first",first,[(3,'2025-01-02 00:00:00'),(2,'2025-01-01 00:00:00')])
last_id,last_time = first[-1]
second = con.execute("""SELECT id,created_at FROM study_profiles
 WHERE status='active' AND age>=18 AND
 (created_at<? OR (created_at=? AND id<?))
 ORDER BY created_at DESC,id DESC LIMIT 2""",(last_time,last_time,last_id)).fetchall()
check("stable_pagination_second",second,[(1,'2025-01-01 00:00:00')])
con.execute("INSERT INTO study_employees VALUES(3,1,5000),(4,1,5000),(5,2,7000)")
check("second_distinct_salary_ties_and_missing_rank",con.execute("""
 WITH ranked_pay AS (
 SELECT id,department_id,salary,DENSE_RANK() OVER(
 PARTITION BY department_id ORDER BY salary DESC) AS pay_rank
 FROM study_employees WHERE salary IS NOT NULL)
 SELECT id,department_id,salary FROM ranked_pay WHERE pay_rank=2 ORDER BY department_id,id
""").fetchall(),[(3,1,5000),(4,1,5000)])
con.executescript("""
CREATE TABLE interview_users(id INTEGER PRIMARY KEY, username TEXT);
INSERT INTO interview_users VALUES(11,'Learner A'),(12,'Learner B'),(13,'Learner C'),(14,'No orders');
CREATE TABLE interview_orders(id INTEGER PRIMARY KEY,user_id INTEGER,paid_at TEXT,status INTEGER,amount INTEGER);
INSERT INTO interview_orders VALUES
(1,11,'2025-01-01 00:00:00',1,400),
(2,11,'2025-12-31 23:59:59.999999',1,600),
(3,12,'2025-03-01 00:00:00',1,1000),
(4,13,'2025-02-01 00:00:00',1,700),
(5,13,'2025-04-01 00:00:00',1,500),
(6,13,'2025-01-01 00:00:00',0,9000),
(7,13,'2026-01-01 00:00:00',1,9000);
""")
check("annual_full_six_outputs_ge_threshold_and_two_orders",con.execute("""
 SELECT u.id,u.username,COUNT(o.id),SUM(o.amount),MAX(o.amount),MIN(o.paid_at)
 FROM interview_users u INNER JOIN interview_orders o ON o.user_id=u.id
 WHERE o.status=1 AND o.paid_at>='2025-01-01 00:00:00'
 AND o.paid_at<'2026-01-01 00:00:00'
 GROUP BY u.id,u.username HAVING SUM(o.amount)>=1000 AND COUNT(o.id)>=2
 ORDER BY SUM(o.amount) DESC,u.id
""").fetchall(),[(13,'Learner C',2,1200,700,'2025-02-01 00:00:00'),
                 (11,'Learner A',2,1000,600,'2025-01-01 00:00:00')])
print(json.dumps({"python":platform.python_version(),"sqlite":sqlite3.sqlite_version,
 "scope":"SQLite equivalents and Python reference only; MySQL not executed",
 "checks":checks,"passed":len(checks)},ensure_ascii=False,indent=2))
