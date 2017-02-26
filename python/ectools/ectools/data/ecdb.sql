DROP TABLE IF EXISTS environment;

CREATE TABLE environment
(
    name TEXT,
    domain TEXT,
    replace_to TEXT,
    description TEXT,
    mark TEXT,
    etown_url TEXT,
    oboe_url TEXT,
    salesforce_url TEXT
);

INSERT INTO environment VALUES ('UAT', 'all', 'uat', 'UAT', '', 'http://uat.englishtown.com', 'http://uatoboe.ef.com/oboe2/', 'https://test.salesforce.com');
INSERT INTO environment VALUES ('QA', 'all', 'qa', 'QA', '', 'http://qa.englishtown.com', 'http://qaoboe.ef.com/oboe2/', 'https://test.salesforce.com');
INSERT INTO environment VALUES ('Staging', 'all', 'staging', 'Staging', '', 'http://staging.englishtown.com', 'http://stagingoboe.ef.com/oboe2/', 'https://test.salesforce.com');
INSERT INTO environment VALUES ('Live', 'cn', 'cn1web1', 'LiveCN', 'livecn', 'http://cn1web1.englishtown.com', 'http://oboecn.ef.com/oboe2/', 'https://login.salesforce.com');
INSERT INTO environment VALUES ('Live', 'us', 'webus1', 'LiveUS', 'liveus', 'http://webus1.englishtown.com', 'http://oboeus.ef.com/oboe2', 'https://login.salesforce.com');

DROP TABLE IF EXISTS database;

CREATE TABLE database
(
    env TEXT,
    domain TEXT,
    server TEXT,
    user TEXT,
    password TEXT
);

INSERT INTO database VALUES ('UAT', 'all', 'CNS-ETDEVDB', 'TestUser', 'testuserdev');
INSERT INTO database VALUES ('QA', 'all', 'USB-ETOWNQADB', 'TestUser', 'testuserqa');
INSERT INTO database VALUES ('Staging', 'all', '10.43.45.180', 'etownreader', 'fishing22');
INSERT INTO database VALUES ('Live', 'cn', '10.17.4.158', 'etownreader', 'fishing22');
INSERT INTO database VALUES ('Live', 'us', '10.43.45.158', 'etownreader', 'fishing22');

DROP TABLE IF EXISTS partner;

CREATE TABLE partner
(
    name TEXT,
    domain TEXT,
    country_code TEXT
);

INSERT INTO partner VALUES ('Cool', 'CN', 'cn');
INSERT INTO partner VALUES ('Mini', 'CN', 'cn');
INSERT INTO partner VALUES ('Rupe', 'US', 'ru');
INSERT INTO partner VALUES ('Indo', 'US', 'id');
INSERT INTO partner VALUES ('Ecsp', 'US', 'es');
INSERT INTO partner VALUES ('Cehk', 'US', 'hk');

DROP TABLE IF EXISTS product;

CREATE TABLE product
(
    partner TEXT,
    id INTEGER,
    name TEXT,
    product_type TEXT,
    main_code TEXT,
    main_one_day TEXT,
    free_code TEXT,
    tags TEXT
);

INSERT INTO product VALUES ('Cool', 63, 'Smart 15 - School', 'School', 'S15SCHOOLMAIN', 'S15SCHOOLM1D', 'S15SCHOOLF1D', 'Major');
INSERT INTO product VALUES ('Cool', 64, 'Smart 15 - Home PL(20)', 'Home', 'S15HOMEPL20MAIN', 'S15HOMEPL20M1D', 'S15HOMEPL20F1D', 'Major');
INSERT INTO product VALUES ('Mini', 65, 'Smart 15 - School - Mini', 'School', 'S15SCHOOLMAIN', 'S15SCHOOLM1D', 'S15SCHOOLF1D', 'Major');
INSERT INTO product VALUES ('Mini', 66, 'Smart 15 - Home PL(20) - Mini', 'Home', 'S15HOMEPL20MAIN', 'S15HOMEPL20M1D', 'S15HOMEPL20F1D', 'Major');
INSERT INTO product VALUES ('Cool', 67, 'Smart 15 - Home GL', 'Home', 'S15HOMEGLMAIN', 'S15HOMEGLM1D', 'S15HOMEGLF1D', '');
INSERT INTO product VALUES ('Mini', 68, 'Smart 15 - Home GL - Mini', 'Home', 'S15HOMEGLMAIN', 'S15HOMEGLM1D', 'S15HOMEGLF1D', '');
INSERT INTO product VALUES ('Cool', 69, 'Smart 15 - Home 7D + 7GL', 'Home', 'S15HOME7GLMAIN', 'S15HOME7GLM1D', 'S15HOME7GLF1D', '');
INSERT INTO product VALUES ('Mini', 70, 'Smart 15 - Home 7D + 7GL - Mini', 'Home', 'S15HOME7GLMAIN', 'S15HOME7GLM1D', 'S15HOME7GLF1D', '');
INSERT INTO product VALUES ('Cool', 71, 'Smart 15 - Home 7D + 7GL + 1PL(20)', 'Home', 'S15HOME7GLPLMAIN', 'S15HOME7GLPLM1D', 'S15HOME7GLPLF1D', '');
INSERT INTO product VALUES ('Mini', 72, 'Smart 15 - Home 7D + 7GL + 1PL(20) - Mini', 'Home', 'S15HOME7GLPLMAIN', 'S15HOME7GLPLM1D', 'S15HOME7GLPLF1D', '');
INSERT INTO product VALUES ('Rupe', 77, 'EF Interactive English Language 15', 'School', 'R15SCHOOLMAIN', 'R15SCHOOLM1D', 'R15SCHOOLF1D', '');
INSERT INTO product VALUES ('Rupe', 78, 'EF Home Product 15', 'Home', 'R15HOMEMAIN', 'R15HOMEM1D', 'R15HOMEF1D', '');
INSERT INTO product VALUES ('Indo', 86, 'Smart English 15', 'School', 'I15SEMAIN', 'I15SEM1D', 'I15SEF1D', '');
INSERT INTO product VALUES ('Indo', 87, 'Professional English 15', 'School', 'I15PEMAIN', 'I15PEM1D', 'I15PEF1D', 'Major');
INSERT INTO product VALUES ('Rupe', 102, 'Exam Preparation 15', 'Home', 'R15EXAMPREMAIN', 'R15EXAMPREM1D', 'R15EXAMPREF1D', '');
INSERT INTO product VALUES ('Cool', 111, 'Smart 15 - CS T1', 'School', 'S15CSMAIN', 'S15CSM1D', 'S15CSF1D', '');
INSERT INTO product VALUES ('Mini', 112, 'Smart 15 - CS T2', 'School', 'S15CSMAIN', 'S15CSM1D', 'S15CSF1D', '');
INSERT INTO product VALUES ('Cool', 118, 'Beginner Camp', 'Home', 'S15HOME7GLMAIN', 'S15HOME7GLM1D', 'S15HOME7GLF1D', '');
INSERT INTO product VALUES ('Cool', 119, 'Smart 15 - Home 7D + 1GL', 'Home', 'S15HOME71GLMAIN', 'S15HOME71GLM1D', 'S15HOME71GLF1D', '');
INSERT INTO product VALUES ('Mini', 120, 'Smart 15 - Home 7D + 1GL - Mini', 'Home', 'S15HOME71GLMAIN', 'S15HOME71GLM1D', 'S15HOME71GLF1D', '');
INSERT INTO product VALUES ('Cool', 122, 'Smart 15 - Alumni Product - Gold', 'School', 'S15ALUMNITPMAIN', 'S15ALUMNITPM1D', 'S15ALUMNITPF1D', '');
INSERT INTO product VALUES ('Cool', 123, 'Smart 15 - Alumni Product - Silver', 'School', 'S15ALUMNITPMAIN', 'S15ALUMNITPM1D', 'S15ALUMNITPF1D', '');
INSERT INTO product VALUES ('Cool', 125, 'Smart 15 - Home 5D', 'Home', 'S15HOME5MAIN', '', 'S15HOME5F1D', '');
INSERT INTO product VALUES ('Mini', 126, 'Smart 15 - Home 5D - Mini', 'Home', 'S15HOME5MAIN', '', 'S15HOME5F1D', '');
INSERT INTO product VALUES ('Cehk', 127, 'Smart 15 - School - HK', 'School', 'HK15SCHOOLMAIN', 'HK15SCHOOLM1D', 'HK15SCHOOLF1D', 'Major');
INSERT INTO product VALUES ('Cehk', 128, 'Smart 15 - Home PL(20) - HK', 'Home', 'HK15HOMEPL20MAIN', 'HK15HOMEPL20M1D', 'HK15HOMEPL20F1D', 'Major');
INSERT INTO product VALUES ('Cehk', 129, 'Smart 15 - Home GL - HK', 'Home', 'HK15HOMEGLMAIN', 'HK15HOMEGLM1D', 'HK15HOMEGLF1D', '');
INSERT INTO product VALUES ('Cehk', 130, 'Smart 15 - Home OS - HK', 'Home', 'HK15HOMEOSMAIN', 'HK15HOMEOSM1D', 'HK15HOMEOSF1D', '');
INSERT INTO product VALUES ('Rupe', 133, 'EF PL20 Smart 15 Home', 'Home', 'R15HOMEPL20MAIN', 'R15HOMEPL20M1D', 'R15HOMEPL20F1D', 'Major');
INSERT INTO product VALUES ('Rupe', 134, 'EF PL20 Interactive English Language 15', 'School', 'R15SCHOOLPL20MAIN', 'R15SCHOOLPL20M1D', 'R15SCHOOLPL20F1D', 'Major');
INSERT INTO product VALUES ('Ecsp', 135, 'EF Smart 15 Spain', 'School', 'SPS15SCHOOLMAIN', 'SPS15SCHOOLM1D', 'SPS15SCHOOLF1D', 'Major');
INSERT INTO product VALUES ('Ecsp', 136, 'EF Smart 15 Spain - Home', 'Home', 'SPS15HOMEMAIN', 'SPS15HOMEM1D', 'SPS15HOMEF1D', 'Major');
INSERT INTO product VALUES ('Ecsp', 139, 'EF Smart 15 Home 90D PL40', 'Home', 'SPS15HOME90PL40MAIN', 'SPS15HOME90PL40M1D', 'SPS15HOME90PL40F1D', '');
INSERT INTO product VALUES ('Cool', 9, 'Preminum 10', 'School', 'SMART3MONTHSCHOOL', '', 'SMART1DAYFREESCHOOL', 'E10');
INSERT INTO product VALUES ('Mini', 37, 'Private 24(School)with F2F', 'School', 'MiniPRIVATELC18775', '', 'privatefree1day18901', 'E10');
INSERT INTO product VALUES ('Cehk', 97, 'Intensive PXLC', 'School', 'HKINTPXLCMAIN', '', 'HKINTPXLCMAIN1D', 'E10');
INSERT INTO product VALUES ('Rupe', 39, 'Interactive English Language Course', 'School', 'Rissiamain3Mschool', '', 'Russiafree1dayschool', 'E10');
INSERT INTO product VALUES ('Indo', 50, 'Smart English', 'School', 'IndoSMARTMAIN', '', 'IndoSMARTFREE', 'E10');

DROP TABLE IF EXISTS school;

CREATE TABLE school
(
    partner TEXT,
    city TEXT,
    name TEXT,
    division_code TEXT,
    tags TEXT
);

INSERT INTO school VALUES ('Cehk', 'Hong Kong Test City', 'Test(CEF)', 'CEF', 'TestCenter');
INSERT INTO school VALUES ('Cehk', 'Hong Kong Test City', 'CWB(TEST01)', 'HKTEST1', 'TestCenter');
INSERT INTO school VALUES ('Cehk', 'HongKong', 'HK_SSC', 'HKSSC', '');
INSERT INTO school VALUES ('Cehk', 'HongKong', 'HK_YLC', 'HKYLC', '');
INSERT INTO school VALUES ('Cehk', 'HongKong', 'HK_SS2', 'HKSS2', '');
INSERT INTO school VALUES ('Cehk', 'HongKong', 'HK_TSQ', 'HKTSQ', '');
INSERT INTO school VALUES ('Cehk', 'HongKong', 'HK_WHC', 'HKWHC', '');
INSERT INTO school VALUES ('Cehk', 'HongKong', 'HK_MKC', 'HKMKC', '');
INSERT INTO school VALUES ('Cehk', 'HongKong', 'HK_TWC', 'HKTWC', '');
INSERT INTO school VALUES ('Cehk', 'HongKong', 'HK_KTC', 'HKKTC', '');
INSERT INTO school VALUES ('Cool', 'Beijing', 'BJ_GM1', 'SSCNBJ2', '');
INSERT INTO school VALUES ('Cool', 'Beijing', 'BJ_FXM', 'SSCNBJ3', '');
INSERT INTO school VALUES ('Cool', 'Beijing', 'BJ_ZGC', 'SSCNBJ4', '');
INSERT INTO school VALUES ('Cool', 'Beijing', 'BJ_DFG', 'SSCNBJ5', '');
INSERT INTO school VALUES ('Cool', 'Beijing', 'BJ_DZM', 'SSCNBJ6', '');
INSERT INTO school VALUES ('Cool', 'Beijing', 'BJ_XZM', 'SSCNBJ7', '');
INSERT INTO school VALUES ('Cool', 'Beijing', 'BJ_SYQ', 'SSCNBJ8', 'PC2.0');
INSERT INTO school VALUES ('Cool', 'Beijing', 'BJ_DWL', 'SSCNBJ9', '');
INSERT INTO school VALUES ('Cool', 'Beijing', 'BJ_WSL', 'SSCNBJ12', 'PC2.0');
INSERT INTO school VALUES ('Cool', 'Beijing', 'BJ_WDK', 'SSCNBJ13', '');
INSERT INTO school VALUES ('Cool', 'Beijing', 'BJ_YYC', 'SSCNBJ11', '');
INSERT INTO school VALUES ('Cool', 'Guangzhou', 'GZ_WLH', 'SSCNGZ6', '');
INSERT INTO school VALUES ('Cool', 'Guangzhou', 'GZ_PYC', 'SSCNGZ7', '');
INSERT INTO school VALUES ('Cool', 'Guangzhou', 'GZ_JNX', 'SSCNGZ5', 'PC2.0');
INSERT INTO school VALUES ('Cool', 'Guangzhou', 'GZ_GYQ', 'SSCNGZ3', '');
INSERT INTO school VALUES ('Cool', 'Guangzhou', 'GZ_THB', 'SSCNGZ2', '');
INSERT INTO school VALUES ('Cool', 'Guangzhou', 'GZ_GTC', 'SSCNGZ8', '');
INSERT INTO school VALUES ('Cool', 'Hangzhou', 'HZ_XXC', 'SSCNHZ6', '');
INSERT INTO school VALUES ('Cool', 'Hangzhou', 'HZ_HBC', 'SSCNHZ2', '');
INSERT INTO school VALUES ('Cool', 'Hangzhou', 'HZ_CXC', 'SSCNHZ3', '');
INSERT INTO school VALUES ('Cool', 'Hangzhou', 'HZ_WLC', 'SSCNHZ4', '');
INSERT INTO school VALUES ('Cool', 'Hangzhou', 'HZ_BJC', 'SSCNHZ5', '');
INSERT INTO school VALUES ('Cool', 'Shanghai', 'SH_XZG', 'SSCNSH9', '');
INSERT INTO school VALUES ('Cool', 'Shanghai', 'SH_BBB', 'SSCNSH10', '');
INSERT INTO school VALUES ('Cool', 'Shanghai', 'SH_PSQ', 'SSCNSH1', '');
INSERT INTO school VALUES ('Cool', 'Shanghai', 'SH_XJH', 'SSCNSH3', '');
INSERT INTO school VALUES ('Cool', 'Shanghai', 'SH_ZSP', 'SSCNSH5', 'PC2.0');
INSERT INTO school VALUES ('Cool', 'Shanghai', 'SH_WJC', 'SSCNSH6', '');
INSERT INTO school VALUES ('Cool', 'Shanghai', 'SH_DNR', 'SSCNSH7', '');
INSERT INTO school VALUES ('Cool', 'Shanghai', 'SH_JAT', 'SSCNSH14', 'PC2.0');
INSERT INTO school VALUES ('Cool', 'Shanghai', 'SH_ZJC', 'SSCNSH15', 'PC2.0');
INSERT INTO school VALUES ('Cool', 'ShenZhen', 'SZ_NSD', 'SSCNSZ2', '');
INSERT INTO school VALUES ('Cool', 'ShenZhen', 'SZ_HQB', 'SSCNSZ3', '');
INSERT INTO school VALUES ('Cool', 'ShenZhen', 'SZ_DWG', 'SSCNSZ1', '');
INSERT INTO school VALUES ('Cool', 'ShenZhen', 'SZ_CHC', 'SSCNSZ4', '');
INSERT INTO school VALUES ('Cool', 'ShenZhen', 'SZ_KJY', 'SSCNSZ5', '');
INSERT INTO school VALUES ('Cool', 'TestCity', 'Tcenter(notselect)', 'SSCNTE1', 'TestCenter');
INSERT INTO school VALUES ('Cool', 'TestCity', 'BJ_Testing_Center', 'TEST', 'TestCenter');
INSERT INTO school VALUES ('Cool', 'TestCity', 'TCenterS14_(DO_NOT_SELECT)', 'SSCNTE2', 'TestCenter PC2.0');
INSERT INTO school VALUES ('Cool', 'Tianjin', 'TJ_NJR', 'SSCNTJ1', '');
INSERT INTO school VALUES ('Ecsp', 'Barcelona', 'BC_BLM', 'SPBC1', '');
INSERT INTO school VALUES ('Ecsp', 'Madrid', 'MD_MDM', 'SPMD1', '');
INSERT INTO school VALUES ('Ecsp', 'Spain Test City', 'Spain_TestCenter', 'SPTE1', 'TestCenter PC2.0');
INSERT INTO school VALUES ('Indo', 'Indo Test City', 'IndonesiaTestCenter', 'IndoTEST', 'TestCenter PC2.0');
INSERT INTO school VALUES ('Indo', 'Jakarta', 'JK_MTA', 'Indo2', '');
INSERT INTO school VALUES ('Indo', 'Jakarta', 'JK_KUN', 'Indo3', '');
INSERT INTO school VALUES ('Indo', 'Jakarta', 'JK_PLZ', 'Indo5', '');
INSERT INTO school VALUES ('Indo', 'Jakarta', 'JK_SUD', 'Indo1', '');
INSERT INTO school VALUES ('Indo', 'Surabaya', 'SU_TOS', 'Indo4', '');
INSERT INTO school VALUES ('Mini', 'ChengDu', 'CD_TFG', 'CNMNCD1', '');
INSERT INTO school VALUES ('Mini', 'ChengDu', 'CD_MCC', 'CNMNCD3', '');
INSERT INTO school VALUES ('Mini', 'ChengDu', 'CD_YTC', 'CNMNCD6', '');
INSERT INTO school VALUES ('Mini', 'ChengDu', 'CD_SNI', 'CNMNCD7', '');
INSERT INTO school VALUES ('Mini', 'ChengDu', 'CD_LFS', 'CNMNCD2', '');
INSERT INTO school VALUES ('Mini', 'ChengDu', 'CD_KJN', 'CNMNCD4', '');
INSERT INTO school VALUES ('Mini', 'ChengDu', 'CD_KTF', 'CNMNCD5', 'PC2.0');
INSERT INTO school VALUES ('Mini', 'ChongQing', 'CQ_GYQ', 'CNMNCQ1', '');
INSERT INTO school VALUES ('Mini', 'DongGuan', 'DG_NCH', 'CNMNDG1', '');
INSERT INTO school VALUES ('Mini', 'FoShan', 'FS_ZUM', 'CNMNFS1', 'PC2.0');
INSERT INTO school VALUES ('Mini', 'Mini Test City', 'Mini_Test', 'CNMNNJTE', 'TestCenter');
INSERT INTO school VALUES ('Mini', 'Mini Test City', 'TCenterS14_M_(DO_NOT_SELECT)', 'CNNMTE1', 'TestCenter PC2.0');
INSERT INTO school VALUES ('Mini', 'Nanjing', 'NJ_IST', 'CNMNNJ2', '');
INSERT INTO school VALUES ('Mini', 'Nanjing', 'NJ_HSH', 'CNMNNJ3', 'PC2.0');
INSERT INTO school VALUES ('Mini', 'Ningbo', 'NB_MLC', 'CNMNNB1', 'PC2.0');
INSERT INTO school VALUES ('Mini', 'Suzhou', 'SU_JHC', 'CNMNSU1', '');
INSERT INTO school VALUES ('Mini', 'Wuhan', 'WH_TDC', 'CNMNWH2', '');
INSERT INTO school VALUES ('Mini', 'Wuhan', 'WH_ZNC', 'CNMNWH3', '');
INSERT INTO school VALUES ('Mini', 'Wuxi', 'WX_HDP', 'CNMNWX1', '');
INSERT INTO school VALUES ('Mini', 'XiAn', 'XA_XGX', 'CNMNXA1', 'PC2.0');
INSERT INTO school VALUES ('Mini', 'XiAn', 'XA_XZC', 'CNMNXA2', '');
INSERT INTO school VALUES ('Rupe', 'Kazan', 'KA_KAZ', 'KAA', '');
INSERT INTO school VALUES ('Rupe', 'Moscow', 'MO_TVE', 'TVE', '');
INSERT INTO school VALUES ('Rupe', 'Moscow', 'MO_KUR', 'KUR', '');
INSERT INTO school VALUES ('Rupe', 'Moscow', 'MO_PAR', 'PAR', '');
INSERT INTO school VALUES ('Rupe', 'Novosibirsk', 'NS_LEN', 'LEN', '');
INSERT INTO school VALUES ('Rupe', 'Russia Test City', 'Russia_Test', 'Rupe', 'TestCenter PC2.0');
INSERT INTO school VALUES ('Rupe', 'St. Petersburg', 'SP_NEV', 'SNI', '');
INSERT INTO school VALUES ('Rupe', 'St. Petersburg', 'SP_TEK', 'TEK', '');
