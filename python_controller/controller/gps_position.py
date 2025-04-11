import serial
import json

def convert_coord(coord, direction):
    """
    Wandelt einen Koordinatenstring im Format ddmm.mmmm (bei Breitengraden)
    oder dddmm.mmmm (bei Längengraden) in Dezimalgrad um.
    """
    if direction in ['N', 'S']:
        degrees = int(coord[:2])
        minutes = float(coord[2:])
    elif direction in ['E', 'W']:
        degrees = int(coord[:3])
        minutes = float(coord[3:])
    else:
        raise ValueError("Ungültige Richtungsangabe")
    
    decimal = degrees + minutes / 60
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def parse_gpgga(gpgga_string):
    """
    Parst einen GPGGA-String und gibt die extrahierten Daten als Dictionary zurück.
    
    Enthalten sind:
      - time: Zeitstempel (HHMMSS.SS)
      - latitude: Breitengrad in Dezimalgrad
      - longitude: Längengrad in Dezimalgrad
      - altitude: Höhe (falls vorhanden)
      - altitude_units: Einheit der Höhe
      - google_maps_link: Link zu Google Maps
    """
    parts = gpgga_string.strip().split(',')
    if len(parts) < 6:
        raise ValueError("Ungültiger GPGGA-Satz")
    
    data = {}
    data["time"] = parts[1]
    
    # Breitengrad umwandeln
    lat_str = parts[2]
    lat_dir = parts[3]
    data["latitude"] = convert_coord(lat_str, lat_dir)
    
    # Längengrad umwandeln
    lon_str = parts[4]
    lon_dir = parts[5]
    data["longitude"] = convert_coord(lon_str, lon_dir)
    
    # Optional: Höhe extrahieren
    try:
        data["altitude"] = float(parts[9])
        data["altitude_units"] = parts[10]
    except (ValueError, IndexError):
        data["altitude"] = None
        data["altitude_units"] = None
    
    # Google Maps Link generieren
    data["google_maps_link"] = (
        f"https://www.google.com/maps/search/?api=1&query={data['latitude']},{data['longitude']}"
    )
    return data

def main():
    # Konfiguration
    serial_port = "/dev/cu.usbmodem21301"
    server_address = "127.0.0.1"
    server_port = 6000
    debug = False  # Debug aktivieren, um mehr Informationen zu erhalten

    # Serielle Verbindung öffnen (typischerweise 4800 Baud für NMEA-Daten)
    try:
        ser = serial.Serial(serial_port, baudrate=4800, timeout=1)
        if debug:
            print(f"Verbunden mit Serial Port: {serial_port}")
            print(f"Server Adresse: {server_address} und Port: {server_port} (nicht verwendet)")
    except Exception as e:
        print(f"Fehler beim Öffnen des Serial Ports {serial_port}: {e}")
        return

    try:
        while True:
            # Lese eine Zeile vom Serial-Port
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if debug:
                print("Empfangen:", line)
            if line.startswith("$GPGGA"):
                try:
                    # GPGGA-Daten parsen
                    data = parse_gpgga(line)
                    if debug:
                        print("Geparste Daten:", data)
                    # Ausgabe der Daten als JSON-String
                    message = json.dumps(data, indent=2)
                    print("Daten (JSON):", message)
                except Exception as e:
                    if debug:
                        print("Fehler beim Parsen:", e)
    except KeyboardInterrupt:
        print("Beendet durch Benutzer.")
    finally:
        ser.close()

if __name__ == '__main__':
    main()
