# Preparing our environment

Complete the following steps in your local machine (or an equivalent dev environment):

- Open the terminal, go to the directory when the repository was downloaded and run the following command:
```
pip install -r requirements.txt
```

- Notes:
    - We use a python version 3.10 or greater.

## Troubleshooting pyarrow related issues
- If you do not have `pyarrow` installed, you do not need to install it yourself; installing `Snowpark` automatically installs the appropriate version.
- Do not reinstall a different version of pyarrow after installing Snowpark.

# Accessing data on Snowflake Marketplace

Snowflake Marketplace provides visibility to a wide variety of datasets from third-party data stewards which broaden access to data points used to transform business processes. Snowflake Marketplace also removes the need to integrate and model data by providing secure access to data sets fully maintained by the data provider.

## Log into Snowsight

1. In a supported web browser, navigate to https://app.snowflake.com.
2. Provide your account name or account URL. If you've previously signed in to Snowsight, you might see an account name that you can select.
3. Sign in using your Snowflake account credentials.

## Obtain dataset from Snowflake Marketplace

1. At the top left corner, make sure you are logged in as ACCOUNTADMIN (switch role to ACCOUNTADMIN if not).
2. Navigate to the Cybersyn Financial & Economic Essentials listing in the Snowflake Marketplace by clicking [here](https://t.influ2.com/p/g/?clid=60a8506e-1d1b-4f8d-b9b5-22274c239afb&a=&caid=&s=&dt=Frosty%3A%20Build%20an%20LLM%20Chatbot%20in%20Streamlit%20on%20your%20Snowflake%20Data&id=here&ref=https%3A%2F%2Fquickstarts.snowflake.com%2Fguide%2Ffrosty_llm_chatbot_on_streamlit_snowflake%2F%3F_fsi%3DxxsTvsN0%230&r=https%3A%2F%2Fapp.snowflake.com%2Fmarketplace%2Flisting%2FGZTSZAS2KF7%2Fcybersyn-inc-cybersyn-financial-economic-essentials%3F_fsi%3DxxsTvsN0%26_fsi%3DxxsTvsN0).
3. Select "**Get.**"
4. Select the appropriate roles to access the database being created and accept the Snowflake consumer terms and Cybersyn's terms of use.
5. Select "**Query Data,**" which will open a worksheet with example queries.

![Snowflake Financial Data Example](/images/example_data.png)

## Prep database

Before building our app, we need to run a set of SQL statements in Snowflake to create two views. The first view is `FROSTY_SAMPLE.CYBERSYN_FINANCIAL.FINANCIAL_ENTITY_ATTRIBUTES_LIMITED`, which includes:

- A subset of `cybersyn_financial__economic_essentials.cybersyn.financial_institution_attributes`:
    - Totals for assets, real estate loans, securities, deposits; % of deposits insured; total employees.

The second view is `FROSTY_SAMPLE.CYBERSYN_FINANCIAL.FINANCIAL_ENTITY_ANNUAL_TIME_SERIES`, which includes:

- A modified version of `cybersyn_financial__economic_essentials.cybersyn.financial_institution_timeseries` as follows:
    - Entity and attribute metadata is joined directly
        - Only the set of attributes from `FINANCIAL_ENTITY_ATTRIBUTES_LIMITED` are exposed.
        - Only the **end-of-year metrics (YYYY-12-31)** are included, and a YEAR column is provided instead of the date column.

You can copy the SQL statements from the `prep_database_query.sql` file and run them in the worksheet created for your sample queries.