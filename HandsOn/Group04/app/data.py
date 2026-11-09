"""Access to the Breathe & Play Madrid knowledge graph.

The app sends SPARQL queries to one of two sources:

- "local" (default): the RDF files of Hands-on 6 are loaded in memory with
  pyoxigraph, an RDF store that runs inside Python (about 1 second).
- "graphdb": the SPARQL endpoint of the repository published in GraphDB, e.g.
  http://localhost:7200/repositories/breatheplay

To use GraphDB, set the environment variable before starting the app:
    set BPM_SPARQL_ENDPOINT=http://localhost:7200/repositories/breatheplay   (Windows)
    export BPM_SPARQL_ENDPOINT=http://localhost:7200/repositories/breatheplay (Linux/Mac)
"""
import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

GROUP_DIR = Path(__file__).resolve().parent.parent  # HandsOn/Group04
RDF_FILES = [
    GROUP_DIR / "rdf" / "calidad-aire-diario-2024-reuse.ttl",
    GROUP_DIR / "rdf" / "estaciones-control-aire-reuse.ttl",
    GROUP_DIR / "rdf" / "instalaciones-deportivas-reuse.ttl",
    GROUP_DIR / "ontology" / "breatheplay-kos.ttl",
    GROUP_DIR / "ontology" / "breatheplay-reuse.ttl",
]
ENDPOINT = os.environ.get("BPM_SPARQL_ENDPOINT", "").strip()

XSD = "http://www.w3.org/2001/XMLSchema#"
NUMBER_TYPES = {XSD + t for t in ("decimal", "double", "float", "integer", "int", "long")}


def source_name():
    return f"GraphDB ({ENDPOINT})" if ENDPOINT else "RDF local (pyoxigraph)"


def _convert(value, datatype):
    """Turns an RDF literal into a Python value (number, bool or text)."""
    if datatype in NUMBER_TYPES:
        return float(value)
    if datatype == XSD + "boolean":
        return value == "true"
    return value


@st.cache_resource(show_spinner="Cargando el grafo (unos segundos)...")
def _local_store():
    import pyoxigraph as ox

    store = ox.Store()
    for path in RDF_FILES:
        store.bulk_load(path=str(path), format=ox.RdfFormat.TURTLE)
    return store


def _query_local(sparql):
    import pyoxigraph as ox

    result = _local_store().query(sparql)
    names = [v.value for v in result.variables]
    rows = []
    for solution in result:
        row = {}
        for name in names:
            term = solution[name]
            if term is None:
                row[name] = None
            elif isinstance(term, ox.Literal):
                row[name] = _convert(term.value, term.datatype.value)
            else:
                row[name] = term.value
        rows.append(row)
    return pd.DataFrame(rows, columns=names)


def _query_graphdb(sparql):
    response = requests.post(
        ENDPOINT,
        data={"query": sparql},
        headers={"Accept": "application/sparql-results+json"},
        timeout=60,
    )
    response.raise_for_status()
    result = response.json()
    names = result["head"]["vars"]
    rows = []
    for binding in result["results"]["bindings"]:
        row = {}
        for name in names:
            term = binding.get(name)
            if term is None:
                row[name] = None
            elif term["type"] == "literal":
                row[name] = _convert(term["value"], term.get("datatype", ""))
            else:
                row[name] = term["value"]
        rows.append(row)
    return pd.DataFrame(rows, columns=names)


@st.cache_data(show_spinner=False)
def query(sparql):
    """Runs a SPARQL SELECT query and returns the results as a table (DataFrame)."""
    return _query_graphdb(sparql) if ENDPOINT else _query_local(sparql)
