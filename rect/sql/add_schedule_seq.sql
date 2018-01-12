CREATE SEQUENCE schedule_seq
        INCREMENT 1
        MINVALUE 1
        MAXVALUE 999
        START 1
        CACHE 1
        CYCLE;

CREATE or REPLACE FUNCTION fn_schedule_seq() RETURNS trigger AS $fn_schedule_seq$
BEGIN NEW.schedule_no := 'P'||to_char(now(),'YYYYMMDD')||lpad(nextval('schedule_seq')::char, 3, '0');
RETURN NEW;
END;
$fn_schedule_seq$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS cc_schedule_seq ON rect_schedule;
CREATE TRIGGER cc_schedule_seq
    BEFORE INSERT ON rect_schedule
            FOR EACH ROW
            EXECUTE PROCEDURE fn_schedule_seq();

DROP TRIGGER IF EXISTS cc_task_seq ON rect_cctask;
DROP TRIGGER IF EXISTS cs_task_seq ON rect_classifytask;
DROP TRIGGER IF EXISTS rp_task_seq ON rect_pagetask;
DROP TRIGGER IF EXISTS ab_task_seq ON rect_absenttask;
DROP TRIGGER IF EXISTS dl_task_seq ON rect_deltask;
DROP TRIGGER IF EXISTS rv_task_seq ON rect_reviewtask;