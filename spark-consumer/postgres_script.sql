
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