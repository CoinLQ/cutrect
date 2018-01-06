CREATE or REPLACE FUNCTION fn_task_seq() RETURNS trigger AS $fn_task_seq$
BEGIN NEW.number := 'TK'||to_char(now(),'YYYYMMDD')||lpad(nextval('task_seq')::char, 7, '0');
RETURN NEW;
END;
$fn_task_seq$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS cc_task_seq ON rect_cctask;
CREATE TRIGGER cc_task_seq
    BEFORE INSERT ON rect_cctask
            FOR EACH ROW
            EXECUTE PROCEDURE fn_task_seq();

DROP TRIGGER IF EXISTS cs_task_seq ON rect_classifytask;
CREATE TRIGGER cs_task_seq
    BEFORE INSERT ON rect_classifytask
            FOR EACH ROW
            EXECUTE PROCEDURE fn_task_seq();

DROP TRIGGER IF EXISTS rp_task_seq ON rect_pagetask;
CREATE TRIGGER rp_task_seq
    BEFORE INSERT ON rect_pagetask
            FOR EACH ROW
            EXECUTE PROCEDURE fn_task_seq();


DROP TRIGGER IF EXISTS ab_task_seq ON rect_absenttask;
CREATE TRIGGER ab_task_seq
    BEFORE INSERT ON rect_absenttask
            FOR EACH ROW
            EXECUTE PROCEDURE fn_task_seq();


DROP TRIGGER IF EXISTS dl_task_seq ON rect_deltask;
CREATE TRIGGER dl_task_seq
    BEFORE INSERT ON rect_deltask
            FOR EACH ROW
            EXECUTE PROCEDURE fn_task_seq();

DROP TRIGGER IF EXISTS rv_task_seq ON rect_reviewtask;
CREATE TRIGGER rv_task_seq
    BEFORE INSERT ON rect_reviewtask
            FOR EACH ROW
            EXECUTE PROCEDURE fn_task_seq();


