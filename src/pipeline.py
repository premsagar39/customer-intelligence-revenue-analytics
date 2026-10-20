"""Reproducible Online Retail II analysis, retaining anonymous revenue and signed returns."""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

def clean_transactions(raw):
    """Remove exact source duplicates; retain valid sales and negative-quantity credits."""
    raw=raw.rename(columns={'Invoice':'InvoiceNo','Price':'UnitPrice','Customer ID':'CustomerID'})
    raw['LineID']=np.arange(1,len(raw)+1,dtype='int64')
    subset=['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country']
    duplicate=raw.duplicated(subset=subset)
    d=raw.loc[~duplicate].copy()
    for c in ['InvoiceNo','StockCode','Country']:
        d[c]=d[c].astype('string').str.strip()
    d['InvoiceDate']=pd.to_datetime(d['InvoiceDate'],errors='coerce')
    d['Quantity']=pd.to_numeric(d['Quantity'],errors='coerce')
    d['UnitPrice']=pd.to_numeric(d['UnitPrice'],errors='coerce')
    d['CustomerID']=pd.to_numeric(d['CustomerID'],errors='coerce').astype('Int64').astype('string').fillna('UNKNOWN')
    cancel=d['InvoiceNo'].str.upper().str.startswith('C',na=False)
    invalid=d['InvoiceDate'].isna()|d['Quantity'].isna()|d['UnitPrice'].isna()|(d['UnitPrice']<=0)|(d['Quantity']==0)|d['InvoiceNo'].isna()|d['StockCode'].isna()|(cancel&(d['Quantity']>0))
    rejects=d.loc[invalid].copy()
    d=d.loc[~invalid].copy()
    d['Country']=d['Country'].fillna('Unknown')
    d['LineType']=np.where(d['Quantity']>0,'Sale','Return')
    d['LineRevenue']=(d['Quantity']*d['UnitPrice']).round(6)
    d['SalesRevenue']=d['LineRevenue'].clip(lower=0)
    d['ReturnValue']=(-d['LineRevenue']).clip(lower=0)
    d['DateKey']=d['InvoiceDate'].dt.strftime('%Y-%m-%d')
    d['Month']=d['InvoiceDate'].dt.strftime('%Y-%m')
    quality={'raw_rows':len(raw),'duplicate_rows_removed':int(duplicate.sum()),'invalid_rows_excluded':len(rejects),'accepted_rows':len(d),'missing_customer_rows_retained':int(d['CustomerID'].eq('UNKNOWN').sum()),'missing_description_rows':int(d['Description'].isna().sum()),'positive_quantity_credit_notes_excluded':int((cancel&(pd.to_numeric(raw.loc[~duplicate,'Quantity'],errors='coerce')>0)).sum())}
    assert quality['raw_rows']==quality['duplicate_rows_removed']+quality['invalid_rows_excluded']+quality['accepted_rows']
    assert np.isclose(d['LineRevenue'].sum(),d['SalesRevenue'].sum()-d['ReturnValue'].sum())
    return d, rejects, quality

def rfm_segmentation(sales):
    """Use an explicit observation end and tie-preserving empirical quintile scores."""
    identified=sales.loc[sales['CustomerID'].ne('UNKNOWN')].copy()
    snapshot=sales['InvoiceDate'].max().normalize()+pd.Timedelta(days=1)
    rfm=identified.groupby('CustomerID').agg(LastPurchase=('InvoiceDate','max'),Frequency=('InvoiceNo','nunique'),Monetary=('SalesRevenue','sum')).reset_index()
    rfm['Recency']=(snapshot-rfm['LastPurchase'].dt.normalize()).dt.days
    for col in ['Recency','Frequency','Monetary']:
        score=np.ceil(rfm[col].rank(method='average',pct=True)*5).clip(1,5).astype(int)
        rfm[col[0]+'Score']=6-score if col=='Recency' else score
    r,f,m=rfm.RScore,rfm.FScore,rfm.MScore
    rfm['Segment']=np.select([(r>=4)&(f>=4)&(m>=4),(r>=3)&(f>=4),(r<=2)&(f>=3),(r>=4)&(f<=2),(r<=2)&(f<=2)],['Champions','Loyal','At risk','Recent low frequency','Hibernating'],default='Developing')
    rfm['SnapshotDate']=snapshot.strftime('%Y-%m-%d')
    return rfm

def cohorts(sales):
    """Return observed retention cells only; later unobserved periods stay absent."""
    d=sales.loc[sales.CustomerID.ne('UNKNOWN'),['CustomerID','Month']].drop_duplicates()
    first=d.groupby('CustomerID')['Month'].min().rename('CohortMonth')
    d=d.join(first,on='CustomerID')
    date=pd.to_datetime(d.Month+'-01'); start=pd.to_datetime(d.CohortMonth+'-01')
    d['MonthIndex']=(date.dt.year-start.dt.year)*12+date.dt.month-start.dt.month
    counts=d.groupby(['CohortMonth','MonthIndex']).CustomerID.nunique().rename('ActiveCustomers').reset_index()
    base=counts.loc[counts.MonthIndex.eq(0)].set_index('CohortMonth').ActiveCustomers
    last=pd.Period(sales.Month.max(),freq='M')
    grid=[]
    for cohort,n in base.items():
        for age in range(last.ordinal-pd.Period(cohort,freq='M').ordinal+1): grid.append((cohort,age,n))
    result=pd.DataFrame(grid,columns=['CohortMonth','MonthIndex','CohortSize']).merge(counts,how='left',on=['CohortMonth','MonthIndex'])
    result['ActiveCustomers']=result.ActiveCustomers.fillna(0).astype(int)
    result['Retention']=result.ActiveCustomers/result.CohortSize
    result['ActivityMonth']=[str(pd.Period(c,freq='M')+int(a)) for c,a in zip(result.CohortMonth,result.MonthIndex)]
    result['PartialActivityMonth']=result.ActivityMonth.eq(sales.Month.max()) & (sales.InvoiceDate.max().day < last.days_in_month)
    assert result.Retention.between(0,1).all()
    assert result.loc[result.MonthIndex.eq(0),'Retention'].eq(1).all()
    return result

def run(source,root=ROOT):
    """Read both workbook years and export the fact, dimensions, and analysis marts."""
    root=Path(root); processed=root/'data/processed'; exports=root/'data/exports'; reports=root/'reports'
    for p in [processed,exports,reports]:p.mkdir(parents=True,exist_ok=True)
    sheets=pd.read_excel(source,sheet_name=None,engine='openpyxl')
    raw=pd.concat(sheets.values(),ignore_index=True)
    d,rejects,quality=clean_transactions(raw)
    del raw,sheets
    sales=d.loc[d.LineType.eq('Sale')]
    rfm=rfm_segmentation(sales); retention=cohorts(sales)
    monthly=d.groupby('Month').agg(GrossRevenue=('SalesRevenue','sum'),Returns=('ReturnValue','sum'),NetRevenue=('LineRevenue','sum'),Lines=('LineID','size')).reset_index()
    monthly=monthly.merge(sales.groupby('Month').InvoiceNo.nunique().rename('Orders'),on='Month')
    monthly['AOV']=monthly.GrossRevenue/monthly.Orders
    monthly['MoMNetGrowth']=monthly.NetRevenue.pct_change()
    monthly['PartialMonth']=monthly.Month.eq(d.Month.max()) & (d.InvoiceDate.max().day<pd.Period(d.Month.max(),freq='M').days_in_month)
    country=d.groupby('Country').agg(NetRevenue=('LineRevenue','sum'),GrossRevenue=('SalesRevenue','sum'),Returns=('ReturnValue','sum')).sort_values('NetRevenue',ascending=False).reset_index()
    products=d.groupby('StockCode').agg(NetRevenue=('LineRevenue','sum'),GrossRevenue=('SalesRevenue','sum'),ReturnValue=('ReturnValue','sum'),NetQuantity=('Quantity','sum')).reset_index()
    descriptions=d.dropna(subset=['Description']).sort_values('InvoiceDate').drop_duplicates('StockCode',keep='last')[['StockCode','Description']]
    products=products.merge(descriptions,on='StockCode',how='left').sort_values('NetRevenue',ascending=False)
    segments=rfm.groupby('Segment').agg(Customers=('CustomerID','size'),GrossRevenue=('Monetary','sum'),MedianRecency=('Recency','median'),MeanFrequency=('Frequency','mean')).reset_index()
    customers=d[['CustomerID']].drop_duplicates().merge(rfm[['CustomerID','Segment','Recency','Frequency','Monetary','RScore','FScore','MScore','SnapshotDate']],on='CustomerID',how='left')
    customers['Segment']=customers.Segment.fillna('Return only')
    customers.loc[customers.CustomerID.eq('UNKNOWN'),'Segment']='Unidentified'
    for c in ['Recency','Frequency','RScore','FScore','MScore']:customers[c]=customers[c].astype('Int64')
    dates=pd.DataFrame({'DateKey':pd.date_range(d.InvoiceDate.min().normalize(),d.InvoiceDate.max().normalize())})
    dates['Year']=dates.DateKey.dt.year; dates['Month']=dates.DateKey.dt.strftime('%Y-%m'); dates['MonthNumber']=dates.DateKey.dt.month; dates['DateKey']=dates.DateKey.dt.strftime('%Y-%m-%d')
    facts=d[['LineID','InvoiceNo','StockCode','CustomerID','DateKey','InvoiceDate','Country','Quantity','UnitPrice','LineType','LineRevenue','SalesRevenue','ReturnValue']]
    facts.to_csv(processed/'transactions.csv',index=False,float_format='%.6f')
    facts.to_parquet(processed/'transactions.parquet',index=False)
    rejects.head(5000).to_csv(processed/'excluded_rows_review.csv',index=False)
    for name,frame in [('customers',customers),('products',products[['StockCode','Description']]),('dates',dates)]:frame.to_csv(processed/(name+'.csv'),index=False,float_format='%.6f')
    for name,frame in [('monthly_revenue',monthly),('country_revenue',country),('product_performance',products),('customer_segments',segments),('cohort_retention',retention)]:frame.to_csv(exports/(name+'.csv'),index=False,float_format='%.6f')
    rfm.to_csv(processed/'customer_rfm.csv',index=False,float_format='%.6f')
    n=len(rfm); repeat=int(rfm.Frequency.ge(2).sum())
    top_cut=max(1,int(np.ceil(n*.1))); top_share=rfm.nlargest(top_cut,'Monetary').Monetary.sum()/rfm.Monetary.sum()
    metrics={'gross_revenue_gbp':float(sales.SalesRevenue.sum()),'returns_gbp':float(d.ReturnValue.sum()),'net_revenue_gbp':float(d.LineRevenue.sum()),'sale_orders':int(sales.InvoiceNo.nunique()),'identified_customers':n,'repeat_customers':repeat,'repeat_customer_share':repeat/n,'average_order_value_gbp':float(sales.SalesRevenue.sum()/sales.InvoiceNo.nunique()),'top_decile_customer_gross_revenue_share':float(top_share),'anonymous_gross_revenue_share':float(sales.loc[sales.CustomerID.eq('UNKNOWN'),'SalesRevenue'].sum()/sales.SalesRevenue.sum()),'first_date':str(d.InvoiceDate.min()),'last_date':str(d.InvoiceDate.max()),'countries':int(d.Country.nunique()),'products':int(d.StockCode.nunique()),'snapshot_date':rfm.SnapshotDate.iloc[0],**quality}
    (reports/'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    print(json.dumps(metrics,indent=2),flush=True)
    return metrics

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);args=parser.parse_args()
    if not args.source.is_file():parser.error('Source workbook not found')
    run(args.source)
