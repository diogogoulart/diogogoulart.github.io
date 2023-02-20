USE estetica;

#F
#1 
#EXPLAIN
SELECT c.name as client_name, a.date, s.name as service_name
FROM client c, appointment a, appointment_service ap, service s
WHERE a.client_id=c.client_id AND ap.apt_id=a.apt_id AND ap.service_id=s.service_id
AND (a.date BETWEEN '2020-10-01' AND CURDATE())
ORDER BY a.date
;
#to make this query more efficient, an index could be created for the date, so that SQL uses
#a sequential seek. And this way the query doesn't have to run all the observations of the table


#2
#Best customer = who spent the most money in the year 2022
EXPLAIN
SELECT c.name as client_name, SUM(a.apt_price) as total_spent
FROM client c, appointment a
WHERE a.client_id=c.client_id #AND (a.date BETWEEN '2019-01-01' AND CURDATE()) - if we want to set dates
GROUP BY c.client_id 
ORDER BY total_spent DESC
LIMIT 3
;
#since it is needed to group by the clients (to sum by them), the query needs to go through all of the
#observations to get the result

#3
#Average amount of appointments
#Query between '2020-01-01' and '2022-11-01'
#EXPLAIN
SELECT CONCAT(CAST(DATE_FORMAT(MIN(a.date), '%m/%Y') AS CHAR),' - ',CAST(DATE_FORMAT(MAX(a.date), '%m/%Y') AS CHAR)) AS PeriodOfSales, 
SUM(a.apt_price) as `TotalSales (euros)`,
ROUND(SUM(a.apt_price)/TIMESTAMPDIFF(YEAR,'2020-01-01','2022-11-01'),2) as `YearlyAverage (of the given period)`, 
ROUND(SUM(a.apt_price)/TIMESTAMPDIFF(MONTH,'2020-01-01','2022-11-01'),2) as `MonthlyAverage (ofthe given period)`
FROM appointment a
WHERE (a.date BETWEEN '2021-01-01' AND '2022-11-01')
GROUP BY if(a.date BETWEEN '2020-01-01' AND '2022-11-01', 0, 1)
;
#to make this query more efficient, an index could be created for the date, so that SQL uses
#a sequential seek. And this way the query doesn't have to run all the observations of the table


#Procedure to get the same query for any period that the user wants
DROP PROCEDURE IF EXISTS GetDates;
DELIMITER //
CREATE PROCEDURE GetDates(start_date date, end_date date)
BEGIN
    SELECT CONCAT(CAST(DATE_FORMAT(start_date, '%m/%Y') AS CHAR),' - ',CAST(DATE_FORMAT(end_date, '%m/%Y') AS CHAR)) AS PeriodOfSales, 
	SUM(a.apt_price) as `TotalSales (euros)`,
	ROUND(SUM(a.apt_price)/TIMESTAMPDIFF(YEAR,start_date,end_date),2) as `YearlyAverage (of the given period)`, 
	ROUND(SUM(a.apt_price)/TIMESTAMPDIFF(MONTH,start_date,end_date),2) as `MonthlyAverage (ofthe given period)`
	FROM appointment a
	WHERE (a.date BETWEEN start_date AND end_date)
	GROUP BY if(a.date BETWEEN start_date AND end_date, 0, 1);
END //
DELIMITER ;

CALL GetDates('2019-01-01', '2020-01-01');

#4
#EXPLAIN
SELECT con.country_name as Country, count(*) as Total_Appointments, SUM(a.apt_price) as TotalSalesEur
FROM appointment a, client c, country con
WHERE a.client_id=c.client_id AND con.country_id=c.nationality
GROUP BY con.country_id;
#since it is needed to group by the country, the query needs to go through all of the
#observations to get the result
#but efficiency is gained by grouping by the country id in the country table, because in that table
#the id's are unique, so it doesn't have to search for the distinct values 

#5
EXPLAIN
SELECT con.country_name as Country, s.name as Service, ROUND(AVG(r.rating),2) as AverageRating
FROM client c, country con, appointment a, appointment_service aps, service s, rating r
WHERE c.nationality=con.country_id AND  c.client_id=a.client_id AND a.apt_id=aps.apt_id AND 
aps.service_id = s.service_id AND aps.apt_ser_id=r.apt_ser_id
GROUP BY con.country_id, s.name;
#efficiency is gained by grouping by the country id in the country table, because in that table
#all of the steps to perform this query uses indexes, primary keys and foreign keys to get the rows needed
#showing efficiency