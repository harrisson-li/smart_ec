-- noinspection SqlNoDataSourceInspectionForFile
DROP TABLE IF EXISTS environments;

CREATE TABLE environments
(
  "__id__"         INTEGER
    PRIMARY KEY
  AUTOINCREMENT,
  name             TEXT,
  domain           TEXT,
  replace_to       TEXT,
  description      TEXT,
  mark             TEXT,
  etown_url        TEXT,
  oboe_url         TEXT,
  salesforce_url   TEXT,
  tags             TEXT,
  marketing_url    TEXT,
  marketing_ts_url TEXT
);

DROP TABLE IF EXISTS databases;

CREATE TABLE databases
(
  "__id__" INTEGER
    PRIMARY KEY
  AUTOINCREMENT,
  name     TEXT,
  domain   TEXT,
  server   TEXT,
  user     TEXT,
  password TEXT,
  tags     TEXT
);

DROP TABLE IF EXISTS partners;

CREATE TABLE partners
(
  "__id__"     INTEGER
    PRIMARY KEY
  AUTOINCREMENT,
  name         TEXT,
  domain       TEXT,
  country_code TEXT,
  tags         TEXT
);

DROP TABLE IF EXISTS products;

CREATE TABLE products
(
  "__id__"     INTEGER
    PRIMARY KEY
  AUTOINCREMENT,
  partner      TEXT,
  id           INTEGER,
  name         TEXT,
  product_type TEXT,
  main_code    TEXT,
  main_one_day TEXT,
  free_code    TEXT,
  tags         TEXT
);

DROP TABLE IF EXISTS schools;

CREATE TABLE schools
(
  "__id__"      INTEGER
    PRIMARY KEY
  AUTOINCREMENT,
  id            INTEGER,
  partner       TEXT,
  city          TEXT,
  name          TEXT,
  division_code TEXT,
  tags          TEXT,
  lc_city       TEXT,
  ca_city       TEXT
);

CREATE TABLE IF NOT EXISTS test_accounts
(
  environment TEXT NOT NULL,
  member_id   INT  NOT NULL,
  username    TEXT,
  detail      TEXT,
  created_on  TEXT,
  created_by  TEXT,
  tags        TEXT,
  CONSTRAINT test_accounts_pk
  PRIMARY KEY (member_id, environment)
);

CREATE TABLE IF NOT EXISTS suspend_info (
  member_id           TEXT,
  suspend_date        TEXT,
  resume_date         TEXT,
  suspend_external_id TEXT
)