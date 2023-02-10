#!/usr/bin/env python
# coding: utf-8

# In[1]:


#import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt


# In[2]:


#Load KPMG dataset
df_draft = pd.read_csv("Bản sao của HomeTest 1 - KPMG Data.xlsx - Transactions.csv")


# In[3]:


#Filtering orders_status is approved
is_Approved = df_draft['order_status'] == 'Approved'
df = df_draft[is_Approved]


# In[4]:


df = df.drop_duplicates()
df = df.dropna(subset=['customer_id'])


# In[5]:


# Create a function to get month from transaction_date
def get_month(x): return dt.datetime(x.year, x.month, 1)


# In[6]:


#Convert transaction_date data type: from string to datetime
df["transaction_date"] =  pd.to_datetime(df["transaction_date"], format="%d/%m/%Y")
# Create transaction_date column based on month and store in TransactionMonth
df['order_month'] = df['transaction_date'].apply(get_month) 


# In[7]:


# Grouping by customer_id and select order_month
Customer_group = df.groupby('customer_id')['order_month']
# Finding the first transaction.
df['CohortMonth'] = Customer_group.transform('min')


# In[8]:


# Creating function to return year, month, day
def get_date_int(df, column):
    year = df[column].dt.year
    month = df[column].dt.month
    day = df[column].dt.day
    return year, month, day
# Getting the integers for date parts from the `order_month` column
transcation_year, transaction_month, _ = get_date_int(df, 'order_month')
# Getting the integers for date parts from the `CohortDay` column
cohort_year, cohort_month, _ = get_date_int(df, 'CohortMonth')


# In[9]:


#  Get the  difference in years
years_diff = transcation_year - cohort_year
# Calculate difference in months
months_diff = transaction_month - cohort_month
# calculate the difference in months between order_month vs CohortMonth
df['CohortIndex'] = years_diff * 12 + months_diff  + 1 


# In[10]:


# Counting daily active user from each cohort
Customer_group = df.groupby(['CohortMonth', 'CohortIndex'])
# Counting number of unique customer_id in each group of CohortMonth and CohortIndex
cohort_data = Customer_group['customer_id'].apply(pd.Series.nunique)
cohort_data = cohort_data.reset_index()
 # Adding column names to the dataframe created above
cohort_counts = cohort_data.pivot(index='CohortMonth',
                                 columns ='CohortIndex',
                                 values = 'customer_id')


# In[11]:


#Setup cohort_sizes + retention
cohort_sizes = cohort_counts.iloc[:,0]
retention = cohort_counts.divide(cohort_sizes, axis=0)


# In[12]:


# Create retention index
retention.index = retention.index.strftime('%Y-%m')
retention.index


# In[13]:


# Setup the figure size
plt.figure(figsize=(16, 10))

# Adding title for cohort chart
plt.title('MoM Retention Rate for Customer Transaction Data', fontsize = 15)

# Creating the cohort chart
sns.heatmap((retention*100).round(1), annot=True, fmt= '',cmap='YlGnBu', vmin = 30 , vmax = 100)
plt.ylabel('Cohort Month')
plt.xlabel('Cohort Index')
plt.yticks( rotation='360')
plt.show()


# In[14]:


#Insights
#1, Những khách hàng đăng kí và đặt hàng đầu tiên vào tháng 7/2017 có tỉ lệ giữ chân rất cao( tận 48.1%) sau 5 tháng hoạt động
#2, Những khách hàng đăng kí và đặt hàng đầu tiên vào tháng 4/2017 có tỉ lệ giữ chân ở mức ổn định và tương đối cao: 45,1% (tháng thứ 4), 42,1% (tháng thứ 5), 42,7% (tháng thứ 7) 
#3, Những khách hàng đăng kí và đặt hàng đầu tiên vào tháng 5/20217 cũng có tỉ lệ giữ chân khá cao, ổn định : 40,4%,39%,41,3% ở các tháng thứ 2,3,4 hoạt động
#4, Nhìn vào các insights trên, chúng ta có thể thấy những khách hàng bắt đầu đặt hàng từ giữa năm 4,5,6,7,8 có xu hướng đặt hàng ổn định, và tương đối cao hơn so với các tháng còn lại trong năm
#5, Những khách hàng có đặt hàng ở đầu năm tháng 1,2 thì chỉ cho thấy sự ổn định, không có gì nổi trội lắm
#6, tỉ lệ giữ trên khách khàng trong năm của KPMG khá ổn, toàn từ 30% trở lên ( ngoại trừ 1 tháng 25,5%)

#Recommendation
#1, Cần có những chính sách ưu đãi hấp dẫn cho khách hàng những tháng đầu năm để tăng tỉ lệ đặt hàng(giữ chân) qua các tháng
#2, Những tháng giữa năm có tỉ lệ giữ chân cao hơn các tháng khác -> cần phải tìm ra nguyên nhân tại sao (bằng các dữ liệu liên quan, trực quan hoá các dữ liệu khác) ? để áp dụng cho các tháng khác

