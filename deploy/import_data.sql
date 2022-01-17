SELECT DISTINCT(sku) FROM resource_prices WHERE vendor='Azure' AND (service_name='Virtual Machines' OR service_name='Storage');
INSERT INTO resource_prices(
                `vendor`,
                `service_name`,
	            `description`,
	            `sku`,
	            `os_type`,
	            `currency`,
	            `billing_type`,
	            `unit_price`,
	            `reservation_term`,
	            `azure_region`
	        )
    SELECT  `vendor`,
            `service_name`,
	        `description`,
	        `sku`,
	        `os_type`,
	        `currency`,
	        `billing_type`,
	        `unit_price`,
	        `reservation_term`,
	        `azure_region`
	FROM    resource_prices_temp;

