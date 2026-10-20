from pathlib import Path
import importlib.util
import numpy as np
import pandas as pd
BASE=Path(__file__).resolve().parents[1]
def load(key):
    s=importlib.util.spec_from_file_location(key,BASE/'src/pipeline.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def test_retail_signed_returns_anonymous_duplicates_case():
    m=load('retail')
    rows=[['1','a','Item',2,'2011-01-01',5,1,'UK'],['1','a','Item',2,'2011-01-01',5,1,'UK'],['C2','a','Item',-1,'2011-01-02',5,1,'UK'],['3','A','Other',1,'2011-01-03',4,None,'UK'],['C4','a','Item',1,'2011-01-04',5,1,'UK']]
    d,reject,q=m.clean_transactions(pd.DataFrame(rows,columns=['Invoice','StockCode','Description','Quantity','InvoiceDate','Price','Customer ID','Country']))
    assert q['duplicate_rows_removed']==1 and q['invalid_rows_excluded']==1
    assert len(d)==3 and d.LineRevenue.sum()==9 and d.StockCode.nunique()==2
    assert d.loc[d.CustomerID.eq('UNKNOWN'),'SalesRevenue'].sum()==4


def test_rfm_counts_invoices_not_lines_and_ties():
    m=load('retail');s=pd.DataFrame({'CustomerID':['1','1','1','2'],'InvoiceNo':['a','a','b','c'],'InvoiceDate':pd.to_datetime(['2011-01-01','2011-01-01','2011-02-01','2011-02-01']),'SalesRevenue':[2,3,5,10]})
    r=m.rfm_segmentation(s).set_index('CustomerID')
    assert r.loc['1','Frequency']==2 and r.loc['1','Monetary']==10
    assert r.loc['1','RScore']==r.loc['2','RScore']


def test_cohort_observed_zero_and_future_absent():
    m=load('retail');s=pd.DataFrame({'CustomerID':['1','1','2'],'Month':['2011-01','2011-03','2011-03'],'InvoiceDate':pd.to_datetime(['2011-01-01','2011-03-05','2011-03-10'])})
    r=m.cohorts(s)
    assert r.loc[(r.CohortMonth=='2011-01')&(r.MonthIndex==1),'Retention'].iloc[0]==0
    assert len(r.loc[r.CohortMonth=='2011-03'])==1
    assert r.PartialActivityMonth.sum()==2
