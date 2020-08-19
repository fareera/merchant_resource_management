DO
$$

DECLARE

BEGIN
    --------------------------------------------------------------------
    -- SCHEMA
    --------------------------------------------------------------------

    --------------------------------------------------------------------
    -- TABLE
    --------------------------------------------------------------------

    -- brand
    DROP TABLE IF EXISTS brand CASCADE;
    CREATE TABLE IF NOT EXISTS brand (
        id int PRIMARY KEY SERIAL,
        name varchar(50) NOT NULL,
        create_time timestamp NOT NULL
    );

    -- product
    DROP TABLE IF EXISTS product CASCADE;
    CREATE TABLE IF NOT EXISTS product (
        sku_id int PRIMARY KEY SERIAL, -- 注意，要设置这个id从10000000开始递增，这样可以保持sku的位数一致性
        brand_id int NOT NULL,
        name varchar(200) NOT NULL,
        unit varchar(50) NOT NULL,
        price decimal(20, 3) NOT NULL,
        stock int NOT NULL,
        status int NOT NULL,
        image varchar(500) NOT NULL,
        image_thumbnail varchar(500) NOT NULL,
        image_list varchar(500) NOT NULL,
        description varchar(500) NOT NULL,
        keywords varchar(500) NOT NULL,
        create_time timestamp NOT NULL
        update_time timestamp NOT NULL
    );

    -- order
    DROP TABLE IF EXISTS order CASCADE;
    CREATE TABLE IF NOT EXISTS order (
        id int PRIMARY KEY SERIAL,
        order_delivery_id varchar(200) NOT NULL,
        sku_id int NOT NULL,
        amount decimal(20, 3) NOT NULL,
        partner_id int NOT NULL,
        status int NOT NULL,
        create_time timestamp NOT NULL
    );

    -- order_detail
    DROP TABLE IF EXISTS order_detail CASCADE;
    CREATE TABLE IF NOT EXISTS order_detail (
        order_id int NOT NULL,
        sku_id int NOT NULL,
        volume int NOT NULL
    );

    -- partner
    DROP TABLE IF EXISTS partner CASCADE;
    CREATE TABLE IF NOT EXISTS partner (
        id int PRIMARY KEY SERIAL,
        name varchar(200) NOT NULL,
        account varchar(200) NOT NULL,
        password varchar(200) NOT NULL
    );

    -- partner_history
    DROP TABLE IF EXISTS partner_history CASCADE;
    CREATE TABLE IF NOT EXISTS partner_history (
        id int PRIMARY KEY SERIAL,
        partner_id int NOT NULL,
        operation varchar(200) NOT NULL,
        description varchar(200) NOT NULL,
        update_time timestamp NOT NULL
    );


END
$$ LANGUAGE plpgsql;
