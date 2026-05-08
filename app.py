import streamlit as st
from fpdf import FPDF
from datetime import date
import io

st.set_page_config(page_title="Preiskalkulator", page_icon="💻", layout="centered")

st.markdown("""
<style>
div[data-testid="stNumberInput"] input { text-align: right; }
</style>
""", unsafe_allow_html=True)

st.title("Website Preiskalkulator")

# --- Projekttyp ---
st.subheader("Projekttyp")
typ = st.radio(
    "Typ",
    ["Statische Site", "CMS – Webflow", "CMS – Custom Code"],
    horizontal=True,
    label_visibility="collapsed"
)
typ_preise = {"Statische Site": 800, "CMS – Webflow": 1500, "CMS – Custom Code": 1800}
grundpreis = typ_preise[typ]

# --- Seiten ---
st.subheader("Seiten")
st.caption("Startseite im Grundpreis. Impressum & Datenschutz kostenlos.")
weitere_seiten = st.number_input("Weitere Seiten (à 80 €)", min_value=0, step=1, value=0)
seiten_preis = weitere_seiten * 80

# --- Extras ---
st.subheader("Extras")
col1, col2 = st.columns(2)
with col1:
    logo = st.checkbox("Logo-Design (+250 €)")
    formular = st.checkbox("Kontaktformular (+75 €)")
with col2:
    if typ == "CMS – Webflow":
        st.checkbox("Wartung + Hosting", disabled=True, value=False)
        st.caption("Bei Webflow zahlt der Kunde das Hosting selbst.")
        hosting = False
        hosting_preis = 0
    else:
        hosting = st.checkbox("Wartung + Hosting (Hostinger)")
        if hosting:
            hosting_preis = st.number_input("Monatliche Pauschale (€)", min_value=0, value=25, step=5)
        else:
            hosting_preis = 0

# --- Rabatt ---
st.subheader("Rabatt")
col_r1, col_r2 = st.columns(2)
with col_r1:
    rabatt_pct = st.number_input("Rabatt in %", min_value=0, max_value=100, value=0, step=5)
with col_r2:
    rabatt_eur = st.number_input("Oder fixer Betrag (€)", min_value=0, value=0, step=10)

# --- Angebot ---
st.subheader("Angaboten für")
col_a1, col_a2 = st.columns(2)
with col_a1:
    kunde = st.text_input("Kundenname", placeholder="z.B. Max Mustermann")
with col_a2:
    projekt = st.text_input("Projektbeschreibung", placeholder="z.B. Hausmeister Service Website")

# --- Berechnung ---
subtotal = grundpreis + seiten_preis
if logo: subtotal += 250
if formular: subtotal += 75

if rabatt_pct > 0:
    rabatt_betrag = round(subtotal * rabatt_pct / 100)
elif rabatt_eur > 0:
    rabatt_betrag = min(rabatt_eur, subtotal)
else:
    rabatt_betrag = 0

gesamt = subtotal - rabatt_betrag

# --- Zusammenfassung ---
st.divider()
st.subheader("Zusammenfassung")

positionen = []
positionen.append((typ, grundpreis))
if weitere_seiten > 0:
    positionen.append((f"{weitere_seiten} weitere Seite{'n' if weitere_seiten > 1 else ''} (à 80 €)", seiten_preis))
if logo:
    positionen.append(("Logo-Design", 250))
if formular:
    positionen.append(("Kontaktformular", 75))

for label, preis in positionen:
    col_l, col_r = st.columns([3, 1])
    col_l.write(label)
    col_r.write(f"{preis:,.0f} €".replace(",", "."))

if rabatt_betrag > 0:
    label_r = f"Rabatt ({rabatt_pct}%)" if rabatt_pct > 0 else "Rabatt"
    col_l, col_r = st.columns([3, 1])
    col_l.markdown(f"<span style='color:green'>{label_r}</span>", unsafe_allow_html=True)
    col_r.markdown(f"<span style='color:green'>−{rabatt_betrag:,.0f} €</span>".replace(",", "."), unsafe_allow_html=True)

st.markdown("---")
col_l, col_r = st.columns([3, 1])
col_l.markdown("**Einmalig gesamt**")
col_r.markdown(f"**{gesamt:,.0f} €**".replace(",", "."))

if hosting and hosting_preis > 0:
    col_l, col_r = st.columns([3, 1])
    col_l.caption("Wartung + Hosting (monatlich)")
    col_r.caption(f"{hosting_preis} €/Monat")

# --- PDF Export ---
st.divider()

def erstelle_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)

    heute = date.today().strftime("%d.%m.%Y")

    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 5, "Hannes — Freelance Webdesign", ln=True)
    pdf.cell(0, 5, "Dortmund", ln=True)
    pdf.ln(2)
    pdf.set_xy(20, 20)
    pdf.cell(0, 5, f"Angebot vom {heute}", align="R", ln=True)

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", size=22)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, "Angebot", ln=True)

    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, f"Fuer: {kunde or 'Kunde'}", ln=True)
    pdf.cell(0, 6, f"Projekt: {projekt or 'Website-Projekt'}", ln=True)

    pdf.ln(3)
    pdf.set_draw_color(220, 220, 220)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(130, 5, "LEISTUNG")
    pdf.cell(0, 5, "PREIS", align="R", ln=True)
    pdf.set_draw_color(230, 230, 230)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(40, 40, 40)
    for label, preis in positionen:
        pdf.cell(130, 7, label)
        pdf.cell(0, 7, f"{preis:,.0f} EUR".replace(",", "."), align="R", ln=True)

    if rabatt_betrag > 0:
        label_r = f"Rabatt ({rabatt_pct}%)" if rabatt_pct > 0 else "Rabatt"
        pdf.set_text_color(60, 140, 80)
        pdf.cell(130, 7, label_r)
        pdf.cell(0, 7, f"-{rabatt_betrag:,.0f} EUR".replace(",", "."), align="R", ln=True)
        pdf.set_text_color(40, 40, 40)

    pdf.ln(2)
    pdf.set_draw_color(180, 180, 180)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", size=13)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(130, 8, "Gesamt (einmalig)")
    pdf.cell(0, 8, f"{gesamt:,.0f} EUR".replace(",", "."), align="R", ln=True)

    if hosting and hosting_preis > 0:
        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(130, 7, "Wartung + Hosting (monatlich)")
        pdf.cell(0, 7, f"{hosting_preis} EUR/Monat", align="R", ln=True)

    pdf.ln(15)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "Alle Preise netto. Kein Umsatzsteuerausweis (Privatperson).", ln=True)
    pdf.cell(0, 5, "Angebot freibleibend. Gueltig fuer 30 Tage ab Ausstellungsdatum.", ln=True)

    return pdf.output()

pdf_bytes = erstelle_pdf()
dateiname = f"Angebot_{(kunde or 'Kunde').replace(' ', '_')}_{date.today().strftime('%d-%m-%Y')}.pdf"

st.download_button(
    label="Angebot als PDF herunterladen",
    data=bytes(pdf_bytes),
    file_name=dateiname,
    mime="application/pdf",
    use_container_width=True,
    type="primary"
)

st.caption("Alle Preise netto. Kein Umsatzsteuerausweis (Privatperson).")
