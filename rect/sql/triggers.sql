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


CREATE or REPLACE FUNCTION fn_gen_sid() RETURNS trigger AS $fn_gen_sid$
BEGIN NEW.sid := NEW.tripitaka_id||lpad(NEW.code, 5, '0')||NEW.variant_code;
RETURN NEW;
END;
$fn_gen_sid$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS fn_gen_sid ON rect_sutra;
CREATE TRIGGER fn_gen_sid
    BEFORE INSERT ON rect_sutra
            FOR EACH ROW
            EXECUTE PROCEDURE fn_gen_sid();

CREATE or REPLACE FUNCTION fn_gen_rid() RETURNS trigger AS $fn_gen_rid$
BEGIN NEW.rid := NEW.sutra_id||'r'|| lpad(NEW.reel_no, 3, '0');
RETURN NEW;
END;
$fn_gen_rid$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS fn_gen_rid ON rect_reel;
CREATE TRIGGER fn_gen_rid
    BEFORE INSERT ON rect_reel
            FOR EACH ROW
            EXECUTE PROCEDURE fn_gen_rid();


CREATE or REPLACE FUNCTION fn_gen_pid() RETURNS trigger AS $fn_gen_pid$
BEGIN
IF NEW.bar_no IS NULL THEN
NEW.pid := LEFT(NEW.reel_id, 8)||'v'||lpad(NEW.vol_no, 3, '0')||'p'||to_char(NEW.page_no,'FM0000')||'0';
ELSE
NEW.pid := LEFT(NEW.reel_id, 8)||'v'||lpad(NEW.vol_no, 3, '0')||'p'||to_char(NEW.page_no,'FM0000')||NEW.bar_no;
END IF;
RETURN NEW;
END;
$fn_gen_pid$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS fn_gen_pid ON rect_page;
CREATE TRIGGER fn_gen_pid
    BEFORE INSERT ON rect_page
            FOR EACH ROW
            EXECUTE PROCEDURE fn_gen_pid();


CREATE or REPLACE FUNCTION fn_gen_cid() RETURNS trigger AS $fn_gen_cid$
NEW.cid := NEW.page_code|| to_char(NEW.line_no, 'FM00')|| 'n' || to_char(NEW.char_no, 'FM00');
RETURN NEW;
END;
$fn_gen_cid$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS fn_gen_cid ON rect_rect;
CREATE TRIGGER fn_gen_cid
    BEFORE INSERT OR UPDATE ON rect_rect
            FOR EACH ROW
            EXECUTE PROCEDURE fn_gen_cid();