--
-- PostgreSQL database dump
--

-- Dumped from database version 9.4.10
-- Dumped by pg_dump version 9.4.10
-- Started on 2017-01-08 17:57:05

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = ON;
SET check_function_bodies = FALSE;
SET client_min_messages = WARNING;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = FALSE;

--
-- TOC entry 196 (class 1259 OID 20742)
-- Name: dives; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE dives (
  id         INTEGER NOT NULL,
  start_time TIMESTAMP WITH TIME ZONE,
  end_time   TIMESTAMP WITH TIME ZONE
);

--
-- TOC entry 195 (class 1259 OID 20740)
-- Name: dives_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE dives_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;

--
-- TOC entry 3358 (class 0 OID 0)
-- Dependencies: 195
-- Name: dives_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE dives_id_seq OWNED BY dives.id;

--
-- TOC entry 200 (class 1259 OID 20765)
-- Name: measures; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE measures (
  id                    INTEGER                  NOT NULL,
  "timestamp"           TIMESTAMP WITH TIME ZONE NOT NULL,
  location_corrected    GEOMETRY,
  location_brut         GEOMETRY                 NOT NULL,
  correction_vector     GEOMETRY,
  acceleration          GEOMETRY                 NOT NULL,
  precision_mm          INTEGER,
  measure_value         CHARACTER VARYING(255)   NOT NULL,
  dive_id               INTEGER                  NOT NULL,
  measureinformation_id INTEGER
);

--
-- TOC entry 3359 (class 0 OID 0)
-- Dependencies: 200
-- Name: COLUMN measures.location_corrected; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN measures.location_corrected IS 'location_corrected';

--
-- TOC entry 198 (class 1259 OID 20752)
-- Name: measures_information; Type: TABLE; Schema: public; Owner: -; Tablespace:
--

CREATE TABLE measures_information (
  id      INTEGER                NOT NULL,
  type    CHARACTER VARYING(255) NOT NULL,
  display CHARACTER VARYING(255) NOT NULL,
  unit    CHARACTER VARYING(255) NOT NULL,
  name    CHARACTER VARYING(255) NOT NULL
);

--
-- TOC entry 199 (class 1259 OID 20763)
-- Name: measures_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE measures_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;

--
-- TOC entry 3360 (class 0 OID 0)
-- Dependencies: 199
-- Name: measures_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE measures_id_seq OWNED BY measures.id;

--
-- TOC entry 197 (class 1259 OID 20750)
-- Name: measures_information_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE measures_information_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;

--
-- TOC entry 3361 (class 0 OID 0)
-- Dependencies: 197
-- Name: measures_information_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE measures_information_id_seq OWNED BY measures_information.id;

--
-- TOC entry 3217 (class 2604 OID 20745)
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY dives
  ALTER COLUMN id SET DEFAULT nextval('dives_id_seq' :: REGCLASS);

--
-- TOC entry 3219 (class 2604 OID 20768)
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY measures
  ALTER COLUMN id SET DEFAULT nextval('measures_id_seq' :: REGCLASS);

--
-- TOC entry 3218 (class 2604 OID 20755)
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY measures_information
  ALTER COLUMN id SET DEFAULT nextval('measures_information_id_seq' :: REGCLASS);

--
-- TOC entry 3221 (class 2606 OID 20747)
-- Name: DIVES_PK_ID; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY dives
  ADD CONSTRAINT "DIVES_PK_ID" PRIMARY KEY (id);

--
-- TOC entry 3223 (class 2606 OID 20749)
-- Name: DIVES_UNIQUE_START_END; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY dives
  ADD CONSTRAINT "DIVES_UNIQUE_START_END" UNIQUE (start_time, end_time);

--
-- TOC entry 3225 (class 2606 OID 20760)
-- Name: MEASURESINFORMATION_PK_ID; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY measures_information
  ADD CONSTRAINT "MEASURESINFORMATION_PK_ID" PRIMARY KEY (id);

--
-- TOC entry 3227 (class 2606 OID 20762)
-- Name: MEASURESINFORMATION_UNIQUE_NAME; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY measures_information
  ADD CONSTRAINT "MEASURESINFORMATION_UNIQUE_NAME" UNIQUE (name);

--
-- TOC entry 3229 (class 2606 OID 20773)
-- Name: MEASURES_PK_ID; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY measures
  ADD CONSTRAINT "MEASURES_PK_ID" PRIMARY KEY (id);

--
-- TOC entry 3231 (class 2606 OID 20775)
-- Name: MEASURES_UNIQUE_POSITION_MEASURE_VALUE; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace:
--

ALTER TABLE ONLY measures
  ADD CONSTRAINT "MEASURES_UNIQUE_POSITION_MEASURE_VALUE" UNIQUE (location_brut, location_corrected, measureinformation_id);

--
-- TOC entry 3232 (class 1259 OID 20809)
-- Name: sidx_measures_acceleration; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX sidx_measures_acceleration
  ON measures USING GIST (acceleration);

--
-- TOC entry 3233 (class 1259 OID 20810)
-- Name: sidx_measures_correction_vector; Type: INDEX; Schema: public; Owner: -; Tablespace:
--

CREATE INDEX sidx_measures_correction_vector
  ON measures USING GIST (correction_vector);

--
-- TOC entry 3234 (class 2606 OID 20776)
-- Name: MEASURES_FK_DIVE_ID_DIVES_ID; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY measures
  ADD CONSTRAINT "MEASURES_FK_DIVE_ID_DIVES_ID" FOREIGN KEY (dive_id) REFERENCES dives (id) ON DELETE CASCADE;

--
-- TOC entry 3235 (class 2606 OID 20781)
-- Name: MEASURES_FK_MEASUREINFORMATION_ID_MEASURESINFORMATION_ID; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY measures
  ADD CONSTRAINT "MEASURES_FK_MEASUREINFORMATION_ID_MEASURESINFORMATION_ID" FOREIGN KEY (measureinformation_id) REFERENCES measures_information (id) ON DELETE CASCADE;

--
-- View: public.measures_formated
--

CREATE OR REPLACE VIEW public.measures_formated AS
  SELECT
    measures.id                                                                                           AS measure_id,
    dives.id                                                                                              AS dive_id,
    dives.start_time,
    dives.end_time,
    measures."timestamp",
    measures.location_corrected,
    measures.location_brut,
    measures.measure_value,
    regexp_replace(measures_information.display :: TEXT, '\{0\}' :: TEXT, measures.measure_value :: TEXT) AS display,
    measures_information.type,
    measures_information.unit,
    measures_information.name
  FROM dives,
    measures,
    measures_information
  WHERE measures.dive_id = dives.id AND measures_information.id = measures.measureinformation_id;

SELECT Populate_Geometry_Columns(('public.measures') :: REGCLASS);
SELECT Populate_Geometry_Columns(('public.measures_formated') :: REGCLASS);


-- Completed on 2017-01-08 17:57:06

--
-- PostgreSQL database dump complete
--


--- INSERTS
INSERT INTO public.dives (start_time, end_time) VALUES (?, ?);
INSERT INTO public.measures_information (type, display, unit, name) VALUES (?, ?, ?, ?);
INSERT INTO public.measures ("timestamp", location_brut, acceleration, measure_value, dive_id, measureinformation_id)
VALUES (time, ST_SetSRID(ST_MakePoint(X, Y, Z), 4326), ST_MakePoint(aX, aY, aZ), temp, dive_id, measure_id);
