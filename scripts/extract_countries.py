"""Extract countries data from countries.ts to countries-data.js"""
import re
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TS_FILE = BASE / "static" / "countries.ts"
JS_FILE = BASE / "static" / "countries-data.js"

def main():
    content = TS_FILE.read_text(encoding="utf-8")
    parts = content.split("new Country({")
    countries = []
    for part in parts[1:]:
        depth = 0
        end = 0
        for i, c in enumerate(part):
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == -1:
                    end = i
                    break
        block = part[:end]
        name = re.search(r'name:\s*"([^"]+)"', block)
        iso2 = re.search(r'iso2:\s*"([^"]+)"', block)
        country_code = re.search(r'countryCode:\s*"([^"]+)"', block)
        phone_format = re.search(r'phoneFormat:\s*"([^"]*)"', block)
        min_len = re.search(r'minLengthPhone:\s*(\d+)', block)
        max_len = re.search(r'maxLengthPhone:\s*(\d+)', block)
        if name and iso2 and country_code:
            countries.append({
                "name": name.group(1),
                "iso2": iso2.group(1),
                "countryCode": country_code.group(1),
                "phoneFormat": phone_format.group(1) if phone_format else "XXXXXXXXXX",
                "minLengthPhone": int(min_len.group(1)) if min_len else 9,
                "maxLengthPhone": int(max_len.group(1)) if max_len else 9,
            })
    js_content = "window.COUNTRIES = " + json.dumps(countries, ensure_ascii=False, indent=2) + ";\n"
    JS_FILE.write_text(js_content, encoding="utf-8")
    print(f"Extracted {len(countries)} countries to {JS_FILE}")

if __name__ == "__main__":
    main()
