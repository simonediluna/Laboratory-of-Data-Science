/*********** Create tables ***********/
/* The UNIQUE constraints were removed 
   after populating the dimension tables. */

USE simonediluna_DB;
GO 

CREATE TABLE cpu_product (
	cpu_id int IDENTITY(1,1) NOT NULL,
	cpu_code int NOT NULL,
	brand varchar(7) NOT NULL,
	series varchar(25) NOT NULL,
	cpu_name varchar(39) NOT NULL,
	n_cores smallint NOT NULL,
	socket varchar(12) NOT NULL,
	CONSTRAINT PK_cpu_product PRIMARY KEY (cpu_id),
	CONSTRAINT UNIQUE_cpu_product UNIQUE (cpu_code)
);

CREATE TABLE geography (
	geo_id int IDENTITY(1,1) NOT NULL,
	geo_code int NOT NULL,
	continent varchar(7) NOT NULL,
	country varchar(30) NOT NULL,
	region varchar(32) NOT NULL,
	currency char(3) NOT NULL,
	CONSTRAINT PK_geography PRIMARY KEY (geo_id),
	CONSTRAINT UNIQUE_geography UNIQUE (geo_code)
);

CREATE TABLE time_by_day (
	time_id int NOT NULL,
	the_year smallint NOT NULL,
	month_of_year tinyint NOT NULL,
	day_of_month tinyint NOT NULL,
	week_of_year tinyint NOT NULL,
	the_quarter char(2) NOT NULL,
	day_name char(9) NOT NULL,
	CONSTRAINT PK_time_by_day PRIMARY KEY (time_id)
);

CREATE TABLE vendor (
	vendor_id int IDENTITY(1,1) NOT NULL,
	vendor_code int NOT NULL,
	vendor_name nvarchar(32) NOT NULL,
	CONSTRAINT PK_vendor PRIMARY KEY (vendor_id),
	CONSTRAINT UNIQUE_vendor UNIQUE (vendor_code)
);

GO

CREATE TABLE cpu_sales_fact (
	fact_id int IDENTITY(1,1) NOT NULL,
	cpu_id int NOT NULL,
	time_id int NOT NULL,
	geo_id int NOT NULL,
	vendor_id int NOT NULL,
	sales_usd money NOT NULL DEFAULT 0,
	sales_currency money NOT NULL DEFAULT 0,
	cost money NOT NULL DEFAULT 0,
	CONSTRAINT PK_cpu_sales_fact 
		PRIMARY KEY (fact_id),
	CONSTRAINT FK_cpu_sales_fact_cpu_product
		FOREIGN KEY (cpu_id) REFERENCES cpu_product (cpu_id),
	CONSTRAINT FK_cpu_sales_fact_time_by_day
		FOREIGN KEY (time_id) REFERENCES time_by_day (time_id),
	CONSTRAINT FK_cpu_sales_fact_geography
		FOREIGN KEY (geo_id) REFERENCES geography (geo_id),
	CONSTRAINT FK_cpu_sales_fact_vendor
		FOREIGN KEY (vendor_id) REFERENCES vendor (vendor_id)
);