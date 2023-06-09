--------------------------------------------------------
--  DDL for Table MEMBER
--------------------------------------------------------
 CREATE TABLE "GROUP7"."MEMBER" 
    (	
    "MID" VARCHAR2(20) NOT NULL, 
    "NAME" VARCHAR2(20), 
    "ACCOUNT"  VARCHAR2(20),
    "PASSWORD" VARCHAR2(20),
    "IDENTITY" VARCHAR2(20) NOT NULL,
    PRIMARY KEY("MID")
    ) ;

--------------------------------------------------------
--  DDL for Table THEME
--------------------------------------------------------
 CREATE TABLE "GROUP7"."THEME" 
    (	
    "THEMEID" VARCHAR2(20) NOT NULL, 
    "TNAME" VARCHAR2(50), 
    PRIMARY KEY("THEMEID")
    ) ;

--------------------------------------------------------
--  DDL for Table CATEGORIS
--------------------------------------------------------
 CREATE TABLE "GROUP7"."CATEGORIS" 
    (	
    "CATEGORYID" VARCHAR2(20) NOT NULL, 
    "CNAME" VARCHAR2(50), 
    PRIMARY KEY("CATEGORYID")
    ) ;

--------------------------------------------------------
--  DDL for Table BOOKS
--------------------------------------------------------
 CREATE TABLE "GROUP7"."BOOKS" 
    (	
    "BID" VARCHAR2(20) NOT NULL, 
    "BNAME" VARCHAR2(20), 
    "PRESS" VARCHAR2(20),
    "PDATE" DATE,
    "IDATE" DATE,
    "AUTHOR" VARCHAR2(50),
    "THEMEID" VARCHAR2(20),
    "CATEGORYID" VARCHAR2(20),
    PRIMARY KEY("BID"),
    FOREIGN KEY("THEMEID") REFERENCES "GROUP7"."THEME"("THEMEID"),
    FOREIGN KEY("CATEGORYID") REFERENCES "GROUP7"."CATEGORIS"("CATEGORYID")
    ) ;

--------------------------------------------------------
--  DDL for Table BORROWINGRECORDS
--------------------------------------------------------
 CREATE TABLE "GROUP7"."BORROWINGRECORDS" 
    (	
    "MID" VARCHAR2(20) NOT NULL,
    "BID" VARCHAR2(20) NOT NULL,
    "BORROWDATE" Date NOT NULL,
    "RETURNDATE" Date, 
    "LIMITDATE" Date,
    PRIMARY KEY("MID", "BID", "BORROWDATE"),
    FOREIGN KEY("MID") REFERENCES "GROUP7"."MEMBER"("MID"),
    FOREIGN KEY("BID") REFERENCES "GROUP7"."BOOKS"("BID")
    ) ;

--------------------------------------------------------
--  DDL for Table RESERVATIONRECORDS
--------------------------------------------------------
 CREATE TABLE "GROUP7"."RESERVATIONRECORDS" 
    (	
    "MID" VARCHAR2(20) NOT NULL,
    "BID" VARCHAR2(20) NOT NULL,
    "RESERVEDATE" Date NOT NULL,
    "RESERVESTUS" VARCHAR2(1), 
    PRIMARY KEY("MID", "BID", "RESERVEDATE"),
    FOREIGN KEY("MID") REFERENCES "GROUP7"."MEMBER"("MID"),
    FOREIGN KEY("BID") REFERENCES "GROUP7"."BOOKS"("BID")
    ) ;

--------------------------------------------------------
--  DDL for Table REVIEWS
--------------------------------------------------------
 CREATE TABLE "GROUP7"."REVIEWS" 
    (	
    "MID" VARCHAR2(20) NOT NULL,
    "BID" VARCHAR2(20) NOT NULL,
    "REVIEWSTIME" Date NOT NULL,
    "CONTENT" VARCHAR2(1000), 
    "STAR" NUMBER(5), 
    PRIMARY KEY("MID", "BID", "REVIEWSTIME"),
    FOREIGN KEY("MID") REFERENCES "GROUP7"."MEMBER"("MID"),
    FOREIGN KEY("BID") REFERENCES "GROUP7"."BOOKS"("BID")
    ) ;

--------------------------------------------------------
--  DDL for Table RECOMMENDATION
--------------------------------------------------------
 CREATE TABLE "GROUP7"."RECOMMENDATION" 
    (	
    "R_ISBN" VARCHAR2(50) NOT NULL, 
    "R_BNAME" VARCHAR2(50), 
    "MID" VARCHAR2(20), 
    PRIMARY KEY("R_ISBN"),
    FOREIGN KEY("MID") REFERENCES "GROUP7"."MEMBER"("MID")
    ) ;