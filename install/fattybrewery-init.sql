-- Default values for inserting 

-- There is equipment, and ingredients

-- First, the equipment

-- Create a mashtun liquid reservoir
DELETE FROM containers;

INSERT INTO containers 
(total_volume,total_volume_units,current_volume,current_volume_units,target_temperature,target_temperature_units,clean)
VALUES
(200,"L",0,"L",20,"C",0);

INSERT INTO liquid_reservoirs
(container,mixable)
VALUES
((SELECT last_insert_rowid()),1);

-- Create a container for the mash tun

INSERT INTO containers 
(total_volume,total_volume_units,current_volume,current_volume_units,target_temperature,target_temperature_units,clean)
VALUES
(100,"L",0,"L",20,"C",0);

DELETE FROM mash_tuns;
INSERT INTO mash_tuns
(container)
VALUES
(( SELECT last_insert_rowid()));

-- Create a fermenter container
INSERT INTO containers 
(total_volume,total_volume_units,current_volume,current_volume_units,target_temperature,target_temperature_units)
VALUES
(100,"L",0,"L",20,"C");

-- Define one basic fermenter, it is a placeholder table for othre values in the future
DELETE FROM fermenters;
INSERT INTO fermenters
(container)
VALUES
((SELECT last_insert_rowid()));

-- One bottler, and one kegger packager. 

DELETE FROM packagers;
INSERT INTO packagers
(packaging_type,packaging_rate,packaging_rate_unit)
VALUES
("bottle",100,"L/hr");


INSERT INTO packagers
(packaging_type,packaging_rate,packaging_rate_unit)
VALUES
("keg",100,"L/hr");


-- One valve each for going into and out of the mashtun
DELETE FROM valves;
INSERT INTO valves (valve_name) VALUES ('mashtun-in-valve-1');

INSERT INTO containers_valves_join (container,valve,cont_valve_relationship) 
VALUES 
( (SELECT id FROM mash_tuns LIMIT 1),(SELECT last_insert_rowid()),'into_container');
INSERT INTO valves (valve_name) VALUES ("mashtun-out-valve-1");
INSERT INTO containers_valves_join (container,valve,cont_valve_relationship) VALUES 
( (SELECT id FROM mash_tuns LIMIT 1),(SELECT last_insert_rowid()),'out_of_container');

-- One valve each for going into and out of the fermenter, but only one required. The others can be rotated into place
INSERT INTO valves (valve_name) VALUES ("fermenter-in-valve-1");
INSERT INTO containers_valves_join (container,valve,cont_valve_relationship) VALUES 
( (SELECT id FROM fermenters LIMIT 1),(SELECT last_insert_rowid()),'into_container');

INSERT INTO valves (valve_name) VALUES ("fermenter-out-valve-1");
INSERT INTO containers_valves_join (container,valve,cont_valve_relationship) VALUES 
( (SELECT id FROM fermenters LIMIT 1),(SELECT last_insert_rowid()),'out_of_container');


-- One valve each for valves going into an out of the reservoir container
INSERT INTO valves (valve_name) VALUES ("reservoir-in-valve-1");
INSERT INTO containers_valves_join (container,valve,cont_valve_relationship) VALUES 
( ( SELECT id FROM liquid_reservoirs LIMIT 1),(SELECT last_insert_rowid()),'into_container');

INSERT INTO valves (valve_name) VALUES ("reservoir-out-valve-1");
INSERT INTO containers_valves_join (container,valve,cont_valve_relationship) VALUES 
( (SELECT id FROM liquid_reservoirs LIMIT 1),(SELECT last_insert_rowid()),'out_of_container');

---

DELETE FROM batches;
INSERT INTO batches
(batch_name,batch_type,batch_alias,batch_status)
VALUES
('fatty-first','generic brew','fatty-first','pending') ;


-- Insert basic ingredients, one of each


DELETE FROM ingredients;
INSERT INTO ingredients
(ingredient_type,ingredient_alias)
VALUES 
('yeast','generic-yeast');

INSERT INTO yeast_inventory
(ingredient,name,amount,amount_units)
VALUES
((SELECT last_insert_rowid()),'generic-yeast',1,'unit-yeast');

INSERT INTO ingredients
(ingredient_type,ingredient_alias)
VALUES
('hops','shwag-hops');

INSERT INTO hops_inventory
(ingredient,name,weight,weight_units)
VALUES
((SELECT last_insert_rowid()),'generic-hops',1,'unit-hops');

INSERT INTO ingredients
(ingredient_type,ingredient_alias)
VALUES
('malt','cow-fodder');

INSERT INTO malt_inventory
(ingredient,name,weight,weight_units)
VALUES
((SELECT last_insert_rowid()),'generic-malt',1,'unit-malt');

INSERT INTO ingredients
(ingredient_type,ingredient_alias)
VALUES
('water','tap-water');


DELETE FROM hops_inventory;
INSERT INTO hops_inventory 
(ingredient,name,weight,weight_units)
VALUES
( (SELECT ingredients.id FROM ingredients WHERE ingredients.ingredient_type LIKE 'hops'),'generic-hops',1,'unit-hops');

DELETE FROM malt_inventory;
INSERT INTO malt_inventory
(ingredient,name,weight,weight_units)
VALUES
( (SELECT ingredients.id FROM ingredients WHERE ingredients.ingredient_type LIKE 'malt'),'generic-malt',1,'unit-malts');


