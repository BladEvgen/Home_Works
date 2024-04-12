-- Создание личного типа данных для передачи информации о предмете одежды
CREATE TYPE ClothesData AS (
    name VARCHAR(255),
    category_name VARCHAR(255),
    category_slug VARCHAR(255),
    wearing_period INTEGER,
    description TEXT
);

-- POST Процедура вставки новых данных
CREATE
OR REPLACE PROCEDURE create_clothes (clothes_data ClothesData) LANGUAGE plpgsql AS DECLARE category_id bigint;

BEGIN
SELECT
    id INTO category_id
FROM
    clothes_app_category
WHERE
    name = clothes_data.category_name;

IF NOT FOUND THEN
INSERT INTO
    clothes_app_category (name, slug)
VALUES
    (
        clothes_data.category_name,
        clothes_data.category_slug
    ) RETURNING id INTO category_id;

END IF;

INSERT INTO
    clothes_app_clothes (name, category_id, wearing_period, description)
VALUES
    (
        clothes_data.name,
        category_id,
        clothes_data.wearing_period,
        clothes_data.description
    );

END;

-- Пример использования процедуры 
CALL create_clothes (
    (
        'Платье',
        'Платья',
        'platya',
        30,
        'Прекрасное платье для вечеринок'
    )
);

-- UPDATE (PUT) Процедура обновления информации об одежды
CREATE
OR REPLACE PROCEDURE update_clothes_user (
    clothes_id_param bigint,
    person_id_param bigint,
    date_started_wearing_param date,
    date_ended_wearing_param date
) LANGUAGE plpgsql AS BEGIN
UPDATE clothes_app_clothesuser
SET
    date_started_wearing = date_started_wearing_param,
    date_ended_wearing = date_ended_wearing_param
WHERE
    clothes_id = clothes_id_param
    AND person_id = person_id_param;

COMMIT;

END;

-- Пример 
CALL update_clothes_user (3, 2, '2024-05-01', '2024-05-10');

-- DELETE Процедура по удалению 
CREATE
OR REPLACE PROCEDURE delete_clothes (p_clothes_id BIGINT) LANGUAGE plpgsql AS BEGIN
DELETE FROM clothes_app_clothesuser
WHERE
    clothes_id = p_clothes_id;

DELETE FROM clothes_app_clothes
WHERE
    id = p_clothes_id;

END;

--Использование 
CALL delete_clothes (1);

-- GET Получение информации об Одежде, кто использует и дате окончания и начала
CREATE
OR REPLACE FUNCTION get_cloth_info (cloth_id BIGINT) RETURNS TABLE (
    id BIGINT,
    Cloth_title VARCHAR(255),
    Cloth_category VARCHAR(100),
    date_of_start DATE,
    end_date_of_wearing DATE,
    period_in_days INTEGER,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    patranomic VARCHAR(100)
) LANGUAGE SQL AS
SELECT
    c.id,
    c.name AS Cloth_title,
    cat.name AS Cloth_category,
    cu.date_started_wearing AS start_date_of_wearing,
    cu.date_ended_wearing AS end_date_of_wearing,
    c.wearing_period AS period_in_days,
    p.first_name,
    p.last_name,
    p.patronymic
FROM
    clothes_app_clothes c
    JOIN clothes_app_category cat ON c.category_id = cat.id
    JOIN clothes_app_clothesuser cu ON c.id = cu.clothes_id
    JOIN clothes_app_person p ON cu.person_id = p.id
WHERE
    c.id = cloth_id;

--Использование
SELECT
    *
FROM
    get_cloth_info (2);



-- TRIGGER DB
CREATE TABLE
    clothesuser_logs (
        id SERIAL PRIMARY KEY,
        action TEXT NOT NULL,
        field_changed TEXT,
        timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

GRANT USAGE,
SELECT
    ON SEQUENCE clothesuser_logs_id_seq TO admin;


-- TRIGGER 
DECLARE
    operation_text TEXT;
    changed_fields TEXT := '';
    column_record RECORD;
    old_value TEXT;
    new_value TEXT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        operation_text := 'INSERT';
        
        FOR column_record IN
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = TG_TABLE_NAME AND column_name <> 'id'
        LOOP
            EXECUTE 'SELECT ($1).' || column_record.column_name INTO new_value USING NEW;
            changed_fields := changed_fields || column_record.column_name || ': ' || new_value || ', ';
        END LOOP;
    ELSIF TG_OP = 'UPDATE' THEN
        operation_text := 'UPDATE';
        
        FOR column_record IN
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = TG_TABLE_NAME AND column_name <> 'id'
        LOOP
            EXECUTE 'SELECT ($1).' || column_record.column_name INTO new_value USING NEW;
            EXECUTE 'SELECT ($1).' || column_record.column_name INTO old_value USING OLD;
            IF new_value <> old_value THEN
                changed_fields := changed_fields || column_record.column_name || ': ' || old_value || ' -> ' || new_value || ', ';
            END IF;
        END LOOP;
    ELSIF TG_OP = 'DELETE' THEN
        operation_text := 'DELETE';
        
        FOR column_record IN
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = TG_TABLE_NAME AND column_name <> 'id'
        LOOP
            EXECUTE 'SELECT ($1).' || column_record.column_name INTO old_value USING OLD;
            changed_fields := changed_fields || column_record.column_name || ': ' || old_value || ', ';
        END LOOP;
    END IF;

    IF LENGTH(changed_fields) > 0 THEN
        changed_fields := LEFT(changed_fields, LENGTH(changed_fields) - 2);
    END IF;

    INSERT INTO clothesuser_logs (action, field_changed, timestamp)
    VALUES (operation_text, changed_fields, NOW());

    RETURN NEW;
END;



-- Функция которя возвращает только у кого date_ended меньше текущей даты, UNION ALL

CREATE OR REPLACE FUNCTION get_currently_worn_clothes()
RETURNS TABLE (
    clothes_name character varying,
    category_name character varying,
    user_first_name character varying,
    user_last_name character varying,
    user_tabel_num character varying,
    date_started_wearing date,
    date_ended_wearing date
)
AS $$
BEGIN
    RETURN QUERY
    (
        SELECT
            c.name AS clothes_name,
            cat.name AS category_name,
            p.first_name AS user_first_name,
            p.last_name AS user_last_name,
            p.tabel_num AS user_tabel_num,
            cu.date_started_wearing,
            cu.date_ended_wearing
        FROM
            clothes_app_clothesuser cu
        JOIN
            clothes_app_clothes c ON cu.clothes_id = c.id
        JOIN
            clothes_app_category cat ON c.category_id = cat.id
        JOIN
            clothes_app_person p ON cu.person_id = p.id
        WHERE
            cu.date_started_wearing <= CURRENT_DATE
            AND (cu.date_ended_wearing IS NULL OR cu.date_ended_wearing = CURRENT_DATE)

        UNION ALL

        SELECT
            c.name AS clothes_name,
            cat.name AS category_name,
            p.first_name AS user_first_name,
            p.last_name AS user_last_name,
            p.tabel_num AS user_tabel_num,
            cu.date_started_wearing,
            cu.date_ended_wearing
        FROM
            clothes_app_clothesuser cu
        JOIN
            clothes_app_clothes c ON cu.clothes_id = c.id
        JOIN
            clothes_app_category cat ON c.category_id = cat.id
        JOIN
            clothes_app_person p ON cu.person_id = p.id
        WHERE
            cu.date_ended_wearing <= CURRENT_DATE
    );
END;
$$ LANGUAGE plpgsql;

-- Использование 
SELECT * FROM get_currently_worn_clothes();