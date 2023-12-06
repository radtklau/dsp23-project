-- Table: public.data_errors

-- DROP TABLE IF EXISTS public.data_errors;

CREATE TABLE IF NOT EXISTS public.data_errors
(
    id integer NOT NULL DEFAULT nextval('data_errors_id_seq'::regclass),
    dag_run_date timestamp without time zone NOT NULL,
    file_name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default",
    CONSTRAINT data_errors_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.data_errors
    OWNER to postgres;
