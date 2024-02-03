# Allium Engineering Assignment: Wallet PnL

## Challenge
Suppose that this prototype is a success, and we wish to scale this API to
- include 10,000 tokens
- calculate PnL with 5-minute granularity (instead of hourly)
- show PnLs up to the start of the coins (e.g. 2009 for Bitcoin, 2015 for Ethereum),
instead of just the past week
Suggest ways to scale the system to support these requirements.

## Summary
Scaling the Wallet PnL API and ELT Pipeline may include: upgrading the database, improving query performance and schema design, adding rate limiting and caching to the API, using streaming APIs and streaming processing tools for ELT, and breaking out the project into several different microservices. Making these changes will enable faster processing of data, more data ingestion and support for many asynchronous users. I will elaborate on each change and its expected impact below.

## Database Upgrade and Query Performance
Time series databases (TSDBs) are a great choice for projects requiring intense read and write throughput of pairs of time and value data. TSDBs are common in financial systems where large volumes of transactions with time data are processed. TimescaleDB or InfluxDB are good TSDB options which include support for large scans across broad time horizons. These options also offer data management services like regular clean up of old or stale data. 

Regardless of database choice, several improvements can be made to improve query performance for large datasets. In PostgreSQL and many other database products, tables can be partitioned across time or coin. This enables the scanning of smaller sub-sections of data instead of scanning an entire table every time data is requested. Indexes can also add performance to a database. Adding indexes on one or several columns organizes the data so that the SQL engine can more efficiently navigate your database. 

Another suggested update is to add support for asset precision. In crypto, assets have a broad range of supported digits after the decimal point. Keeping a store of asset precision is important for providing clean data to your customers.

## API Rate Limiting and Caching
Adding rate limiting to the api will protect the system from blunt force attacks and increase system stability. Support for caching will enable faster response times to users who repeatedly request the same data. This will also reduce strain on the database as requesting cached data does not require querying the database. Both of these improvements will provide security and stability to the API and will reduce CPU on the database. 

## ELT Streaming
Increasing the data granularity to 5-minute may require streaming apis and processing as opposed to standard RESTAPI calls. Using Apache Kafka or AWS Kinesis Firehose you can capture real-time data from a crypto data stream and periodically (every 5 minutes) load data into your database. Blockchain.com and CyptoCompare offer streaming options which would enable 5-minute granularity. 

## Microservices 
Any production grade system can benefit from microservices architecture. Breaking down a project into smaller pieces, which are then distributed across several servers and databases, enables optimal performance and easier maintenance. However, doing so involves tradeoffs in project complexity and data sharing. When microservices are implemented, data can become siloed in each system. Usually, a central data warehouse is created to join data across systems. 

## Conclusion
Each of the above recommendations will increase the scalability of the Wallet PnL API and ETL pipeline. Making some or all of these changes will support the new system requirements outlined above. 
