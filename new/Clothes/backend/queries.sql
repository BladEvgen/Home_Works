-- Создание личного типа данных для передачи информации о предмете одежды
CREATE TYPE ClothesInfo AS (
    name VARCHAR(255),
    category_id BIGINT,
    wearing_period INTEGER,
    description TEXT
);

-- Процедура вставки новых данных
CREATE OR REPLACE PROCEDURE create_clothes(
    clothes_data ClothesInfo
)
LANGUAGE SQL
AS $$
INSERT INTO django_app_cloth (title, category_id, deadline, date)
VALUES (clothes_data.name, clothes_data.category_id, clothes_data.wearing_period, CURRENT_DATE);
$$;

-- Пример использования процедуры 

CALL create_clothes(('Платье', 1, 30, 'Прекрасное платье для вечеринок'));


-- Процедура обновления информации об одежды
CREATE OR REPLACE PROCEDURE update_clothes(
    clothes_id BIGINT,
    clothes_data ClothesInfo
)
LANGUAGE SQL
AS $$
UPDATE django_app_cloth
SET title = clothes_data.name,
    category_id = clothes_data.category_id,
    deadline = clothes_data.wearing_period
WHERE id = clothes_id;
$$;

-- Пример 
CALL update_clothes(1, ('Брюки', 2, 60, 'Удобные повседневные брюки'));

-- Процедура по удалению 
CREATE OR REPLACE PROCEDURE delete_clothes(
    clothes_id BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM django_app_clothset
    WHERE cloth_type_id = clothes_id;

    DELETE FROM django_app_cloth
    WHERE id = clothes_id;

END;
$$;

--Использование 
CALL delete_clothes(1);


--Получение информации об Одежде, кто использует и дате окончания и начала

CREATE OR REPLACE FUNCTION get_cloth_info(cloth_id BIGINT)
RETURNS TABLE (
    id BIGINT,
    Cloth_title VARCHAR(255),
    Cloth_category VARCHAR(100),
    date_of_start DATE,
    end_date_of_wearing DATE,
    period_in_days INTEGER,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    patranomic VARCHAR(100)
)
LANGUAGE SQL
AS $$
SELECT c.id,
       c.title AS Cloth_title,
       cc.title AS Cloth_category,
       c.date AS date_of_start,
       (c.date + c.deadline) AS end_date_of_wearing,
       c.deadline AS period_in_days,
       p.first_name,
       p.last_name,
       p.patranomic
FROM django_app_cloth c
JOIN django_app_clothcategory cc ON c.category_id = cc.id
JOIN django_app_clothset cs ON c.id = cs.cloth_type_id
JOIN django_app_person p ON cs.person_id = p.id
WHERE c.id = cloth_id;
$$;

--Использование
SELECT * FROM get_cloth_info(2);
