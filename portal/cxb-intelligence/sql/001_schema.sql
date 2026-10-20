CREATE EXTENSION IF NOT EXISTS postgis;
CREATE SCHEMA IF NOT EXISTS cxb;
CREATE TABLE IF NOT EXISTS cxb.source_asset(id text PRIMARY KEY, metadata jsonb NOT NULL);
CREATE TABLE IF NOT EXISTS cxb.geography(id text PRIMARY KEY, label text NOT NULL UNIQUE, geometry geometry(MultiPolygon,4326), geometry_source text REFERENCES cxb.source_asset(id));
CREATE TABLE IF NOT EXISTS cxb.population_snapshot(geo_id text REFERENCES cxb.geography(id), observation_date date NOT NULL, individuals integer NOT NULL CHECK(individuals>=0), families integer NOT NULL CHECK(families>=0), source_id text REFERENCES cxb.source_asset(id), PRIMARY KEY(geo_id,observation_date));
CREATE TABLE IF NOT EXISTS cxb.demographic_snapshot(geo_id text REFERENCES cxb.geography(id), observation_date date NOT NULL, age_band text NOT NULL, sex text NOT NULL CHECK(sex IN ('female','male')), individuals integer NOT NULL CHECK(individuals>=0), source_id text REFERENCES cxb.source_asset(id), PRIMARY KEY(geo_id,observation_date,age_band,sex));
CREATE TABLE IF NOT EXISTS cxb.sector_indicator(id text PRIMARY KEY, observation jsonb NOT NULL);
CREATE TABLE IF NOT EXISTS cxb.analysis_release(id text PRIMARY KEY, payload jsonb NOT NULL, sha256 text NOT NULL, loaded_at timestamptz NOT NULL DEFAULT now());
CREATE OR REPLACE VIEW cxb.population_change AS
 SELECT g.label,a.individuals AS august,b.individuals AS september,b.individuals-a.individuals AS change,
 round(100.0*(b.individuals-a.individuals)/NULLIF(a.individuals,0),6) AS change_pct
 FROM cxb.population_snapshot a JOIN cxb.population_snapshot b USING(geo_id) JOIN cxb.geography g ON g.id=a.geo_id
 WHERE a.observation_date='2026-08-31' AND b.observation_date='2026-09-30';
