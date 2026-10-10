import numpy as np
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import URL
import os 
from dotenv import load_dotenv

#import implementation
def importData(filePath):
    try:
        df = pd.read_csv(filePath)
        print(f"Imported dataset successfully.\n")
        return df
    except ImportError as impErr:
        print(f"Error occured while importing:\n {impErr}")
        return None

#inspect implementation
def inspData(df):
    df.info()
    print(f"Data shape check:\n {df.shape}")
    print(f"Duplicate count:\n {df.duplicated().sum()}\n")
    print(f"Missing value check:\n{df.isnull().sum()}\n")
    print(f"Dataset statistics:\n{df.describe()}\n")
    print(f"Data sample at inspection:\n{df.head(5)}\n")
    print(f"Region value at inspection:\n{df['region'].unique()}\n"
          f"Company anme value at inspection:\n{df['company_name'].unique()}")

#remove duplicate implementation
def duplRem(df):
    if (df.duplicated().sum())>0:
        print(f"Duplicate count is {df.duplicated().sum()} \n and sample check:\n {df[df.duplicated(keep=False)].sort_values(by=df.columns.tolist())}\n")
        try:
            df_clean = df.drop_duplicates()
            print(f"Shape of clean data post duplicate removal: {df_clean.shape}\n")
            return df_clean
        except Exception as err:
            print(f"Error occured during duplicate removal:\n {err}")
            return df
    else:
        print("No duplicate found.\n")
        return df

#data transformation implementation
def transformDT(df_clean):
    #column name standardisation
    df_clean.columns = (df_clean.columns
                    .str.strip()
                    .str.lower()
                    .str.replace(r'[^a-z0-9]+','_',regex= True))
    print(f"Column names post standardisation:\n{df_clean.columns}\n")

    #remove [£,] from salary values
    df_clean['salary_min_gbp'] =(df_clean['salary_min_gbp'].str.strip()
                                .str.replace(r'[£,]','',regex=True))
    df_clean['salary_max_gbp'] =(df_clean['salary_max_gbp'].str.strip()
                                    .str.replace(r'[£,]','',regex=True))
    #convert numeric values to numeric column
    numericCol = ['applicants_count','salary_min_gbp','salary_max_gbp',]
    for col in numericCol:
        df_clean[col] = pd.to_numeric(df_clean[col],errors='coerce')

    #date columns
    dayfirst_PD = pd.to_datetime(df_clean['posting_date'].str.strip(),format='%d/%m/%Y',errors='coerce')
    dayfirst_CD = pd.to_datetime(df_clean['closing_date'].str.strip(),format='%d/%m/%Y',errors='coerce')
    monthfirst_PD = pd.to_datetime(df_clean['posting_date'].str.strip(),format='%m/%d/%Y',errors='coerce')
    monthfirst_CD = pd.to_datetime(df_clean['closing_date'].str.strip(),format='%m/%d/%Y',errors='coerce')

    posting_date = dayfirst_PD.copy()
    posting_date=posting_date.fillna(monthfirst_PD)

    closing_date = dayfirst_CD.copy()
    closing_date=closing_date.fillna(monthfirst_CD)

    df_clean['posting_date'] = posting_date.dt.normalize()
    df_clean['closing_date'] = closing_date.dt.normalize()


    #standardise categorical columns
    df_clean[['region','company_name','job_title','job_location_city','job_status','seniority_level','degree_required','salary_period','source_platform']] =(df_clean[['region','company_name','job_title','job_location_city','job_status','seniority_level','degree_required','salary_period','source_platform']].apply(lambda x:x.str.strip().str.title().str.replace(r'[^A-Za-z0-9-]', '', regex=True)))
    df_clean['job_status'] = df_clean['job_status'].replace({'Active' : 'Open'})
    df_clean['source_platform'] = df_clean['source_platform'].replace({'ReedCoUk' : 'Reed'})
    df_clean['job_location_city'] = df_clean['job_location_city'].replace({'GtrManchester' : 'GreaterManchester'})
    df_clean['remote_type'] = (df_clean['remote_type']
                                    .str.strip()                         
                                    .str.replace(r'[^A-Za-z0-9-]', '', regex=True)
                                    .str.lower()                          
                                    .replace({
                                        'wfh'          : 'Remote',
                                        'workfromhome' : 'Remote',
                                        'remote'       : 'Remote',
                                        'hybrid'       : 'Hybrid',
                                        'onsite'       : 'Onsite',
                                        'inoffice'     : 'Onsite',
                                        'officebased'  : 'Onsite',
                                        'on-site'      : 'Onsite',
                                        'office-based' : 'Onsite',
                                        'onsite'       : 'Onsite',
                                    })
                                    )
    df_clean['employment_type'] = (df_clean['employment_type']
                                   .str.strip()
                                   .str.lower()
                                   .replace({
                                    'full-time' : 'Full Time',
                                    'full time' : 'Full Time',
                                    'temporary' : 'Temporary',
                                    'part-time' : 'Part Time', 
                                    'internship': 'Internship',
                                    'contract'  : 'Contract', 
                                    'contractor': 'Contract',
                                    'ft'        : 'Full Time',
                                    'apprenticeship' : 'Apprenticeship',
                                    'pt'        : 'Part Time',
                                    'part time' : 'Part Time'})
                                )
    df_clean['industry_sector'] = (df_clean['industry_sector'].str.strip()
                                   .str.lower()
                                   .str.title()
                                   .replace({
                                            'It/Tech'       : 'IT & Technology',
                                            'It&Technology' : 'IT & Technology',
                                            'Technology'    : 'IT & Technology',
                                            'It'            : 'IT & Technology',
                                            'Energy'        : 'Energy & Utilities',
                                            'Utilities'     : 'Energy & Utilities',
                                            'Banking'       : 'Finance & Banking',
                                            'Finance'       : 'Finance & Banking',
                                            'Government'    : 'Public Sector',
                                            'Finance&Banking'       : 'Finance & Banking',
                                            })
                                    )
    
    #seniority recalculation
    print(f"seniority_level values at raw data: {df_clean['seniority_level'].unique()}")
    valid_exp = (df_clean['experience_years_required']>=0) & (df_clean['experience_years_required']<=40)
    expBin= [-np.inf,2,5,8,12,np.inf]
    expLabel =['Entry','Junior','Mid','Senior','Lead']
    df_clean['seniority_level_revised'] = None
    df_clean.loc[valid_exp,'seniority_level_revised']= pd.cut(df_clean.loc[valid_exp,'experience_years_required'],bins=expBin,labels=expLabel,right=False)
    print(f"seniority_level_revised values post recalculation: {df_clean['seniority_level_revised'].unique()}\n")
    print(f"experience_years_required{df_clean[df_clean['seniority_level_revised'].isna()]['experience_years_required'].unique()}")

    #clean data quality check - negative salary or experience
    txt_col = ['region','company_name','job_title','job_location_city','job_status','salary_period','degree_required','employment_type','industry_sector','company_size']
    for cols in txt_col:
        print(f"{cols} values after standardising:\n{df_clean[cols].unique()}\n")

    print(f"Numeric value after cleaning:\n {df_clean[['salary_max_gbp','salary_min_gbp','posting_date','closing_date','salary_period',]].head(5)}")
    
    print(f"Checking data shape: \n {df_clean.shape}\n")
    print(f"DataType value after cleaning: \n {df_clean.dtypes}\n")
    return df_clean

#export quarantine
def extrctqrtnData(df_clean, quartantinePath):
    #invalid data marking
    print(f"Clean dataset with {len(df_clean)} rows, before invalid data removal.")
    invalid_mask = (df_clean['applicants_count']<0)|(df_clean['salary_max_gbp']<df_clean['salary_min_gbp'])|(df_clean['closing_date']<df_clean['posting_date'])|(df_clean['experience_years_required']<0)|(df_clean['experience_years_required']>40)
   
    #export invalid data
    df_qrtn = df_clean[invalid_mask].copy()
    
    df_qrtn.to_csv(quartantinePath,index= False)
    print(f"Quarantine export is done, {len(df_qrtn)} rows exported. Shape of data {df_qrtn.shape}")

    #revised clean data
    df_clean = df_clean[~invalid_mask]
    print(f"Revised clean dataset with {len(df_clean)} rows. Shape of data {df_clean.shape}")

    print(f"seniority_level_revised in clean data: {df_clean['seniority_level_revised'].unique()}\n")

    return df_clean

#Feature engineering
def featureEngg(df_clean):
    #posting attarctiveness
    df_clean['posting_attractiveness_score'] = (100
                                                +(df_clean['remote_type']=='Remote')*15
                                                +(df_clean['remote_type']=='Hybrid')*8
                                                -(df_clean['degree_required']=='Yes')*20
                                                -(df_clean['experience_years_required']>8)*10).clip(0,100)
    #role salary volatility
    salary_stats = df_clean.groupby('job_title')['salary_min_gbp'].agg(mean ='mean', std ='std')
    salary_stats['cv'] = round((salary_stats['std']/salary_stats['mean'])*100,2)
    df_clean['role_salary_volatility_index'] = (df_clean['job_title'].map(salary_stats['cv']))
    print(f'Salary statistics: {salary_stats.head()}\n')
    
    print(f'Chceking data after feature engineering: {df_clean.head(5)}\n')
    print(f"Shape of final data {df_clean.shape}\n")
    return df_clean

def qualityCheck(df_clean):
    neg_sal_mask = (df_clean['salary_min_gbp']<0)|(df_clean['salary_max_gbp']<0)
    if neg_sal_mask.any():
        print(f"Invalid Salary for {neg_sal_mask.sum()} rows.\n recod details:\n {df_clean[neg_sal_mask]}\n")
    else:
        print(f"No negative salary records found.")

    invalid_exp_mask =(df_clean['experience_years_required']<0)|(df_clean['experience_years_required']>40)
    if invalid_exp_mask.any():
        print(f"Invalid edxperience record count: {invalid_exp_mask.sum()}\n record details: {df_clean[invalid_exp_mask]}\n")
    else:
        print(f"No invalid experience records found.")

    if (df_clean['applicants_count']<0).sum()>0:
        print(f"Count of negative record count:{(df_clean['applicants_count']<0).sum()}\n record details:{df_clean[df_clean['applicants_count']<0]}\n")
    else:
        print(f"No negative applicant count records found.Shape check {df_clean.shape}")

    return df_clean

def saveCleanData(df_clean, cleanDataPath):
    df_clean.to_csv(cleanDataPath,index = False)
    print(f"Clean dataset is saved with {len(df_clean)} rows. Shape of data {df_clean.shape}")

#push to SQL DB
def ingesttoDB(df_clean):
    env_path = Path(__file__).resolve().parent / ".env"

    print("Env file exists:", env_path.is_file())
    load_dotenv(env_path)

    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    connection_url = URL.create(
    "mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database=DB_NAME,
)

    engine = create_engine(connection_url)
    df_clean.to_sql("uk_skills_demand_postings", 
                    con = engine, 
                    if_exists = "replace",
                    index =False)

#main function
def main():
    #import
    rawdataPath = "skills_tracker_raw_dataset.csv"
    cleanDataPath = "skills_tracker_clean_dataset.csv"
    quartantinePath = "skills_tracker_qrtn_dataset.csv"

    df = importData(rawdataPath)

    #inspect
    if df is not None:
        inspData(df)
    else:
       print(f"Chcek the dataset:\n{df.shape}")

    #remove duplicate
    df_clean = duplRem(df)

    #transform data
    df_clean = transformDT(df_clean)

    #export quarantine
    df_clean = extrctqrtnData(df_clean,quartantinePath)

    #feature engineering
    df_clean = featureEngg(df_clean)

    #validate
    df_clean = qualityCheck(df_clean)

    #save data
    saveCleanData(df_clean, cleanDataPath)

    #ingest into DB
    ingesttoDB(df_clean)

#execute
main()