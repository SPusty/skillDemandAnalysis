-- Query 1: The “Silent Salary Gap” Detector
select avg_sal.job_title,avg_sal.seniority_level, avg_sal.avg_min_sal,
avg_sal.deg_posting,avg_sal.tot_posting,
mkt_avg.mkt_avg_sal
from
(select job_title, seniority_level,
round(avg(case when salary_period = 'Annual' then salary_min_gbp end),2) as avg_min_sal,
count(case when degree_required='Yes' then 1 end) as deg_posting,
count(degree_required) as tot_posting
from sqlbasics.uk_skills_demand_postings
group by job_title, seniority_level) avg_sal
join
(select seniority_level,
round(avg(case when salary_period = 'Annual' then salary_min_gbp end),2) as mkt_avg_sal
from sqlbasics.uk_skills_demand_postings
group by seniority_level) mkt_avg
on avg_sal.seniority_level = mkt_avg.seniority_level
where avg_sal.avg_min_sal<mkt_avg.mkt_avg_sal*85/100
and 100.0*avg_sal.deg_posting/avg_sal.tot_posting> 25;

-- Query 2: The “Demand Spike” Vulnerability Finder
select posting_data.posting_id,industry_data.industry_sector,posting_data.applicants_count,posting_data.views_count,
industry_data.ind_avg_appl,industry_data.ind_avg_vw
from
(select posting_id, applicants_count,views_count, industry_sector
from sqlbasics.uk_skills_demand_postings) posting_data
join
(select industry_sector,round(avg(applicants_count),2) as ind_avg_appl, 
round(avg(views_count),2) as ind_avg_vw
from sqlbasics.uk_skills_demand_postings group by industry_sector) industry_data
on posting_data.industry_sector=industry_data.industry_sector
where posting_data.applicants_count>(1.5*industry_data.ind_avg_appl)
and posting_data.views_count<industry_data.ind_avg_vw;

-- Query 3: Remote-Work Engagement Stress Test
SELECT
    employment_type,
    ROUND(AVG(CASE WHEN remote_type = 'Remote' THEN applicants_count END), 2) AS remote_avg,
    ROUND(AVG(CASE WHEN remote_type = 'Onsite' THEN applicants_count END), 2) AS onsite_avg
FROM sqlbasics.uk_skills_demand_postings
WHERE remote_type IN ('Remote', 'Onsite')
GROUP BY employment_type
HAVING
    AVG(CASE WHEN remote_type = 'Remote' THEN applicants_count END)
    -
    AVG(CASE WHEN remote_type = 'Onsite' THEN applicants_count END) > 5;

-- Query 4: The “False Seniority Alarm” Audit
SELECT industry_sector, COUNT(*) AS senior_labelled,       
SUM(CASE WHEN experience_years_required <= 3 THEN 1 ELSE 0 END) AS false_senior,       
ROUND(100.0 * SUM(CASE WHEN experience_years_required <= 3 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct 
FROM uk_skills_demand_postings 
WHERE seniority_level_raw = 'Senior' GROUP BY industry_sector;

