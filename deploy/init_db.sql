-- ----------------------------
--  Table structure for `users`
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
	`id` INT NOT NULL AUTO_INCREMENT COMMENT 'user id',
	`username` VARCHAR(100) NOT NULL,
	`password` VARCHAR(100) NOT NULL,
	`gender` ENUM('M','F') NOT NULL DEFAULT 'M'',
	`active` BOOLEAN NOT NULL DEFAULT '1' COMMENT 'User Active',
	`login_time` INT NULL DEFAULT '0' COMMENT 'login timestamp, mainly for JWT time checking',
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`, `username`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='User Table'
;

-- --------------------------------------
--  Table structure for `project_records`
-- --------------------------------------
DROP TABLE IF EXISTS `project_records`;
CREATE TABLE IF NOT EXISTS `project_records` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`uuid` VARCHAR(100) NOT NULL,
	`app` ENUM('RIM', 'CTMS') NOT NULL,
	`customer_name` VARCHAR(100),
	`project_name` VARCHAR(100),
	`remark` VARCHAR(255),
	`create_username` VARCHAR(100),
	`update_username` VARCHAR(100),
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`, `uuid`, `app`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='Project Summary Table'
;

-- --------------------------------------
--  Table structure for `rim_summary_records`
-- --------------------------------------
DROP TABLE IF EXISTS `rim_summary_records`;
CREATE TABLE IF NOT EXISTS `rim_summary_records` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`uuid` VARCHAR(100) NOT NULL COMMENT 'project uuid',
	`version` INT NOT NULL DEFAULT 1 COMMENT 'version of the project',
	`remark` VARCHAR(255),
	`is_customized` BOOLEAN DEFAULT 0 COMMENT 'is this estimation based on t-shirt templates',
	`discount` FLOAT NOT NULL DEFAULT 0 COMMENT 'overall discount',
	`total_reg_users` INT NOT NULL DEFAULT 0,
	`conc_reg_users` INT NOT NULL DEFAULT 0,
	`total_pub_users` INT NOT NULL DEFAULT 0,
	`conc_pub_users` INT NOT NULL DEFAULT 0,
	`total_view_users` INT NOT NULL DEFAULT 0,
	`conc_view_users` INT NOT NULL DEFAULT 0,
	`prod_envs` INT DEFAULT 1,
	`nonprodval_envs` INT DEFAULT 0,
	`nonprod_envs` INT DEFAULT 0,
	`is_multitenant` BOOLEAN NOT NULL DEFAULT 1,
	`multitenant_db_ratio` FLOAT NOT NULL DEFAULT 0.0625 COMMENT 'A tenant uses 6.25% of the DB',
	`has_prod_read_replica_db` BOOLEAN NOT NULL DEFAULT 1,
	`has_nonprodval_read_replica_db` BOOLEAN NOT NULL DEFAULT 1,
	`has_nonprod_read_replica_db` BOOLEAN NOT NULL DEFAULT 1,
	`has_citrix` BOOLEAN NOT NULL DEFAULT 1,
	`db_storage_gb` INT NOT NULL DEFAULT 512 COMMENT 'Oracle DB VM storage size (GB/Vm)',
	`azure_region` ENUM('US','EU','CN') NOT NULL DEFAULT 'CN' COLLATE 'utf8mb4_general_ci',
	`currency` ENUM('USD','EUR','CNY') NOT NULL DEFAULT 'CNY',
	`contract_term` INT NOT NULL DEFAULT 3 COMMENT 'customer contract term in years',
	`has_power_bi` BOOLEAN NOT NULL DEFAULT 0 COMMENT 'Power BI Related, for future use',
	`report_creators` INT NOT NULL DEFAULT 0 COMMENT 'Power BI Related, for future use',
	`super_users` INT NOT NULL DEFAULT 0 COMMENT 'Power BI Related, for future use',
	`standard_users` INT NOT NULL DEFAULT 0 COMMENT 'Power BI Related, for future use',
	`azure_fileshare_storage_gb` INT NOT NULL DEFAULT 0 COMMENT 'if we provide file share',
	`azure_fileshare_sync_servers` INT NOT NULL DEFAULT 1 COMMENT 'if we provide file share',
	`has_azure_ri_discount` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'user 1-year or 3-year RI rate if possible',
    `has_vendor_discount` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'Vendor pre-agreed discounts included (e.g. Oracle)',
    `sla` FLOAT NOT NULL DEFAULT 0.995 COMMENT '99.5% Availability',
    `has_dr` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'has Disaster Recovery design',
    `dr_rpo` INT NOT NULL DEFAULT 1 COMMENT '1 hour RPO',
    `dr_rto` INT NOT NULL DEFAULT 1 COMMENT '8 hour RTO',
	`create_username` VARCHAR(100),
	`update_username` VARCHAR(100),
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`, `uuid`, `version`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='Quote Summary Table'
;

-- --------------------------------------
--  Table structure for `env_summary_records`
-- --------------------------------------
DROP TABLE IF EXISTS `env_summary_records`;
CREATE TABLE IF NOT EXISTS `env_summary_records` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`uuid` VARCHAR(100) NOT NULL COMMENT 'project uuid',
	`version` INT NOT NULL DEFAULT 1 COMMENT 'version of the project',
	`env` ENUM('PROD','NONPRODVAL','NONPROD','SHARED') NOT NULL DEFAULT 'SHARED',
	`tshirt_size` ENUM('XSMALL','SMALL','MEDIUM', 'LARGE', 'XLARGE') NOT NULL,
	`qty` INT NOT NULL DEFAULT 1 COMMENT 'number of environments',
	`uptime_ratio` FLOAT NOT NULL DEFAULT 1 COMMENT 'uptime ratio of the environment, default 100% (always up)',
	`shared_ratio` FLOAT NOT NULL DEFAULT 1 COMMENT 'shared ratio of the environment, default 100% (not shared)',
	`create_username` VARCHAR(100),
	`update_username` VARCHAR(100),
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`, `uuid`, `version`, `env`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='environment summaryTable'
;

-- --------------------------------------
--  Table structure for `detail_records`
-- --------------------------------------
DROP TABLE IF EXISTS `detail_records`;
CREATE TABLE IF NOT EXISTS `detail_records` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`uuid` VARCHAR(100) NOT NULL COMMENT 'project uuid',
	`version` INT NOT NULL DEFAULT 1 COMMENT 'version of the project',
	`env` ENUM('PROD','NONPRODVAL','NONPROD','SHARED') NOT NULL DEFAULT 'PROD' COMMENT 'environment name',
	`remark` VARCHAR(255),
	`vendor` VARCHAR(100) COMMENT 'vendor of the resource',
	`sku` VARCHAR(100) NOT NULL COMMENT 'sku of the part, use to get resource details',
	`qty` INT NOT NULL DEFAULT 1 COMMENT 'quantity of the resource',
	`app_role` VARCHAR(255) COMMENT 'The role of this resource',
    `lv` ENUM('PRIMARY', 'SECONDARY') NOT NULL DEFAULT 'PRIMARY' COMMENT 'main resource or as part of the resource',
	`bom_type` ENUM('LABOR','INFRA','LICENSE','SUPPORT') NOT NULL COMMENT 'BOM type shown on the summary report',
	`bom_subtype` VARCHAR(100) COLLATE 'utf8mb4_general_ci' COMMENT 'BOM sub type name, shown on the summary report',
	`resource_type` VARCHAR(100) NOT NULL COMMENT 'vendor specific type, e.g. Azure - Virtual Machine',
	`billing_type` ENUM('ANNUAL','ONEOFF') NOT NULL DEFAULT 'ANNUAL',
	`unit_price` FLOAT NOT NULL COMMENT 'annual price or one off cost',
	`total_price` FLOAT NOT NULL COMMENT 'unit_price * qty',
	`currency` ENUM('USD','EUR','CNY') NOT NULL DEFAULT 'CNY',
	`create_username` VARCHAR(100),
	`update_username` VARCHAR(100),
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`, `uuid`, `version`, `env`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='Quote detail Table'
;

-- ------------------------------------------------
--  Table structure for `project_price_results`
-- ------------------------------------------------
DROP TABLE IF EXISTS `project_price_results`;
CREATE TABLE IF NOT EXISTS `project_price_results` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`uuid` VARCHAR(100) NOT NULL COMMENT 'project uuid',
	`version` INT NOT NULL DEFAULT 1 COMMENT 'version of the project',
	`price_name` VARCHAR(100) NOT NULL COMMENT 'the displayed name of the price',
	`amount` FLOAT NOT NULL COMMENT 'amount of this price item',
	`currency` ENUM('USD','EUR','CNY') NOT NULL DEFAULT 'CNY',
	`create_username` VARCHAR(100),
	`update_username` VARCHAR(100),
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`, `uuid`, `version`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='Headline prices of the project'
;


-- --------------------------------------
--  Table structure for `rim_tshirt_size`
-- --------------------------------------
DROP TABLE IF EXISTS `rim_tshirt_size`;
CREATE TABLE IF NOT EXISTS `rim_tshirt_size` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`tshirt_size` ENUM('XSMALL','SMALL','MEDIUM', 'LARGE', 'XLARGE') NOT NULL,
	`db_size_upper` INT NOT NULL COMMENT 'upper limit of that T-Shirt size',
	`azure_file_usage` FLOAT NOT NULL,
	`create_username` VARCHAR(100),
	`update_username` VARCHAR(100),
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='RIM T-Shirt Size'
;


-- --------------------------------------
--  Table structure for `dimension_templates`
-- --------------------------------------
DROP TABLE IF EXISTS `dimension_templates`;
CREATE TABLE IF NOT EXISTS `dimension_templates` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `app` ENUM('RIM', 'CTMS') NOT NULL,
    `env` ENUM('PROD','NONPRODVAL','NONPROD','SHARED') NOT NULL DEFAULT 'PROD' COMMENT 'environment name',
    `tshirt_size` ENUM('SHARED', 'XSMALL','SMALL','MEDIUM', 'LARGE', 'XLARGE') NOT NULL,
    `app_role` VARCHAR(255) NOT NULL COMMENT 'The role of this resource',
    `sku` VARCHAR(100) NOT NULL COMMENT 'sku of the resource, sku+os_type+region to identify the price',
    `os_type` ENUM('WINDOWS','LINUX') COMMENT 'operation system of the resource, only for Azure VM',
    `qty` INT NOT NULL DEFAULT 1 COMMENT 'quantity of the resource',
    `is_asr_required` BOOLEAN NOT NULL DEFAULT 1 COMMENT 'only prod and db need ASR',
    `backup_type` ENUM('FILE', 'APP', 'DB') COMMENT 'backup plan name',
    `weekly_data_chg_rate` FLOAT NOT NULL DEFAULT 0,
    `disk1` VARCHAR(100) COMMENT 'OS Disk sku name, usually P10:128G',
    `disk2` VARCHAR(100) COMMENT 'App Disk sku name, usually P6:64G or P10:128G',
    `linux_dist` ENUM('RHEL', 'CENTOS') COMMENT 'linux distribution for linux OS',
    `create_username` VARCHAR(100),
    `update_username` VARCHAR(100),
    `create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`, `app`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='Calyx app dimension templates'
;
--  `lv` ENUM('PRIMARY', 'SECONDARY') NOT NULL DEFAULT 'PRIMARY' COMMENT 'main resource or as part of the resource',


-- --------------------------------------
--  Table structure for `resource_prices`
-- --------------------------------------
DROP TABLE IF EXISTS `resource_prices`;
CREATE TABLE IF NOT EXISTS `resource_prices` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`vendor` VARCHAR(100) COMMENT 'Vendor Name',
	`service_name` VARCHAR(100) COMMENT 'Azure resources service name, or vendor product categories',
	`description` VARCHAR(255) COMMENT 'Description of the product',
	`sku` VARCHAR(100) NOT NULL COMMENT 'sku of the resource, sku+os_type+region to identify the price',
	`os_type` ENUM('WINDOWS','LINUX') COMMENT 'operation system of the resource, only for Azure VM',
	`currency` ENUM('USD','EUR','CNY') NOT NULL DEFAULT 'CNY',
	`billing_type` ENUM('ANNUAL','ONEOFF') NOT NULL DEFAULT 'ANNUAL',
	`unit_price` FLOAT NOT NULL COMMENT 'annual price or one off cost',
	`reservation_term` INT NOT NULL DEFAULT 0 COMMENT 'contract term of years, only for annual prices',
	`azure_region` ENUM('CN EAST 2', 'CN NORTH 2', 'EU WEST', 'EU NORTH', 'US EAST 2', 'US CENTRAL')  COMMENT 'Only for Azure resources',
	`create_username` VARCHAR(100),
	`update_username` VARCHAR(100),
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`, `sku`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='component resource prices'
;

-- --------------------------------------
--  Table structure for `azure_vm_spec`
-- --------------------------------------
DROP TABLE IF EXISTS `azure_vm_spec`;
CREATE TABLE IF NOT EXISTS `azure_vm_spec` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`sku` VARCHAR(100) NOT NULL,
	`cpu` INT NOT NULL,
	`ram` FLOAT NOT NULL COMMENT 'Unit: GB',
	`storage` INT COMMENT 'Unit: GB',
	`create_username` VARCHAR(100),
	`update_username` VARCHAR(100),
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`, `sku`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='Azure VM specification'
;

-- --------------------------------------
--  Table structure for `azure_disk_spec`
-- --------------------------------------
DROP TABLE IF EXISTS `azure_disk_spec`;
CREATE TABLE IF NOT EXISTS `azure_disk_spec` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`sku` VARCHAR(100) NOT NULL,
	`storage` INT COMMENT 'Unit: GB',
	`create_username` VARCHAR(100),
	`update_username` VARCHAR(100),
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`, `sku`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='Azure disk storage specification'
;

-- --------------------------------------
--  Table structure for `app_role_os_map`
-- --------------------------------------
DROP TABLE IF EXISTS `app_role_os_map`;
CREATE TABLE IF NOT EXISTS `app_role_os_map` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`app` ENUM('RIM', 'CTMS') NOT NULL,
	`app_role` VARCHAR(255) NOT NULL COMMENT 'The role of this vm',
	`os_type` ENUM('WINDOWS','LINUX') COMMENT 'operation system of the vm, only for Azure VM',
	`create_username` VARCHAR(100),
	`update_username` VARCHAR(100),
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`, `app`, `app_role`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='mapping vm os type to role in application'
;

-- --------------------------------------
--  Table structure for `backup_ratio`
-- --------------------------------------
DROP TABLE IF EXISTS `backup_ratio`;
CREATE TABLE IF NOT EXISTS `backup_ratio` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`env` ENUM('PROD','NONPRODVAL','NONPROD','SHARED') NOT NULL COMMENT 'environment name',
	`server_type` ENUM('APP','DB','FILE') NOT NULL COMMENT 'server usage type',
	`action` ENUM('FIRST_DEDUPE', 'FIRST_COMPRESS', 'ONGOING_DEDUPE', 'ONGOING_COMPRESS') NOT NULL COMMENT 'backup action types',
	`ratio` FLOAT NOT NULL COMMENT 'compress ratio',
	`create_username` VARCHAR(100),
	`update_username` VARCHAR(100),
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='the backup ratio with experienced data'
;

-- --------------------------------------
--  Table structure for `exchange_rate`
-- --------------------------------------
DROP TABLE IF EXISTS `exchange_rate`;
CREATE TABLE IF NOT EXISTS `exchange_rate` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`currency` ENUM('USD','EUR','GBP','CNY') NOT NULL COMMENT 'currency code',
	`rate` FLOAT NOT NULL DEFAULT 1 COMMENT 'exchange rate to USD',
	`create_username` VARCHAR(100),
	`update_username` VARCHAR(100),
	`create_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`) USING BTREE
)
DEFAULT CHARSET=utf8mb4
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=8
COMMENT='the exchange rate to USD'
;

-- --------------------------------------
--  View structure for `detail_records`
-- --------------------------------------
-- CREATE OR REPLACE VIEW `project_overview` AS
--   SELECT P.*
--     FROM project_records P
-- LEFT JOIN