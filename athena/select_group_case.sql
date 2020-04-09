SELECT DISTINCT date,

SUM(countapartmentbuy) AS Sum_Buy,
SUM(countapartmentrent) AS Sum_Rent,
(SUM(countapartmentbuy) + SUM(countapartmentrent)) AS Total,

SUM (CASE WHEN districtName = 'Mitte' THEN countapartmentBuy ELSE 0 END) AS Mitte_Buy,
SUM (CASE WHEN districtName = 'Mitte' THEN countapartmentRent ELSE 0 END) AS Mitte_Rent,

SUM (CASE WHEN districtName = 'West' THEN countapartmentBuy ELSE 0 END) AS West_Buy,
SUM (CASE WHEN districtName = 'West' THEN countapartmentRent ELSE 0 END) AS West_Rent,

SUM (CASE WHEN districtName = 'Süd' THEN countapartmentBuy ELSE 0 END) AS Sued_Buy,
SUM (CASE WHEN districtName = 'Süd' THEN countapartmentRent ELSE 0 END) AS Sued_Rent,

SUM (CASE WHEN districtName = 'Ost' THEN countapartmentBuy ELSE 0 END) AS Ost_Buy,
SUM (CASE WHEN districtName = 'Ost' THEN countapartmentRent ELSE 0 END) AS Ost_Rent

FROM "immoscout24db"."immoscoutstats"
WHERE districtname NOT LIKE '%districtName%'
GROUP BY date
ORDER BY date;

-- Example Output:
-- "date","Sum_Buy","Sum_Rent","Total","Mitte_Buy","Mitte_Rent","West_Buy","West_Rent","Sued_Buy","Sued_Rent","Ost_Buy","Mitte_Rent"
-- "2020-03-26 08:47:58.000","446","731","1177","16","79","38","92","26","57","38","72"
-- "2020-03-27 17:54:24.000","455","726","1181","18","74","39","98","27","60","41","70"
-- "2020-03-28 08:32:39.000","458","721","1179","18","74","40","97","26","59","41","69"
-- "2020-03-29 08:41:33.000","456","732","1188","18","77","40","99","26","58","41","70"
