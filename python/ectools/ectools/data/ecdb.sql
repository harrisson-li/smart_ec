DROP TABLE IF EXISTS environments;

CREATE TABLE "environments" (
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
  marketing_ts_url TEXT NULL,
  CONSTRAINT environments_pk PRIMARY KEY (domain, name)
);

INSERT INTO environments (name, domain, replace_to, description, mark, etown_url, oboe_url, salesforce_url, tags, marketing_url, marketing_ts_url) VALUES ('UAT', 'all', 'uat', 'UAT', '', 'http://uat.englishtown.com', 'https://smartuat2.englishtown.com/oboe2/', 'https://test.salesforce.com', 'et2', 'http://devcenter.ef.com.cn', 'http://cosam.englishtown.com/online/cn');
INSERT INTO environments (name, domain, replace_to, description, mark, etown_url, oboe_url, salesforce_url, tags, marketing_url, marketing_ts_url) VALUES ('QA', 'all', 'qa', 'QA', '', 'http://qa.englishtown.com', 'http://qaoboe.ef.com/oboe2/', 'https://test.salesforce.com', 'et2', 'http://qacenter.ef.com.cn', 'http://qa.englishtown.cn/online/cn');
INSERT INTO environments (name, domain, replace_to, description, mark, etown_url, oboe_url, salesforce_url, tags, marketing_url, marketing_ts_url) VALUES ('Staging', 'all', 'staging', 'Staging', '', 'http://staging.englishtown.com', 'http://stagingoboe.ef.com/oboe2/', 'https://test.salesforce.com', 'et2', 'http://stgcenter.ef.com.cn', 'http://stagingcn.englishtown.com/online/cn');
INSERT INTO environments (name, domain, replace_to, description, mark, etown_url, oboe_url, salesforce_url, tags, marketing_url, marketing_ts_url) VALUES ('Live', 'cn', 'cn1web1', 'LiveCN', 'livecn', 'http://cn1web1.englishtown.com', 'http://oboe.ef.cn/oboe2/', 'https://login.salesforce.com', 'et2', 'http://center.ef.com.cn', 'http://www.englishlive.cn/online/cn');
INSERT INTO environments (name, domain, replace_to, description, mark, etown_url, oboe_url, salesforce_url, tags, marketing_url, marketing_ts_url) VALUES ('Live', 'us', 'webus1', 'LiveUS', 'liveus', 'http://webus1.englishtown.com', 'http://oboe.ef.com/oboe2/', 'https://login.salesforce.com', 'et2', 'http://center.ef.com.cn', 'http://www.englishlive.cn/online/cn');

DROP TABLE IF EXISTS database;

CREATE TABLE "database" (
  name     TEXT,
  domain   TEXT,
  server   TEXT PRIMARY KEY,
  user     TEXT,
  password TEXT,
  tags     TEXT
);

INSERT INTO database (name, domain, server, user, password, tags) VALUES ('UAT', 'all', 'CNS-ETDEVDB', 'TestUser', 'testuserdev', '');
INSERT INTO database (name, domain, server, user, password, tags) VALUES ('QA', 'all', '10.162.102.73', 'TestUser', 'testuserqa', '');
INSERT INTO database (name, domain, server, user, password, tags) VALUES ('Staging', 'all', '10.162.106.91', 'tempuser', 'tempuserstg', '');
INSERT INTO database (name, domain, server, user, password, tags) VALUES ('Live', 'cn', '10.17.4.158', 'etownreader', 'fishing22', '');
INSERT INTO database (name, domain, server, user, password, tags) VALUES ('Live', 'us', '10.43.45.158', 'etownreader', 'fishing22', '');
INSERT INTO database (name, domain, server, user, password, tags) VALUES ('Staging', 'cn', '10.17.4.56', 'tempuser', 'tempuserstg', 'ignore');
INSERT INTO database (name, domain, server, user, password, tags) VALUES ('QA', 'cn', 'CT1-ETQACNDB', 'TestUser', 'testuserqa', 'ignore');
INSERT INTO database (name, domain, server, user, password, tags) VALUES ('UAT', 'cn', 'CNS-ETDEVCNDB', 'TestUser', 'testuserdev', 'ignore');

DROP TABLE IF EXISTS partners;

CREATE TABLE "partners" (
  name         TEXT PRIMARY KEY,
  domain       TEXT,
  country_code TEXT,
  tags         TEXT
);

INSERT INTO partners VALUES ('Cool', 'CN', 'cn', '');
INSERT INTO partners VALUES ('Mini', 'CN', 'cn', '');
INSERT INTO partners VALUES ('Rupe', 'US', 'ru', '');
INSERT INTO partners VALUES ('Indo', 'US', 'id', '');
INSERT INTO partners VALUES ('Ecsp', 'US', 'es', '');
INSERT INTO partners VALUES ('Cehk', 'US', 'hk', '');

DROP TABLE IF EXISTS products;

CREATE TABLE "products" (
  partner      TEXT,
  id           INTEGER PRIMARY KEY,
  name         TEXT,
  product_type TEXT,
  main_code    TEXT,
  main_one_day TEXT,
  free_code    TEXT,
  tags         TEXT
);

INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 9, 'Preminum 10', 'School', 'SMART3MONTHSCHOOL', '', 'SMART1DAYFREESCHOOL', 'E10');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Mini', 37, 'Private 24(School)with F2F', 'School', 'MiniPRIVATELC18775', '', 'privatefree1day18901', 'E10');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Rupe', 39, 'Interactive English Language Course', 'School', 'Rissiamain3Mschool', '', 'Russiafree1dayschool', 'E10');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Indo', 50, 'Smart English', 'School', 'IndoSMARTMAIN', '', 'IndoSMARTFREE', 'E10');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 63, 'Smart 15 - School', 'School', 'S15SCHOOLMAIN', 'S15SCHOOLM1D', 'S15SCHOOLF1D', 'Major default');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 64, 'Smart 15 - Home PL(20)', 'Home', 'S15HOMEPL20MAIN', 'S15HOMEPL20M1D', 'S15HOMEPL20F1D', 'Major');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Mini', 65, 'Smart 15 - School - Mini', 'School', 'S15SCHOOLMAIN', 'S15SCHOOLM1D', 'S15SCHOOLF1D', 'Major default');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Mini', 66, 'Smart 15 - Home PL(20) - Mini', 'Home', 'S15HOMEPL20MAIN', 'S15HOMEPL20M1D', 'S15HOMEPL20F1D', 'Major');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 67, 'Smart 15 - Home GL', 'Home', 'S15HOMEGLMAIN', 'S15HOMEGLM1D', 'S15HOMEGLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Mini', 68, 'Smart 15 - Home GL - Mini', 'Home', 'S15HOMEGLMAIN', 'S15HOMEGLM1D', 'S15HOMEGLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 69, 'Smart 15 - Home 7D + 7GL', 'Home', 'S15HOME7GLMAIN', 'S15HOME7GLM1D', 'S15HOME7GLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Mini', 70, 'Smart 15 - Home 7D + 7GL - Mini', 'Home', 'S15HOME7GLMAIN', 'S15HOME7GLM1D', 'S15HOME7GLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 71, 'Smart 15 - Home 7D + 7GL + 1PL(20)', 'Home', 'S15HOME7GLPLMAIN', 'S15HOME7GLPLM1D', 'S15HOME7GLPLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Mini', 72, 'Smart 15 - Home 7D + 7GL + 1PL(20) - Mini', 'Home', 'S15HOME7GLPLMAIN', 'S15HOME7GLPLM1D', 'S15HOME7GLPLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Rupe', 77, 'EF Interactive English Language 15', 'School', 'R15SCHOOLMAIN', 'R15SCHOOLM1D', 'R15SCHOOLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Rupe', 78, 'EF Home Product 15', 'Home', 'R15HOMEMAIN', 'R15HOMEM1D', 'R15HOMEF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Indo', 86, 'Smart English 15', 'School', 'I15SEMAIN', 'I15SEM1D', 'I15SEF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Indo', 87, 'Professional English 15', 'School', 'I15PEMAIN', 'I15PEM1D', 'I15PEF1D', 'Major default');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cehk', 97, 'Intensive PXLC', 'School', 'HKINTPXLCMAIN', '', 'HKINTPXLCMAIN1D', 'E10');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Rupe', 102, 'Exam Preparation 15', 'Home', 'R15EXAMPREMAIN', 'R15EXAMPREM1D', 'R15EXAMPREF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 111, 'Smart 15 - CS T1', 'School', 'S15CSMAIN', 'S15CSM1D', 'S15CSF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Mini', 112, 'Smart 15 - CS T2', 'School', 'S15CSMAIN', 'S15CSM1D', 'S15CSF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 118, 'Beginner Camp', 'Home', 'S15HOME7GLMAIN', 'S15HOME7GLM1D', 'S15HOME7GLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 119, 'Smart 15 - Home 7D + 1GL', 'Home', 'S15HOME71GLMAIN', 'S15HOME71GLM1D', 'S15HOME71GLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Mini', 120, 'Smart 15 - Home 7D + 1GL - Mini', 'Home', 'S15HOME71GLMAIN', 'S15HOME71GLM1D', 'S15HOME71GLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 122, 'Smart 15 - Alumni Product - Gold', 'School', 'S15ALUMNITPMAIN', 'S15ALUMNITPM1D', 'S15ALUMNITPF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 123, 'Smart 15 - Alumni Product - Silver', 'School', 'S15ALUMNITPMAIN', 'S15ALUMNITPM1D', 'S15ALUMNITPF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 125, 'Smart 15 - Home 5D', 'Home', 'S15HOME5MAIN', '', 'S15HOME5F1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Mini', 126, 'Smart 15 - Home 5D - Mini', 'Home', 'S15HOME5MAIN', '', 'S15HOME5F1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cehk', 127, 'Smart 15 - School - HK', 'School', 'HK15SCHOOLMAIN', 'HK15SCHOOLM1D', 'HK15SCHOOLF1D', 'Major default');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cehk', 128, 'Smart 15 - Home PL(20) - HK', 'Home', 'HK15HOMEPL20MAIN', 'HK15HOMEPL20M1D', 'HK15HOMEPL20F1D', 'Major');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cehk', 129, 'Smart 15 - Home GL - HK', 'Home', 'HK15HOMEGLMAIN', 'HK15HOMEGLM1D', 'HK15HOMEGLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cehk', 130, 'Smart 15 - Home OS - HK', 'Home', 'HK15HOMEOSMAIN', 'HK15HOMEOSM1D', 'HK15HOMEOSF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Rupe', 133, 'EF PL20 Smart 15 Home', 'Home', 'R15HOMEPL20MAIN', 'R15HOMEPL20M1D', 'R15HOMEPL20F1D', 'Major');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Rupe', 134, 'EF PL20 Interactive English Language 15', 'School', 'R15SCHOOLPL20MAIN', 'R15SCHOOLPL20M1D', 'R15SCHOOLPL20F1D', 'Major default');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Ecsp', 135, 'EF Smart 15 Spain', 'School', 'SPS15SCHOOLMAIN', 'SPS15SCHOOLM1D', 'SPS15SCHOOLF1D', 'Major default');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Ecsp', 136, 'EF Smart 15 Spain - Home', 'Home', 'SPS15HOMEMAIN', 'SPS15HOMEM1D', 'SPS15HOMEF1D', 'Major');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Ecsp', 139, 'EF Smart 15 Home 90D PL40', 'Home', 'SPS15HOME90PL40MAIN', 'SPS15HOME90PL40M1D', 'SPS15HOME90PL40F1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Rupe', 142, 'EF F2F/PL20 Interactive English Language 15', 'School', 'R15SCHOOLF2FPL20MAIN', 'R15SCHOOLF2FPL20M1D', 'R15SCHOOLF2FPL20F1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Mini', 143, 'Smart 15 - EC Lite', 'School', 'S15SCHOOLLTMAIN', 'S15SCHOOLLTM1D', 'S15SCHOOLLTF1D', 'ECLite');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Cool', 144, 'Smart 15 - Offpeak', 'School', 'S15SCHOOLMAIN', 'S15SCHOOLM1D', 'S15SCHOOLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Mini', 145, 'Smart 15 - Offpeak - Mini', 'School', 'S15SCHOOLMAIN', 'S15SCHOOLM1D', 'S15SCHOOLF1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Indo', 146, 'Smart English 15 - PL20', 'School', 'I15SEMAINPL20', 'I15SEMAINPL201D', 'I15SEPL20F1D', '');
INSERT INTO products (partner, id, name, product_type, main_code, main_one_day, free_code, tags) VALUES ('Indo', 147, 'Professional English 15 - PL20', 'School', 'I15PEMAINPL20', 'I15PEMAINPL201D', 'I15PEPL20F1D', '');

DROP TABLE IF EXISTS schools;

CREATE TABLE "schools" (
  id            INTEGER PRIMARY KEY,
  partner       TEXT,
  city          TEXT,
  name          TEXT,
  division_code TEXT,
  tags          TEXT
);

INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (-3, 'Cehk', 'Invalid', 'Invalid', 'Invalid_cehk', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (-2, 'Ecsp', 'Invalid', 'Invalid', 'Invalid_ecsp', 'S15_V1');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (-1, 'Indo', 'Invalid', 'Invalid', 'Invalid_indo', 'S15_V1');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (1, 'Cool', 'Shanghai', 'SH_PSQ', 'SSCNSH1', 'PC2.0 default');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (2, 'Cool', 'Shanghai', 'SH_XJH', 'SSCNSH3', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (6, 'Cool', 'Beijing', 'BJ_GM1', 'SSCNBJ2', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (7, 'Cool', 'Beijing', 'BJ_FXM', 'SSCNBJ3', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (8, 'Cool', 'Beijing', 'BJ_ZGC', 'SSCNBJ4', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (9, 'Cool', 'Shanghai', 'SH_ZSP', 'SSCNSH5', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (11, 'Cool', 'Beijing', 'BJ_DFG', 'SSCNBJ5', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (13, 'Cool', 'Guangzhou', 'GZ_THB', 'SSCNGZ2', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (14, 'Cool', 'ShenZhen', 'SZ_DWG', 'SSCNSZ1', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (15, 'Cool', 'Guangzhou', 'GZ_GYQ', 'SSCNGZ3', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (16, 'Cool', 'Shanghai', 'SH_WJC', 'SSCNSH6', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (18, 'Cool', 'TestCity', 'Tcenter(notselect)', 'SSCNTE1', 'PC2.0 TestCenter');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (19, 'Cool', 'Beijing', 'BJ_DZM', 'SSCNBJ6', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (20, 'Cool', 'Beijing', 'BJ_XZM', 'SSCNBJ7', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (21, 'Cool', 'Shanghai', 'SH_DNR', 'SSCNSH7', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (22, 'Cool', 'ShenZhen', 'SZ_NSD', 'SSCNSZ2', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (23, 'Cool', 'Beijing', 'BJ_SYQ', 'SSCNBJ8', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (24, 'Cool', 'ShenZhen', 'SZ_HQB', 'SSCNSZ3', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (26, 'Cool', 'Beijing', 'BJ_DWL', 'SSCNBJ9', 'PC2.0 OnlineOC');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (28, 'Cool', 'ShenZhen', 'SZ_CHC', 'SSCNSZ4', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (35, 'Cool', 'Guangzhou', 'GZ_JNX', 'SSCNGZ5', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (36, 'Cool', 'Shanghai', 'SH_XZG', 'SSCNSH9', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (39, 'Cool', 'Shanghai', 'SH_BBB', 'SSCNSH10', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (41, 'Cool', 'Beijing', 'BJ_YYC', 'SSCNBJ11', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (42, 'Cool', 'Guangzhou', 'GZ_WLH', 'SSCNGZ6', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (51, 'Cool', 'Beijing', 'BJ_WSL', 'SSCNBJ12', 'PC2.0 OnlineOC');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (52, 'Cool', 'Beijing', 'BJ_WDK', 'SSCNBJ13', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (53, 'Cool', 'ShenZhen', 'SZ_KJY', 'SSCNSZ5', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (54, 'Cool', 'Tianjin', 'TJ_NJR', 'SSCNTJ1', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (56, 'Cool', 'Hangzhou', 'HZ_HBC', 'SSCNHZ2', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (60, 'Cool', 'Hangzhou', 'HZ_CXC', 'SSCNHZ3', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (61, 'Cool', 'Hangzhou', 'HZ_WLC', 'SSCNHZ4', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (62, 'Cool', 'Hangzhou', 'HZ_BJC', 'SSCNHZ5', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (63, 'Cool', 'TestCity', 'TCenterS14_(DO_NOT_SELECT)', 'SSCNTE2', 'PC2.0 TestCenter');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (64, 'Mini', 'Mini Test City', 'TCenterS14_M_(DO_NOT_SELECT)', 'CNNMTE1', 'PC2.0 TestCenter');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (65, 'Cool', 'Guangzhou', 'GZ_PYC', 'SSCNGZ7', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (66, 'Mini', 'XiAn', 'XA_XZC', 'CNMNXA2', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (67, 'Mini', 'Wuhan', 'WH_TDC', 'CNMNWH2', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (68, 'Cool', 'Hangzhou', 'HZ_XXC', 'SSCNHZ6', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (69, 'Mini', 'Wuhan', 'WH_ZNC', 'CNMNWH3', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (70, 'Mini', 'ChengDu', 'CD_MCC', 'CNMNCD3', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (71, 'Cool', 'Shanghai', 'SH_JAT', 'SSCNSH14', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (72, 'Cool', 'Guangzhou', 'GZ_GTC', 'SSCNGZ8', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (73, 'Mini', 'ChengDu', 'CD_YTC', 'CNMNCD6', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (74, 'Mini', 'ChengDu', 'CD_SNI', 'CNMNCD7', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (102, 'Mini', 'Wuxi', 'WX_HDP', 'CNMNWX1', 'PC2.0 OnlineOC');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (103, 'Mini', 'FoShan', 'FS_ZUM', 'CNMNFS1', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (104, 'Mini', 'ChengDu', 'CD_TFG', 'CNMNCD1', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (112, 'Mini', 'DongGuan', 'DG_NCH', 'CNMNDG1', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (114, 'Mini', 'Ningbo', 'NB_MLC', 'CNMNNB1', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (116, 'Mini', 'Mini Test City', 'Mini_Test', 'CNMNNJTE', 'TestCenter OnlineOC');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (117, 'Mini', 'Nanjing', 'NJ_IST', 'CNMNNJ2', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (119, 'Mini', 'ChongQing', 'CQ_GYQ', 'CNMNCQ1', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (121, 'Mini', 'XiAn', 'XA_XGX', 'CNMNXA1', 'default PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (140, 'Mini', 'ChengDu', 'CD_LFS', 'CNMNCD2', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (141, 'Mini', 'Nanjing', 'NJ_HSH', 'CNMNNJ3', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (142, 'Mini', 'ChengDu', 'CD_KJN', 'CNMNCD4', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (143, 'Mini', 'ChengDu', 'CD_KTF', 'CNMNCD5', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (144, 'Mini', 'Suzhou', 'SU_JHC', 'CNMNSU1', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (147, 'Cool', 'Shanghai', 'SH_ZJC', 'SSCNSH15', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (148, 'Mini', 'Nanjing', 'NJ_WDC', 'CNMNNJ4', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (902, 'Cehk', 'HongKong', 'HK_WHC', 'HKWHC', '');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (903, 'Cehk', 'HongKong', 'HK_MKC', 'HKMKC', '');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (904, 'Cehk', 'HongKong', 'HK_TWC', 'HKTWC', '');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (906, 'Cehk', 'HongKong', 'HK_KTC', 'HKKTC', '');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (907, 'Cehk', 'Hong Kong Test City', 'Test(CEF)', 'CEF', 'TestCenter');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (908, 'Cehk', 'Hong Kong Test City', 'CWB(TEST01)', 'HKTEST1', 'TestCenter');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (912, 'Cehk', 'HongKong', 'HK_SSC', 'HKSSC', 'default');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (913, 'Cehk', 'HongKong', 'HK_YLC', 'HKYLC', '');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (1012, 'Rupe', 'St. Petersburg', 'SP_NEV', 'SNI', '');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (1013, 'Rupe', 'Kazan', 'KA_KAZ', 'KAA', '');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (1017, 'Rupe', 'Russia Test City', 'Russia_Test', 'RUPE', 'PC2.0 TestCenter');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (1019, 'Rupe', 'Moscow', 'MO_TVE', 'TVE', 'default TestCenter');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (1021, 'Rupe', 'Moscow', 'MO_KUR', 'KUR', '');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (1026, 'Rupe', 'Moscow', 'MO_PAR', 'PAR', '');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (1027, 'Rupe', 'Novosibirsk', 'NS_LEN', 'LEN', '');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (1029, 'Rupe', 'St. Petersburg', 'SP_TEK', 'TEK', '');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (2001, 'Indo', 'Jakarta', 'JK_SUD', 'INDO1', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (2011, 'Indo', 'Indo Test City', 'IndonesiaTestCenter', 'INDOTEST', 'PC2.0 TestCenter');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (2015, 'Indo', 'Jakarta', 'JK_MTA', 'INDO2', 'default PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (2016, 'Indo', 'Jakarta', 'JK_KUN', 'INDO3', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (2017, 'Indo', 'Surabaya', 'SU_TOS', 'INDO4', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (2019, 'Indo', 'Jakarta', 'JK_PLZ', 'INDO5', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (2020, 'Mini', 'Wuhan_Lite', 'WH_GGC', 'CNMNWH5', 'PC2.0 ECLite');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (3004, 'Ecsp', 'Madrid', 'MD_MDM', 'SPMD1', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (3005, 'Ecsp', 'Barcelona', 'BC_BLM', 'SPBC1', 'default TestCenter PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (3006, 'Ecsp', 'Spain Test City', 'Spain_TestCenter', 'SPTE1', 'PC2.0 TestCenter');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (3011, 'Mini', 'Wuhan_Lite', 'WH_LITE', 'CNMNWH4', 'PC2.0 ECLite TestCenter');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (3012, 'Cool', 'ShenZhen', 'SZ_CBD', 'SSCNSZ6', 'PC2.0');
INSERT INTO schools (id, partner, city, name, division_code, tags) VALUES (241620, 'Cool', 'TestCity', 'BJ_Testing_Center', 'TEST', 'TestCenter OnlineOC');

CREATE TABLE IF NOT EXISTS test_accounts (
  environment TEXT NOT NULL,
  member_id   INT  NOT NULL,
  username    TEXT,
  detail      TEXT,
  created_on  TEXT,
  created_by  TEXT,
  tags        TEXT
);

CREATE TABLE IF NOT EXISTS suspend_info (
  member_id           TEXT,
  suspend_date        TEXT,
  resume_date         TEXT,
  suspend_external_id TEXT
)