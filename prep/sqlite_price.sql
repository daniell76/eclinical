-- Get CN Prices
  SELECT 'Azure' vendor,
         service_name,
         UPPER(sku),
         os_type,
         currency,
         'ANNUAL' billing_type,
         yearly_price unit_price,
         CAST(reservation_term AS INTEGER) reservation_term,
         UPPER(location) azure_region
    FROM price
   WHERE location IN ('CN East 2', 'CN North 2')
ORDER BY service_name, sku, os_type, reservation_term;

-- Get VM Specs
  SELECT DISTINCT 
         REPLACE(UPPER(vm_type), ' ', '_') sku, 
         cpu, 
         ram, 
         storage 
    FROM az_cn_cpp_price 
   WHERE sku 
      IN (
  SELECT DISTINCT 
         UPPER(sku) 
    FROM price 
   WHERE location IN ('CN East 2', 'CN North 2') 
     AND service_name = "Virtual Machines" 
         );

-- Update dimension_templates sku to upper case
UPDATE `dimension_templates` SET `sku` = UPPER(sku);
UPDATE `dimension_templates` SET `sku` = REPLACE(sku, ' ', '_');

-- Get DB related vm prices
-- We need E8-4S_V3(E8S_V3) / E16-8S_V3(E16S_V3) / E32-16S_v3(E32S_V3)
SELECT * FROM resource_prices WHERE (sku LIKE 'E32-%' OR sku LIKE 'E32S%') AND os_type='LINUX';
SELECT * FROM resource_prices WHERE (sku LIKE 'E16-%' OR sku LIKE 'E16S%') AND os_type='LINUX';
SELECT * FROM resource_prices WHERE (sku LIKE 'E8-%' OR sku LIKE 'E8S%') AND os_type='LINUX';
