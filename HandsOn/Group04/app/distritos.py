"""Districts: facilities and air quality per district, and the facilities of a
sport with the cleanest air (FR6, FR7)."""
import streamlit as st

import common
import data
import queries as q

st.title("Distritos")

pollutants = common.pollutant_table()
name = st.sidebar.selectbox("Contaminante", pollutants["name"])
p = pollutants[pollutants["name"] == name].iloc[0]
common.sidebar_footer()

# ------------------------------------------------------------------ FR7
st.subheader(f"Instalaciones y {name} por distrito")
districts = data.query(q.districts(p["property"]))
districts["stations"] = districts["stations"].fillna(0)
districts["mean"] = districts["mean"].astype(float)
st.dataframe(
    districts[["name", "facilities", "stations", "mean", "wikidata"]],
    hide_index=True, width="stretch",
    column_config={
        "name": "Distrito",
        "facilities": st.column_config.NumberColumn("Instalaciones", format="%d"),
        "stations": st.column_config.NumberColumn(f"Estaciones que miden {name}", format="%d"),
        "mean": st.column_config.NumberColumn(f"Media anual ({p['unit']})", format="%.1f"),
        "wikidata": st.column_config.LinkColumn("Wikidata", display_text="Ver en Wikidata"),
    },
)
st.caption("Media de los valores diarios válidos de 2024 de las estaciones situadas en el "
           "distrito. Vacío: el distrito no tiene ninguna estación que mida este contaminante.")

# ------------------------------------------------------------------ FR6
st.subheader("¿Dónde hay mejor aire para tu deporte?")
types = data.query(q.facility_types())
type_name = st.selectbox("Tipo de instalación", types["name"],
                         index=int((types["name"] == "Calistenia").idxmax()))
facility_type = types[types["name"] == type_name].iloc[0]["type"]
ranking = data.query(q.ranking(facility_type, p["property"]))
ranking["instalacion"] = ranking["name"].map(common.short_name)
ranking["ficha"] = ranking["facility"].map(
    lambda iri: f"/ficha?facility={common.slug(iri)}")
st.dataframe(
    ranking[["instalacion", "district", "stationName", "distance", "mean", "ficha"]].head(10),
    hide_index=True, width="stretch",
    column_config={
        "instalacion": "Instalación", "district": "Distrito",
        "stationName": "Estación más cercana",
        "distance": st.column_config.NumberColumn("Distancia (km)", format="%.1f"),
        "mean": st.column_config.NumberColumn(f"Media anual de {name} ({p['unit']})", format="%.1f"),
        "ficha": st.column_config.LinkColumn("Ficha", display_text="Ver ficha"),
    },
)
st.caption(f"Las 10 instalaciones de tipo «{type_name}» cuya estación más cercana tuvo la "
           f"media anual más baja. Solo se listan las que tienen cerca una estación que mide "
           f"{name}.")
