-- Table: public.data_errors

-- DROP TABLE IF EXISTS public.data_errors;
CREATE SEQUENCE data_errors_id_seq;

CREATE TABLE IF NOT EXISTS public.data_errors
(
    id integer NOT NULL DEFAULT nextval('data_errors_id_seq'::regclass),
    dag_run_date timestamp without time zone NOT NULL,
    file_name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default",
    percent_missing_values float,  
    evaluated_expectations integer,  
    successful_expectations integer, 
    unsuccessful_expectations integer,
    success_percent float,
    percent_bad_columns float,
    CONSTRAINT data_errors_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.data_errors
    OWNER to postgres;
