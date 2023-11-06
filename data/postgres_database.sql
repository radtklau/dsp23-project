-- Table: public.predictions

-- DROP TABLE IF EXISTS public.predictions;

CREATE TABLE IF NOT EXISTS public.predictions
(
    id SERIAL,
    "TotRmsAbvGrd" real,
    "WoodDeckSF" real,
    "YrSold" integer,
    "FirstFlrSF" real,
    "Foundation_BrkTil" integer,
    "Foundation_CBlock" integer,
    "Foundation_PConc" integer,
    "Foundation_Slab" integer,
    "Foundation_Stone" integer,
    "Foundation_Wood" integer,
    "KitchenQual_Ex" integer,
    "KitchenQual_Fa" integer,
    "KitchenQual_Gd" integer,
    "KitchenQual_TA" integer,
    predict_date timestamp without time zone,
    predict_result real,
    predict_source text COLLATE pg_catalog."default",
    CONSTRAINT prediction_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.predictions
    OWNER to postgres;