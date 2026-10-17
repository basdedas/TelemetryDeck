def parse_line(raw: bytes):
    """Turn one raw serial line into a dict, or None if it is not a data line."""
    line = raw.decode("ascii", errors="ignore").strip()
    if not line or line.startswith("#"):
        return None

    parts = line.split(",")
    if len(parts) != 6:
        return None
 
    try:
        return {
            "t": int(parts[0]) / 1000,      # ms -> seconds
            "temp": float(parts[1]),
            "pressure": float(parts[2]),
            "humidity": float(parts[3]),    # "nan" parses fine (BMP280)
            "pot": int(parts[4]),
            "enc": int(parts[5]),
        }
    except ValueError:
        return None