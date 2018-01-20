CREATE or REPLACE FUNCTION fn_create_reelstatis() RETURNS trigger AS $fn_create_reelstatis$
BEGIN
INSERT INTO rect_reel_task_statistical (schedule_id, reel_id,amount_of_cctasks,completed_cctasks,amount_of_absenttasks,completed_absenttasks,amount_of_pptasks,completed_pptasks,updated_at)
VALUES (NEW.schedule_id, NEW.reel_id,-1,0,-1,0,-1,0, now());
RETURN NEW;
END;
$fn_create_reelstatis$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS fn_create_reelstatis ON rect_schedule_reels;
CREATE TRIGGER fn_create_reelstatis
    BEFORE INSERT ON rect_schedule_reels
            FOR EACH ROW
            EXECUTE PROCEDURE fn_create_reelstatis();
