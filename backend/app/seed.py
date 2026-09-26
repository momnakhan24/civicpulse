from app.database import SessionLocal
from app.models import Complaint, Category, Priority, Status

SEED_COMPLAINTS = [
    ("Burst water pipe flooding street near masjid since fajr time", "Gulshan Block 5", Category.water, Priority.high),
    ("No electricity in our area since yesterday evening, transformer maybe burnt", "Nazimabad Block 2", Category.electricity, Priority.high),
    ("Garbage not collected for one week, very bad smell everywhere", "Korangi Sector 4", Category.sanitation, Priority.normal),
    ("Big pothole on main road causing bike accidents daily", "Shahrah-e-Faisal", Category.roads, Priority.high),
    ("Streetlight not working near park, kids scared to play at night", "PECHS Block 6", Category.streetlights, Priority.normal),
    ("Water pipeline leaking continuously wasting so much water", "Malir Cantt", Category.water, Priority.normal),
    ("Frequent power outages every day for two hours minimum", "North Nazimabad", Category.electricity, Priority.normal),
    ("Sewerage overflow on street, water entering houses", "Liaquatabad", Category.sanitation, Priority.high),
    ("Road completely broken after rain, cars getting stuck", "Landhi", Category.roads, Priority.high),
    ("All streetlights on our block are off since a month", "Gulistan-e-Johar", Category.streetlights, Priority.low),
    ("Low water pressure whole week, tank not filling properly", "DHA Phase 2", Category.water, Priority.low),
    ("Electric wire hanging loose near school, very dangerous", "Federal B Area", Category.electricity, Priority.high),
    ("Trash piling up near market, stray animals gathering", "Saddar", Category.sanitation, Priority.normal),
    ("Speed breaker damaged, causing traffic jam every morning", "Clifton Block 4", Category.roads, Priority.normal),
    ("Streetlight flickering continuously, disturbing residents", "Gulshan Block 13", Category.streetlights, Priority.low),
    ("Water tanker did not come this week as scheduled", "Orangi Town", Category.water, Priority.normal),
    ("Voltage fluctuation damaging home appliances frequently", "Bahadurabad", Category.electricity, Priority.normal),
    ("Open manhole on road, very dangerous for pedestrians at night", "Tariq Road", Category.sanitation, Priority.high),
    ("Road construction incomplete for six months now, dust everywhere", "Malir", Category.roads, Priority.normal),
    ("No streetlights on entire road, women feel unsafe walking", "Lyari", Category.streetlights, Priority.high),
    ("Water supply contaminated, smells bad and looks yellow", "Baldia Town", Category.water, Priority.high),
    ("Electricity meter reading wrong, bill too high this month", "Gulberg", Category.electricity, Priority.low),
    ("Dead animal lying on road for two days, health hazard", "Surjani Town", Category.sanitation, Priority.high),
    ("Footpath broken, pedestrians forced to walk on road", "II Chundrigar Road", Category.roads, Priority.normal),
    ("New streetlight pole installed but light never turned on", "Scheme 33", Category.streetlights, Priority.low),
    ("Water line burst near main market, road flooded completely", "Empress Market area", Category.water, Priority.high),
    ("Power breaker trips every time we use AC in summer", "Defence Phase 5", Category.electricity, Priority.normal),
    ("Drain blocked causing water to stagnate, mosquitoes breeding", "Nazimabad Block 4", Category.sanitation, Priority.normal),
    ("Road sinking near bridge, feels unsafe to drive over", "Sohrab Goth", Category.roads, Priority.high),
    ("Only half the streetlights work on our road", "Model Colony", Category.streetlights, Priority.normal),
    ("Water bill received but no water supply for two weeks", "Shah Faisal Colony", Category.water, Priority.normal),
    ("Underground cable exposed after roadwork, safety risk", "Airport Road", Category.electricity, Priority.high),
]


def run_seed():
    db = SessionLocal()
    try:
        existing_count = db.query(Complaint).count()
        if existing_count >= len(SEED_COMPLAINTS):
            print(f"Seed skipped: {existing_count} complaints already exist.")
            return

        added = 0
        for text, location, category, priority in SEED_COMPLAINTS:
            already_exists = db.query(Complaint).filter(Complaint.text == text).first()
            if already_exists:
                continue

            complaint = Complaint(
                text=text,
                location=location,
                category=category,
                priority=priority,
                status=Status.open,
                triaged_by="rules",
                triage_latency_ms=0,
            )
            db.add(complaint)
            added += 1

        db.commit()
        print(f"Seed complete: {added} new complaints added.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
