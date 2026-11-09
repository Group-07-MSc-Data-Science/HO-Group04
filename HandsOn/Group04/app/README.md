# Breathe & Play Madrid – application

Web application (Streamlit) over the knowledge graph of Hands-on 6. Every value shown
comes from a SPARQL query over the graph (`queries.py`).

| Page | What it shows | Requirements (applicationRequirements.html) |
|---|---|---|
| **Mapa** | The 607 sports facilities on a map, coloured by the air quality measured on the chosen day at their nearest monitoring station; filters by type, district and accessibility; the 24 stations | FR1, FR2, FR3, FR9 |
| **Ficha de la instalación** | Data of a facility, its nearest station, the district and neighbourhood in Wikidata, and the daily values of a pollutant in 2024 with the days above the reference value | FR4, FR5, FR8, FR9 |
| **Distritos** | Facilities and mean value of a pollutant per district (with the Wikidata link), and the facilities of a type with the cleanest air | FR6, FR7, FR8 |

The source and licence of the data (CC BY 4.0, Madrid City Council) are shown on every
page (FR10).

Air quality categories: daily mean ≤ reference value → *Bueno*, ≤ 2 × reference →
*Moderado*, above → *Malo*. Reference values: WHO Air Quality Guidelines 2021, 24-hour
values (NO2 25, PM10 45, PM2.5 15, SO2 40 µg/m³, CO 4 mg/m³; for O3, 100 µg/m³ is an
8-hour value used as an approximation). They are in `queries.py` (`REFERENCE`). Values
marked as not valid by the City Council are not used.

## Files

| File | Content |
|---|---|
| `app.py` | Entry point and navigation |
| `mapa.py`, `ficha.py`, `distritos.py` | The three pages |
| `queries.py` | SPARQL queries (EDINT, SOSA, OWL-Time… vocabulary) and reference values |
| `data.py` | Runs the queries: RDF loaded locally with pyoxigraph, or the GraphDB endpoint |
| `common.py` | Shared helpers (air quality categories, Wikidata, footer) |

## Run

Use a separate Python environment (the version of pyoxigraph used here is newer than
the one Morph-KGC needs). With Anaconda:

```
conda create -n bpm-app python=3.12
conda activate bpm-app
cd HandsOn/Group04
pip install -r app/requirements.txt
streamlit run app/app.py
```

The browser opens at http://localhost:8501. The first load takes a few seconds (the
graph is loaded in memory: `rdf/*-reuse.ttl`, `ontology/breatheplay-kos.ttl` and
`ontology/breatheplay-reuse.ttl`). The map and the Wikidata descriptions need an
internet connection.

### Using the graph published in GraphDB

Load the same files in a GraphDB repository (e.g. `breatheplay`), then start the app
with the endpoint in the variable `BPM_SPARQL_ENDPOINT`:

```
set BPM_SPARQL_ENDPOINT=http://localhost:7200/repositories/breatheplay      (Windows)
export BPM_SPARQL_ENDPOINT=http://localhost:7200/repositories/breatheplay   (Linux/Mac)
streamlit run app/app.py
```

The footer of the sidebar says which source is being used.
