-- SQL Database Scheme for fatty beer brewery

-- Lookup tables

-- measure_units
DROP TABLE if exists measure_units;
CREATE TABLE measure_units(
id INTEGER PRIMARY KEY,
unit TEXT UNIQUE,
unit_type TEXT
);
INSERT INTO measure_units (unit,unit_type) VALUES ("g","mass");
INSERT INTO measure_units (unit,unit_type) VALUES ("kg","mass");
INSERT INTO measure_units (unit,unit_type) VALUES ("unit-mass","mass");
       
INSERT INTO measure_units (unit,unit_type) VALUES ("L","volume");
INSERT INTO measure_units (unit,unit_type) VALUES ("unit-volume","volume");
INSERT INTO measure_units (unit,unit_type) VALUES ("C","temperature");
INSERT INTO measure_units (unit,unit_type) VALUES ("unit-temperature","temperature");
INSERT INTO measure_units (unit,unit_type) VALUES ("L/hr","flow");
INSERT INTO measure_units (unit,unit_type) VALUES ("cm","length");
INSERT INTO measure_units (unit,unit_type) VALUES ("m","length");
INSERT INTO measure_units (unit,unit_type) VALUES ("unit","generic");
INSERT INTO measure_units (unit,unit_type) VALUES ("unit-hops","mass");
INSERT INTO measure_units (unit,unit_type) VALUES ("unit-malt","mass");
INSERT INTO measure_units (unit,unit_type) VALUES ("unit-yeast","yeast");

CREATE INDEX unit ON measure_units ( unit );

-- Vlave type
DROP TABLE if exists valve_types;
CREATE TABLE valve_types(
valve_type VARCHAR UNIQUE);
INSERT INTO valve_types VALUES ("normally_open");
INSERT INTO valve_types VALUES ("normally_closed");


-- Packaging type
DROP TABLE if exists packaging_types;
CREATE TABLE packaging_types(
id INTEGER PRIMARY KEY,
packaging_type TEXT UNIQUE
);
INSERT INTO packaging_types (packaging_type) VALUES ("bottle");
INSERT INTO packaging_types (packaging_type) VALUES ("keg");


-- Open status
DROP TABLE if exists open_status;
CREATE TABLE open_status
( 
id INTEGER PRIMARY KEY,
status VARCHAR UNIQUE
);
INSERT INTO open_status (status) VALUES  ("open");
INSERT INTO open_status (status) VALUES ("closed");
INSERT INTO open_status (status) VALUES  ("partial");
CREATE INDEX status on open_status(status);

-- Liquid types
DROP TABLE if exists liquid_types;
CREATE TABLE liquid_types
(
id INTEGER PRIMARY KEY,
liquid_type TEXT UNIQUE
);
INSERT INTO liquid_types (liquid_type) VALUES ("purified water");
INSERT INTO liquid_types (liquid_type) VALUES ("cleaning_chemical");
INSERT INTO liquid_types (liquid_type) VALUES ("wort");
INSERT INTO liquid_types (liquid_type) VALUES ("beer");
CREATE INDEX liquid_type ON liquid_types(liquid_type);

-- Yeast feeding type
DROP TABLE if exists yeast_types;
CREATE TABLE yeast_types
(
feeding_type TEXT
);
INSERT INTO yeast_types (feeding_type) VALUES ("bottom");
INSERT INTO yeast_types (feeding_type) VALUES ("top");
CREATE INDEX feeding_type ON yeast_types(feeding_type);

-- Batch status types
DROP TABLE if exists batch_status;
CREATE TABLE batch_status
( 
id INTEGER PRIMARY KEY,
status TEXT
);
INSERT INTO batch_status (status) VALUES ("pending");
INSERT INTO batch_status (status) VALUES ("in progress");
INSERT INTO batch_status (status) VALUES ("completed");

-- Valve relationship types
DROP TABLE if exists valve_relationship_types;
CREATE TABLE valve_relationship_types
(
relationship_type VARCHAR UNIQUE
);
INSERT INTO valve_relationship_types (relationship_type) VALUES ('into_container');
INSERT INTO valve_relationship_types (relationship_type) VALUES ('out_of_container');

DROP TABLE if exists ingredient_types;
CREATE TABLE ingredient_types
(
id INTEGER PRIMARY KEY,
ingredient_type VARCHAR UNIQUE
);
INSERT INTO ingredient_types (ingredient_type) VALUES ("yeast");
INSERT INTO ingredient_types (ingredient_type) VALUES ("water");
INSERT INTO ingredient_types (ingredient_type) VALUES ("hops");
INSERT INTO ingredient_types (ingredient_type) VALUES ("malt");
INSERT INTO ingredient_types (ingredient_type) VALUES ("other");

-- Batch inventory, to track the current status of a batch
DROP TABLE if exists batches;
CREATE TABLE batches
( 
id INTEGER PRIMARY KEY,
batch_name TEXT,
batch_alias TEXT UNIQUE,
code_name TEXT,
batch_type TEXT, 
batch_status TEXT,
FOREIGN KEY(batch_status) REFERENCES batch_status(status)
);

DROP TABLE if exists ingredients;
CREATE TABLE ingredients
( 
id INTEGER PRIMARY KEY,
  ingredient_type VARCHAR,
  ingredient_alias VARCHAR,
  FOREIGN KEY(ingredient_type) REFERENCES ingredient_types(ingredient_type)
);

DROP TABLE if exists hops_inventory;
CREATE TABLE hops_inventory
( 
ingredient INTEGER,
name TEXT,
acidity REAL,
weight REAL,
weight_units VARCHAR DEFAULT 'g',
FOREIGN KEY(ingredient) REFERENCES ingredients(id),
FOREIGN KEY(weight_units) REFERENCES measure_units(unit)
);

DROP TABLE if exists malt_inventory;
CREATE TABLE malt_inventory
( 
ingredient INTEGER,
name TEXT,
weight REAL,
weight_units VARCHAR default 'kg',
FOREIGN KEY(ingredient) REFERENCES ingredients(id),
FOREIGN KEY(weight_units) REFERENCES measure_units(unit)
);


DROP TABLE if exists other_ingredient_inventory;
CREATE TABLE other_ingredient_inventory
( 
ingredient INTEGER,
name TEXT,
amount REAL,
amount_units VARCHAR,
FOREIGN KEY(ingredient) REFERENCES ingredients(id),
FOREIGN KEY(amount_units) REFERENCES measure_units(unit)
);

DROP TABLE if exists yeast_inventory;
CREATE TABLE yeast_inventory
( 
id INTEGER PRIMARY KEY,
ingredient INTEGER,
name TEXT,
 date_created INTEGER,
 yeast_type TEXT,
 amount REAL,
 amount_units VARCHAR DEFAULT 'g',
 current_temperature REAL,
 current_temperature_units VARCHAR DEFAULT 'C',
 prime_temperature REAL,
 prime_temperature_units VARCHAR DEFAULT 'C',
 FOREIGN KEY(prime_temperature_units) REFERENCES measure_units(unit)
 FOREIGN KEY(ingredient) REFERENCES ingredients(id),	
 FOREIGN KEY(yeast_type) REFERENCES yeast_types( id ),
 FOREIGN KEY(amount_units) REFERENCES measure_units(unit)
);

DROP TABLE if exists containers;
CREATE TABLE containers
(
id INTEGER PRIMARY KEY,
name TEXT UNIQUE,
total_volume REAL,
total_volume_units VARCHAR default "C",
current_volume REAL default 0,
current_volume_units VARCHAR default "L",
target_temperature REAL DEFAULT 20,
target_temperature_units VARCHAR DEFAULT 'C',
current_temperature REAL DEFAULT 20,
current_temperature_units VARCHAR DEFAULT 'C',
clean INTEGER DEFAULT 0,
FOREIGN KEY(total_volume_units) REFERENCES measure_units(unit),
FOREIGN KEY(current_volume_units) REFERENCES measure_units(unit),
FOREIGN KEY(target_temperature_units) REFERENCES measure_units(unit)
);

DROP TABLE if exists liquid_reservoirs;
CREATE TABLE liquid_reservoirs
( 
id INTEGER PRIMARY KEY,
container INTEGER,
mixable INTEGER,
FOREIGN KEY(container) REFERENCES containers(id)
);


DROP TABLE if exists valves;
CREATE TABLE valves
( 
id INTEGER PRIMARY KEY,
valve_name VARCHAR UNIQUE,
valve_type VARCHAR DEFAULT 'normally_closed',
valve_status VARCHAR DEFAULT 'closed',
valve_diameter REAL DEFAULT 1,
valve_diameter_units VARCHAR "units",
FOREIGN KEY(valve_type) REFERENCES valve_types(valve_type),
FOREIGN KEY(valve_status) REFERENCES opening_statuses(status),
FOREIGN KEY(valve_diameter_units) REFERENCES measure_units(unit)
);


-- This basically describes pipes
DROP TABLE if exists containers_valves_join;
CREATE TABLE containers_valves_join
(
container INTEGER,
valve INTEGER,
cont_valve_relationship VARCHAR default 'into_container',
FOREIGN KEY(valve) REFERENCES valves(id),
FOREIGN KEY (container) REFERENCES containers(id),
FOREIGN KEY(cont_valve_relationship) REFERENCES valve_relationships(relationship_type) 
);

DROP TABLE if exists liquids;
CREATE TABLE liquids
(
name TEXT,
liquid_type VARCHAR,
FOREIGN KEY(liquid_type) REFERENCES liquid_types(liquid_type)
);
INSERT INTO liquids (name,liquid_type) VALUES ("purified water","purified_water");
INSERT INTO liquids (name,liquid_type) VALUES ("generic cleaner","cleaning_chemical");

DROP TABLE if exists container_contents;
CREATE TABLE container_contents
( 
container INTEGER,
liquid INTEGER,
liquid_amount REAL,
liquid_amount_units VARCHAR default "L",
solid_ingredient INTEGER,
solid_ingredient_amount REAL,
solid_ingredient_amount_unit VARCHAR,
FOREIGN KEY(container) REFERENCES containers(id),
FOREIGN KEY(liquid) REFERENCES liquids(id),
FOREIGN KEY(solid_ingredient) REFERENCES liquids(id)
);

CREATE TRIGGER dirty_container AFTER UPDATE OF solid_ingredient_amount ON container_contents
WHEN old.solid_ingredient_amount != 0 AND old.liquid_amount !=0 
BEGIN UPDATE container SET clean=1 WHERE container_contents.container=container.id; END;

DROP TABLE if exists mash_tuns;
CREATE TABLE mash_tuns
(
id INTEGER PRIMARY KEY,
container INTEGER,
FOREIGN KEY(container) REFERENCES containers(id)
);

DROP TABLE if exists fermenters;
CREATE TABLE fermenters
(
id INTEGER PRIMARY KEY,
container INTEGER,
FOREIGN KEY(container) REFERENCES containers(id)
);

DROP TABLE if exists packagers;
CREATE TABLE packagers
(
id INTEGER PRIMARY KEY,
packaging_type VARCHAR,
packaging_rate REAL,
packaging_rate_unit VARCHAR default "L/hr",
FOREIGN KEY(packaging_type) REFERENCES packaging_types(type),
FOREIGN KEY(packaging_rate_unit) REFERENCES measure_units(unit)
);

DROP TABLE if exists packaged_beer;
CREATE TABLE packaged_beer
(
packaging_type TEXT,
batch INTEGER,
last_fermenter INTEGER,
FOREIGN KEY (batch) REFERENCES batches(id),
FOREIGN KEY (last_fermenter) REFERENCES fermenter(id)
);


