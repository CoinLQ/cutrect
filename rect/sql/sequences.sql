DROP SEQUENCE IF EXISTS task_seq;
CREATE SEQUENCE task_seq
        INCREMENT 1
        MINVALUE 1
        MAXVALUE 999999
        START 1
        CACHE 1
        CYCLE;


