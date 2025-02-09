BEGIN TRANSACTION;
DROP TABLE IF EXISTS "aquarium_avg";
CREATE TABLE IF NOT EXISTS "aquarium_avg" (
	"id"	integer,
	"date"	TEXT,
	"time"	TEXT,
	"unixtime"	integer,
	"range_group"	integer,
	"air_temp_avg"	REAL,
	"air_himid_avg"	REAL,
	"water_temp_avg"	REAL,
	"water_ph_avg"	REAL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
COMMIT;
