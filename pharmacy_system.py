"""Track pharmacy stock and prescription dispensing."""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path


class PharmacySystem:
    """Manage patient records, pharmacy stock, and prescriptions."""

    def __init__(self):
        """Initialize the database and in-memory pharmacy records."""
        self.connection = sqlite3.connect(":memory:")
        self.stock = {}
        self.prescriptions = []
        self.setup_database()

    def setup_database(self):
        """Create the patient table and add sample patient records."""
        with self.connection:
            self.connection.execute(
                "CREATE TABLE patients "
                "(id TEXT, name TEXT, allergy TEXT)"
            )
            self.connection.executemany(
                "INSERT INTO patients VALUES (?, ?, ?)",
                [
                    ("P1", "Kavya", "penicillin"),
                    ("P2", "Arjun", "none"),
                    ("P3", "Meena", "ibuprofen"),
                ],
            )

    def find_patient(self, name):
        """Return matching patient IDs and allergy information."""
        query = "SELECT id, allergy FROM patients WHERE name = ?"
        return self.connection.execute(query, (name,)).fetchall()

    def add_stock(self, drug, units, expiry, batch_log=None):
        """Add a valid batch of medicine to stock."""
        if units <= 0:
            raise ValueError("Units must be greater than zero.")

        datetime.strptime(expiry, "%Y-%m-%d")
        if batch_log is None:
            batch_log = []

        current_units = self.stock.get(drug, {}).get("units", 0)
        self.stock[drug] = {
            "units": current_units + units,
            "expiry": expiry,
        }
        batch_log.append((drug, units))
        return len(batch_log)

    def dispense(self, patient_name, drug, units):
        """Dispense medicine when the patient and stock allow it."""
        patients = self.find_patient(patient_name)
        if not patients or units <= 0:
            return False

        patient_id, allergy = patients[0]
        has_allergy = (
            allergy.casefold() != "none"
            and allergy.casefold() in drug.casefold()
        )
        if has_allergy:
            print(f"Allergy warning for {patient_name}")
            return False

        medicine = self.stock.get(drug)
        if medicine is None or medicine["units"] < units:
            return False

        medicine["units"] -= units
        self.prescriptions.append(
            {
                "patient": patient_id,
                "drug": drug,
                "units": units,
                "time": datetime.now().isoformat(timespec="seconds"),
            }
        )
        return True

    def expiring_soon(self, days=30):
        """Return medicine names expiring within the given number of days."""
        now = datetime.now()
        soon = []

        for drug, details in self.stock.items():
            expiry = datetime.strptime(details["expiry"], "%Y-%m-%d")
            if (expiry - now).days < days:
                soon.append(drug)

        return soon

    def export_prescriptions(self, file="prescriptions.json"):
        """Write prescriptions to a JSON file."""
        with Path(file).open("w", encoding="utf-8") as output_file:
            json.dump(self.prescriptions, output_file, indent=2)

    def load_stock(self, file="stock.json"):
        """Load stock from a valid JSON file when one is available."""
        try:
            with Path(file).open(encoding="utf-8") as stock_file:
                loaded_stock = json.load(stock_file)
        except FileNotFoundError:
            return
        except (OSError, json.JSONDecodeError) as error:
            logging.warning("Could not load stock: %s", error)
            return

        if not isinstance(loaded_stock, dict):
            logging.warning("Stock data must be a JSON object.")
            return

        self.stock = loaded_stock

    def print_stock(self):
        """Print each medicine's units and expiry date."""
        print("Pharmacy Stock")
        for drug, details in self.stock.items():
            print(
                f"{drug} -> {details['units']} units, "
                f"expires {details['expiry']}"
            )


def main():
    """Run the pharmacy tracker demonstration."""
    pharmacy = PharmacySystem()
    pharmacy.load_stock()

    pharmacy.add_stock("Paracetamol", 100, "2027-03-01")
    pharmacy.add_stock("Amoxicillin", 20, "2027-12-31")
    pharmacy.add_stock("Penicillin", 50, "2027-01-15")
    pharmacy.add_stock("Ibuprofen", 15, "2026-11-30")

    print(
        "Arjun gets Amoxicillin:",
        pharmacy.dispense("Arjun", "Amoxicillin", 30),
    )
    print(
        "Kavya gets Penicillin:",
        pharmacy.dispense("Kavya", "Penicillin", 10),
    )
    print(
        "Meena gets ibuprofen:",
        pharmacy.dispense("Meena", "ibuprofen", 2),
    )
    print(
        "Unknown patient:",
        pharmacy.dispense("Ghost", "Paracetamol", 5),
    )

    name = input("Patient name to look up (Enter for Arjun): ") or "Arjun"
    print("Lookup result:", pharmacy.find_patient(name))
    print("Expiring within 30 days:", pharmacy.expiring_soon())

    pharmacy.export_prescriptions()
    pharmacy.print_stock()


if __name__ == "__main__":
    main()

