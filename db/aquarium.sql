BEGIN TRANSACTION;
DROP TABLE IF EXISTS "aquarium";
CREATE TABLE IF NOT EXISTS "aquarium" (
	"id"	integer,
	"date"	TEXT,
	"time"	TEXT,
	"unixtime"	integer,
	"air_temp"	REAL,
	"air_himid"	REAL,
	"water_temp"	REAL,
	"water_ph"	REAL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
COMMIT;
