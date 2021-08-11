
\c meetup

DROP TABLE IF EXISTS MEETUP_RSVP;

CREATE TABLE MEETUP_RSVP(
    sequence_no  SERIAL NOT NULL PRIMARY KEY,
    group_name varchar(1000) NULL,
    group_country varchar(100) NULL,
    group_state varchar(100) NULL,
    group_city varchar(100) NULL,
    group_lat NUMERIC NULL,
    group_lon NUMERIC NULL,
    response varchar(10) NULL,
    response_count BIGINT NOT NULL,
    batch_id BIGINT NULL
);

-- For event url table 
CREATE TABLE MEETUP_TABLE(
    sequence_no  SERIAL NOT NULL PRIMARY KEY,
    event_name TEXT NULL,
    event_url TEXT NULL,
    event_time varchar(20) NULL,
    group_name varchar(1000) NULL,
    group_country varchar(20) NULL,
    group_state varchar(100) NULL,
    group_city varchar(100) NULL,
    group_lat NUMERIC NULL,
    group_lon NUMERIC NULL,
    lat NUMERIC NULL,
    lon NUMERIC NULL,
    response varchar(10) NULL,
    response_count BIGINT NOT NULL,
    batch_id BIGINT NULL
);



-- for table with : group_name, num_yes , Num_no, lat, lon


select group_name,sum(case when response='yes' then 1 else 0 end) as response_yes, sum(case when response='no' then 1 else 0 end) as response_no,group_lat, group_lon from MEETUP_RSVP group by group_name,group_lat, group_lon; 