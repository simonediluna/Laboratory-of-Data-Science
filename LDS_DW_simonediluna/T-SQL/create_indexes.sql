/* Create additional indexes to improve query performance. These indexes
    were built only after populating all the tables in the data mart) */

USE simonediluna_DB;
GO

/* Create a columnstore index for each dimension table */ 
CREATE NONCLUSTERED COLUMNSTORE INDEX NCColStoreInd_cpu_product_brand 
	ON cpu_product (brand);  

CREATE NONCLUSTERED COLUMNSTORE INDEX NCColStoreInd_geography_country 
	ON geography (country);

CREATE NONCLUSTERED COLUMNSTORE INDEX NCColumnStoreInd_time_by_day_the_year 
	ON time_by_day (the_year);
	
CREATE NONCLUSTERED COLUMNSTORE INDEX NCColumnStoreInd_vendor_vendor_name
	ON vendor (vendor_name);

/* Create non clustered indexes on the FKs of the fact table */
CREATE NONCLUSTERED INDEX NonClusteredIndex_cpu_FK
	ON cpu_sales_fact (cpu_id);

CREATE NONCLUSTERED INDEX NonClusteredIndex_geo_FK
	ON cpu_sales_fact (geo_id);
	
CREATE NONCLUSTERED INDEX NonClusteredIndex_time_id_FK
	ON cpu_sales_fact (time_id);
	
CREATE NONCLUSTERED INDEX NonClusteredIndex_vendor_FK
	ON cpu_sales_fact (vendor_id);
