# Hands-on assignment 6 – Ontology reuse

Group 04 · Breathe & Play Madrid

## Summary

Version 1 of our ontology (`ontology/breatheplay.ttl`, v1.1.0) was our own model
(12 classes and 25 `bpm:` properties), aligned with SOSA, WGS84 and schema.org.
In this hands-on we regenerated the knowledge graph reusing the **EDINT ontologies**
(*Espacio de Datos para las Infraestructuras Urbanas Inteligentes*, governed by the
Spanish Federation of Municipalities and Provinces, FEMP), which are built on SOSA,
GeoSPARQL, QUDT and OWL-Time:

- [EDINT Environmental Sensors, Air Quality case](https://edint.es/def/calidad-aire/index-es.html)
  (`edintmed:`, https://edint.es/def/medio-ambiente#) for D1 and D2;
- [EDINT Infrastructure](https://edint.es/def/infraestructura/index-es.html)
  (`edintinf:`, https://edint.es/def/infraestructura#) for D3;
- their controlled vocabularies (SKOS): environmental properties, features of
  interest, sensor types and infrastructure types;
- the Spanish vocabularies they reuse for territory (`esadm:Distrito`, `esadm:Barrio`)
  and postal addresses (`esdir:DireccionPostal`).

Version 2.0.0 (`ontology/breatheplay-reuse.ttl`) only defines the terms that have no
equivalent in them: **2 classes and 7 properties** (before: 12 and 25).

## What changed

| Version 1 (own term) | Version 2 (reused term) | Why |
|---|---|---|
| `bpm:MonitoringStation` | `edintmed:SensorPlatform` | same meaning: a platform that hosts sensors (it was already `sosa:Platform`) |
| `bpm:SamplingPoint` | `edintmed:EnvironmentalSensor` + `edintmed:hasSensorType` AirQualitySensor | in EDINT each sensor observes one property at one station, like our sampling points |
| `bpm:DailyObservation` | `edintmed:EnvironmentalObservation` (kept `bpm:DailyObservation` as subclass) | EDINT does not distinguish daily means |
| — | `sosa:hasFeatureOfInterest` Air | new, from the EDINT pattern |
| `bpm:Pollutant` (11 resources) | EDINT environmental properties (`NO2Concentration`…) | reference data maintained by EDINT; ethylbenzene does not exist → own concept |
| `bpm:unit` ("µg/m³") | `qudt:unit` (`unit:MicroGM-PER-M3`, `unit:MilliGM-PER-M3`) | standard units |
| `bpm:date` | `sosa:phenomenonTime` → OWL-Time day (`time:Interval`, beginning `time:Instant` with `time:inXSDDate`, duration P1D) | a daily mean is a value for a whole day; no hour is needed |
| `bpm:MeasurementTechnique` + `bpm:usesTechnique` | `sosa:Procedure` + `sosa:implements` | EDINT has no procedure, so we use SOSA directly |
| `bpm:SportsFacility` | `edintinf:Facility` | |
| `bpm:FacilityType` (24) + `bpm:hasFacilityType` | `edintinf:hasInfrastructureType` → EDINT infrastructure types | see below |
| `bpm:AccessibilityLevel` + `bpm:hasAccessibilityLevel` | `edintinf:accessibility` (text) | EDINT uses text; the 4 values are kept as text, so no information is lost |
| `bpm:District`, `bpm:Neighbourhood` | `esadm:Distrito`, `esadm:Barrio` | Spanish territory vocabulary; the `owl:sameAs` links to Wikidata are kept |
| `bpm:locatedInDistrict`, `bpm:locatedInNeighbourhood` | `edintinf:belongsTo` | |
| `bpm:isPartOfDistrict` | `gsp:sfWithin` | GeoSPARQL |
| `bpm:Place` ⊑ `geo:SpatialThing` | GeoSPARQL features (`gsp:hasGeometry` with a WKT point) | both EDINT classes are GeoSPARQL features; `geo:lat`/`geo:long` are kept, as in the EDINT examples |
| `bpm:address`, `bpm:postalCode` | `schema:address` → `esdir:DireccionPostal` (`schema:streetAddress`, `schema:postalCode`, `schema:addressLocality`) | |
| `bpm:contentURL` | `schema:url` | |
| `bpm:stationCode`, `bpm:samplingPointCode`, `bpm:techniqueCode`, `bpm:facilityId`, `bpm:districtCode`, `bpm:neighbourhoodCode` | `dct:identifier` | EDINT uses `dct:identifier` for codes |
| `bpm:pollutantCode` | `skos:notation` of the Madrid code concept | see below |

**Kept as our own terms** (no equivalent in EDINT): `bpm:DailyObservation`, `bpm:isValid`
(validation flag), `bpm:StationType` and `bpm:hasStationType`, `bpm:startDate`,
`bpm:equipment`, `bpm:transportInfo`, and the link between the two domains:
`bpm:hasNearestStation` and `bpm:distanceToNearestStation`.

**IRIs of our resources did not change** (stations, sampling points, observations,
techniques, facilities, districts, neighbourhoods, pollutant codes and facility
types). New resources: `day/`, `instant/`, `geometry/` and `postal-address/`.

## Madrid code lists mapped to EDINT

We do not want to lose the codes and the classification of the Madrid City Council,
so they are kept as SKOS lists mapped to EDINT (like an authority table crosswalk),
using two correspondence tables in `csv/`:

- `csv/edint-environmental-properties.csv`: Madrid pollutant code (`MAGNITUD`) →
  EDINT environmental property, QUDT unit and Wikidata entity (from Hands-on 5).
  The Madrid codes become `resource/pollutant/{MAGNITUD}` concepts with
  `skos:exactMatch` to EDINT. The observations point to the EDINT concept.
- `csv/edint-infrastructure-types.csv`: Madrid facility type (`TIPO_ID`) → EDINT
  infrastructure type, with the kind of correspondence: 9 exact, 11 close, 2 broad
  ("Instalaciones Deportivas Basicas" and "Centros Espacios Deporte" →
  *Equipamiento deportivo*) and 2 own concepts (table tennis, pickleball).
  "Pistas Tenis Badminton" corresponds to two EDINT types. Each facility has both its
  Madrid type and its EDINT type(s) with `edintinf:hasInfrastructureType`.

Keeping both is necessary: for example, the EDINT type *Fitness de exterior y
circuitos biosaludables* groups "Calistenia", "Circuito Vida" and "Cubo Gym", so the
competency question about calisthenics (CQ01) uses the Madrid type.

## Critical analysis

- **Pollutant vs. concentration.** In version 1 a pollutant was the substance
  (`owl:sameAs` the Wikidata entity of NO2) and also the observed property. In SOSA
  and EDINT what is observed is a property, the *concentration* of NO2 in the air.
  The link to Wikidata is kept, but as `skos:relatedMatch` from our Madrid code
  concept: the concentration is related to the substance, not the same thing.
- **Missing concepts.** Ethylbenzene (pollutant 35), table tennis and pickleball are
  not in the EDINT vocabularies. We created them in `ontology/breatheplay-kos.ttl`
  with the same pattern and `skos:broader` an EDINT concept, so that they could be
  proposed to EDINT as issues in its GitHub repositories (that is how EDINT is
  governed: change requests are reviewed by committees).
- **Precision lost.** Some Madrid types are only close or broad matches of EDINT
  types (182 facilities are "basic sports facilities", i.e. only *Equipamiento
  deportivo*). This is why the Madrid list is kept.
- **Daily means.** EDINT examples use `sosa:resultTime` (date and time) or a time
  period per observation. Our values are daily means without hour, so each
  observation points to a shared OWL-Time day (335 days with data).
- **Procedure.** The EDINT air quality ontology is "purely SOSA" without procedures;
  the measurement technique matters for interpreting the values, so we keep it
  with `sosa:Procedure` / `sosa:implements`.
- **Domains.** `edintinf:belongsTo` is defined for infrastructure elements and
  observation points; we also use it for the monitoring stations (a station is an
  urban infrastructure element), so one property links everything to its district
  and neighbourhood.
- **Size.** The graph grows from 355,889 to 492,734 triples (feature of interest,
  units and days of each observation, geometries, postal addresses and the SKOS
  lists), but the data can now be queried with the same vocabulary as other
  Spanish municipalities that use EDINT.

## Verification

- `rdf/queries-reuse.sparql` (Q1–Q17): the control queries Q2–Q4 return no
  results, and the data and competency question queries return the same results
  as in Hands-on 4 and 5 (e.g. Q7 NO2 ranking, Q12 CQ03 64 football pitches,
  Q13 CQ04 Hortaleza 72 facilities, Q17 12 facilities in the same Wikidata
  neighbourhood as a station).
- The merged graph conforms to the SHACL shapes published by EDINT
  (`shapes/shapes.ttl` of the environment and infrastructure repositories), when
  validated together with the EDINT vocabularies: some shapes require that the
  values are `skos:Concept` (e.g. the sensor type `AirQualitySensor`), and that is
  stated in the EDINT vocabularies, not in our data. Run
  `python validate_shacl-reuse.py` (pySHACL; it reads the EDINT files from GitHub at
  the commit we used); the report is `shacl/report-reuse.ttl` (`sh:conforms true`).

## Files

| File | Content |
|---|---|
| `ontology/breatheplay-reuse.ttl` | ontology v2.0.0 (own terms + declaration of the reused ones) |
| `ontology/breatheplay-kos.ttl` | own SKOS concepts and concept schemes |
| `ontology/breatheplay-reuse.drawio.xml` | diagram of version 2.0.0 in Chowlk notation (orange: own terms; blue: EDINT terms; white: other standards). Chowlk generates from it the same domains, ranges and subclass axioms of our own terms as in `breatheplay-reuse.ttl`; the reused properties are drawn between the classes we use them with, as in the EDINT diagrams, and `gsp:Feature` groups the location properties of stations and facilities |
| `csv/edint-environmental-properties.csv`, `csv/edint-infrastructure-types.csv` | correspondence tables |
| `mappings/*-reuse.rml` | RML mappings (sources: the Hands-on 5 CSV files + correspondence tables) |
| `mappings/generate_rdf-reuse.py` | `python mappings/generate_rdf-reuse.py` (with `PYTHONUTF8=1` on Windows) |
| `rdf/*-reuse.ttl`, `rdf/*-reuse.nt` | RDF: 476,204 / 535 / 15,995 triples |
| `rdf/queries-reuse.sparql` | queries (load the 3 RDF files and `ontology/breatheplay-kos.ttl`) |
| `validate_shacl-reuse.py`, `shacl/report-reuse.ttl` | SHACL validation with the EDINT shapes and its report |
