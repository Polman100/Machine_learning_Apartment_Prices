import tkinter as tk
from tkinter import messagebox
from contextlib import suppress
from src.predict import predict_single

# ========================
# Konfiguracja
# ========================
MODEL_PATH = "models/xgb_final.pkl"

DEFAULT_VALUES = {
    "city": "gdynia",
    "buildYear": "2005",
    "squareMeters": "50.0",
    "rooms": "2",
    "floor": "1",
    "floorCount": "4",
    "hasParkingSpace": "no",
    "hasBalcony": "no",
    "hasElevator": "no",
    "hasSecurity": "no",
    "hasStorageRoom": "no",
    "poiCount": "3",
    "centreDistance": "5.0",
    "clinicDistance": "2.0",
    "restaurantDistance": "1.0",
    "collegeDistance": "4.0"
}

FIELDS = {
    "city": "Miasto",
    "buildYear": "Rok budowy",
    "squareMeters": "Powierzchnia (m²)",
    "rooms": "Liczba pokoi",
    "floor": "Piętro",
    "floorCount": "Liczba pięter w budynku",
    "hasParkingSpace": "Parking",
    "hasBalcony": "Balkon",
    "hasElevator": "Winda",
    "hasSecurity": "Ochrona",
    "hasStorageRoom": "Komórka lokatorska",
    "poiCount": "Liczba punktów POI w okolicy (500 m)",
    "centreDistance": "Odległość od centrum (km)",
    "clinicDistance": "Odległość od kliniki (km)",
    "restaurantDistance": "Odległość od punktu gastronomicznego (km)",
    "collegeDistance": "Odległość od uczelni (km)"
}

CITY_OPTIONS = [
    "bialystok", "bydgoszcz", "czestochowa", "gdansk", "gdynia", "katowice",
    "krakow", "lodz", "lublin", "poznan", "radom", "rzeszow",
    "szczecin", "warszawa", "wroclaw"
]

YES_NO_OPTIONS = ["tak", "nie"]

# Pola typu float (z 1 miejscem po przecinku)
FLOAT_FIELDS = {"squareMeters", "centreDistance", "clinicDistance", "restaurantDistance", "collegeDistance"}
# Pola typu int
INT_FIELDS = {"buildYear", "rooms", "floor", "floorCount", "poiCount"}


# ========================
# Walidacja
# ========================
def validate_number(new_value, field_type):
    """
    Waliduje wpisaną wartość w polu liczbowym.
    Pozwala na puste pole, cyfry dla int oraz liczby zmiennoprzecinkowe z maksymalnie jednym miejscem po przecinku dla float.

    Parametry:
        new_value (str): Nowa wartość wpisana przez użytkownika.
        field_type (str): Typ pola ('int' lub 'float').

    Zwraca:
        bool: True jeśli wartość jest poprawna, False w przeciwnym razie.
    """
    # Pozwól na puste pole
    if new_value == "":
        return True
    # Walidacja dla int
    if field_type == "int":
        return new_value.isdigit()
    # Walidacja dla float
    elif field_type == "float":
        with suppress(ValueError):
            val = float(new_value)
            # Sprawdź czy jest maksymalnie jedno miejsce po przecinku
            parts = new_value.split(".")
            if len(parts) == 2 and len(parts[1]) > 1:
                return False
            return True
    return False


# ========================
# Predykcja
# ========================
def predict_price():
    """
    Pobiera wartości z pól formularza, przygotowuje słownik cech,
    wywołuje funkcję predykcji i wyświetla wynik w oknie dialogowym.

    Krok po kroku:
      1. Tworzy pusty słownik cech.
      2. Iteruje po wszystkich polach formularza.
      3. Pobiera wartość z każdego widgetu (Spinbox lub StringVar).
      4. Przekształca wartości na odpowiedni typ (int, float, tekst, tak/nie).
      5. Wywołuje funkcję predict_single z przygotowanymi cechami.
      6. Wyświetla wynik predykcji w oknie dialogowym.
      7. Obsługuje wyjątki i pokazuje komunikat błędu.

    Zwraca:
        None
    """
    try:
        features = {}
        for key, widget in entries.items():
            # Pobierz wartość z widgetu
            if isinstance(widget, tk.StringVar):
                value = widget.get().strip().lower()
                # Walidacja miasta
                if key == "city":
                    if not value:
                        raise ValueError("Miasto nie może być puste.")
                    features[key] = value
                else:
                    # Zamiana na 'yes'/'no' dla pól binarnych
                    features[key] = "yes" if value == "tak" else "no"
            else:
                value = widget.get().strip()
                # Zamiana na int/float dla pól liczbowych
                if key in INT_FIELDS:
                    features[key] = int(value) if value else 0
                elif key in FLOAT_FIELDS:
                    features[key] = round(float(value), 1) if value else 0.0
                else:
                    features[key] = value or ""
        # Wywołanie predykcji
        price = predict_single(features, artifact_path=MODEL_PATH, mode="xgb")
        # Wyświetlenie wyniku
        messagebox.showinfo("Predykcja ceny", f"Przewidywana cena mieszkania: {price:,.2f} PLN")
    except Exception as e:
        # Obsługa błędów
        messagebox.showerror("Błąd", f"Coś poszło nie tak: {e}")


# ========================
# Reset pól
# ========================
def reset_fields():
    """
    Resetuje wszystkie pola formularza do wartości domyślnych.

    Krok po kroku:
      1. Iteruje po wszystkich polach formularza.
      2. Ustawia wartość domyślną dla każdego widgetu (Spinbox/StringVar).
      3. Pola binarne ustawia na 'nie', miasto na 'gdynia', pozostałe na wartość z DEFAULT_VALUES.

    Zwraca:
        None
    """
    for key, widget in entries.items():
        default = DEFAULT_VALUES.get(key, "")
        if isinstance(widget, tk.StringVar):
            if key in ["hasParkingSpace", "hasBalcony", "hasElevator", "hasSecurity", "hasStorageRoom"]:
                widget.set("nie")
            elif key == "city":
                widget.set("gdynia")
        else:
            widget.delete(0, tk.END)
            widget.insert(0, default)


# ========================
# GUI
# ========================
root = tk.Tk()
root.title("Predykcja cen mieszkań")
entries = {}

for i, (key, label) in enumerate(FIELDS.items()):
    # Dodaj etykietę pola
    tk.Label(root, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
    if key == "city":
        # Pole wyboru miasta (dropdown)
        var = tk.StringVar(value=DEFAULT_VALUES["city"])
        dropdown = tk.OptionMenu(root, var, *CITY_OPTIONS)
        dropdown.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        entries[key] = var
    elif key in ["hasParkingSpace", "hasBalcony", "hasElevator", "hasSecurity", "hasStorageRoom"]:
        # Pola binarne jako RadioButtony "Tak"/"Nie"
        var = tk.StringVar(value="nie")
        frame = tk.Frame(root)
        frame.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        tk.Radiobutton(frame, text="Tak", variable=var, value="tak").pack(side="left", padx=2)
        tk.Radiobutton(frame, text="Nie", variable=var, value="nie").pack(side="left", padx=2)
        entries[key] = var
    else:
        # Pola liczbowe jako Spinbox z walidacją i odpowiednim krokiem
        field_type = "float" if key in FLOAT_FIELDS else "int"
        vcmd = (root.register(validate_number), "%P", field_type)
        if field_type == "int":
            spin = tk.Spinbox(root, from_=0, to=9999, width=28, validate="key", validatecommand=vcmd)
            spin.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            spin.delete(0, tk.END)
            spin.insert(0, DEFAULT_VALUES[key])
            entries[key] = spin
        else:
            spin = tk.Spinbox(root, from_=0, to=9999, increment=0.1, format="%.1f", width=28, validate="key", validatecommand=vcmd)
            spin.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            spin.delete(0, tk.END)
            spin.insert(0, DEFAULT_VALUES[key])
            entries[key] = spin

# Dodaj przycisk predykcji
tk.Button(root, text="Zrób czary-mary", command=predict_price).grid(row=len(FIELDS), column=0, columnspan=2, pady=10)
# Dodaj przycisk resetowania pól
tk.Button(root, text="Resetuj wartości", command=reset_fields).grid(row=len(FIELDS)+1, column=0, columnspan=2, pady=5)

root.mainloop()
