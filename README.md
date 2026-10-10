# SkillDemandAnalysis
Deliver an enterprise-grade, interactive Business Intelligence dashboard focused on prescriptive skills-demand posting analytics.

## **Objective**

Analyze skill demand data to uncover key trendsin current industry demand, posting volume, average annualised salary over time.
Build a clean, modular, and reusable Python ETL pipeline for data preparation and ingestion.Prepare structured datasets for advance SQL analysis. And Power BI visualizations to support interactive insights.
________________________________________

## **Tools & Technologies**

1. VistudioStudio Code
2. PowerBI Desktop
3. Python
4. SQL
5. GitHub
________________________________________

### **Project Phases**
**Phase 1: Python Data Pipeline**
The pipeline separates data cleaning, transformation,feature engineering, data quality validation into individual stages and finally ingest into DB .
**Pipeline Flow:**

```text
Raw CSV 
↓ 
importData() 
↓ 
transformDT() 
↓ 
extrctqrtnData() ──→ Quarantine CSV 
↓ 
featureEngg() 
↓ 
qualityCheck() 
↓ 
save_data() ──→ Clean CSV 
↓ ingesttoDB() ──→ MySQL Database
```
________________________________________

 **Phase 2: SQL Analysis**
SQL queries to execute complex business logic using core relational database mechanics:
1.	Detect any Salary Gap
2.	Finding demand spike (where applicants_count was exceptionally high, while views_count stayed below that industry's average)                                                              
3.	Find average applicants_count for each employment_type when remote_type is 'Remote' versus 'Onsite'
4.	Calculate the percentage of times a posting was labelled 'Senior' as seniority but its 'experience_years_required' was actually 3 or fewer
________________________________________

**Phase 3:Power BI Visualization**

Single page, Interactive Business Intelligence report focused on prescriptive skills-demand analytics.
1. Card visuals to report key metrices -  Total Posting, Total Applicants, InDemand Skills etc.
2. Interactive Slicers - WorkType, Seniority Level, Region, Industry Sector, Job Status etc.
3. A time-series line chart of posting volume and average annualised salary over time, driven by posting_date
4. A “RemotePolicyAdoption” slider, to show “Projected Applicant Uplift” when slider moves from Onsite towards Remote/Hybrid
