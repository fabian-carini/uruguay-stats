#! /usr/bin/env python

import argparse
import csv
import re
import sys
from pathlib import Path


def parse_format_standard(content):
    """Parses Formats 1, 2, and 3 using spacing-based column splits."""
    results = []
    valid_companies = {"ABITAB", "REDPAGOS", "ANDA"}

    # Auto-detect if this format uses row numbers (Format 3)
    has_row_indices = bool(
        re.search(r"^\s*0\s+DIRECCI[OÓ]N", content, re.MULTILINE | re.IGNORECASE)
    )

    for line in content.splitlines():
        clean_line = line.replace("\x0c", "").rstrip("\n\r ")

        if not clean_line:
            continue

        if has_row_indices:
            clean_line = re.sub(r"^\s*\d+\s+", "", clean_line)

        if clean_line.startswith(" ") or clean_line.upper().startswith("DIRECCI"):
            continue

        if re.match(r"^\s*\d{2}/\d{2}/\d{4}", clean_line) or re.match(
            r"^\s*\d+-\d+\s*$", clean_line
        ):
            continue

        columns = re.split(r"\s{2,}", clean_line)

        if len(columns) >= 1:
            address = columns[0].strip()
            company = columns[-1].strip() if len(columns) > 1 else "UNKNOWN"

            if company.upper() not in valid_companies:
                company = "UNKNOWN"
            else:
                company = company.upper()

            # Drop trailing phone numbers glued to the address
            # (e.g., 2203-38-44, 481.76.07, 305.37.82 AL 83)
            phone_pattern = (
                r"\s+(?:[0-9][0-9\.\-\s,]{5,15}[0-9](?:\s*AL\s*\d+)?(?:\s*int\.?\s*\d+)?|\d{7,})$"
            )
            address = re.sub(phone_pattern, "", address, flags=re.IGNORECASE).strip()

            # Slice the string at 'esq', 'esquina', or 'entre' to drop intersections
            address = re.split(r"(?i)\s+(esq\.|esq|esquina|entre|casi)\s+", address)[0].strip()

            if address:
                results.append((address, company))

    return results


def parse_format_4(content):
    """Parses Format 4 using a spatial state machine to handle multi-line wrapping."""
    results = []
    buffer_comp = []
    buffer_addr = []

    # Phone matching pattern
    phone_pattern = (
        r"\s+(?:[0-9][0-9\.\-\s,]{5,15}[0-9](?:\s*AL\s*\d+)?(?:\s*int\.?\s*\d+)?|\d{7,})\s*$"
    )

    for line in content.splitlines():
        clean_line = line.replace("\x0c", "").rstrip("\n\r ")
        if not clean_line:
            continue

        # Skip headers and pagination footers
        if re.match(r"^\s*\d{2}/\d{2}/\d{4}", clean_line) or re.match(
            r"^\s*\d+-\d+\s*$", clean_line
        ):
            continue
        if (
            "Empresa Contratista" in clean_line
            or "Listado Pagos" in clean_line
            or "Nombre de Local" in clean_line
        ):
            continue

        # Strip phone numbers dynamically so they aren't confused for address chunks
        clean_line = re.sub(phone_pattern, "", clean_line, flags=re.IGNORECASE).rstrip()

        # Extract visual column tokens
        tokens = []
        for m in re.finditer(r"(?:[^\s]|\s(?!\s))+", clean_line):
            tokens.append({"text": m.group().strip(), "start": m.start()})

        if not tokens:
            continue

        # Determine if this is the "Main" line of a record by the MONTEVIDEO anchor
        mv_idx = next((i for i, t in enumerate(tokens) if t["text"] == "MONTEVIDEO"), -1)

        if mv_idx != -1:
            # ---> MAIN LINE <---
            comp_pieces = [t["text"] for t in tokens if t["start"] < 30]
            # Barrio is mv_idx + 1. Everything from mv_idx + 2 onwards is the Address
            addr_pieces = [t["text"] for t in tokens[mv_idx + 2 :]]

            if comp_pieces:
                buffer_comp.extend(comp_pieces)
            if addr_pieces:
                buffer_addr.extend(addr_pieces)

            full_comp = " ".join(buffer_comp).upper()
            full_addr = " ".join(buffer_addr)

            # Map the Company Name
            if "NUMMI" in full_comp:
                company = "REDPAGOS"
            elif "ANDA" in full_comp or "ASOCIACION NACIONAL" in full_comp:
                company = "ANDA"
            elif "ABITAB" in full_comp:
                company = "ABITAB"
            else:
                company = "UNKNOWN"

            # Clean the Address (truncate at 'esq', 'esquina', or 'entre')
            clean_addr = re.split(r"(?i)\s+(esq\.|esq|esquina|entre|casi)\s+", full_addr)[0].strip()

            if clean_addr:
                results.append((clean_addr, company))

            # Flush buffers for the next record
            buffer_comp, buffer_addr = [], []
        else:
            # ---> CONTINUATION LINE <---
            comp_pieces = [t["text"] for t in tokens if t["start"] < 30]
            # Address columns in pdftotext align heavily to the right.
            # 100+ is incredibly safe.
            addr_pieces = [t["text"] for t in tokens if t["start"] >= 100]

            if comp_pieces:
                buffer_comp.extend(comp_pieces)
            if addr_pieces:
                buffer_addr.extend(addr_pieces)

    return results


def parse_data(input_path):
    """Reads the file and routes to the correct parser based on the layout signatures."""
    with open(input_path, encoding="utf-8") as file:
        content = file.read()

    # Format routing
    if re.search(r"Empresa Contratista", content, re.IGNORECASE):
        return parse_format_4(content)
    else:
        return parse_format_standard(content)


def write_to_csv(data, output_path):
    """Writes the extracted data to a CSV file."""
    with open(output_path, "w", encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file)
        writer.writerow(["Address", "Company"])  # Header
        writer.writerows(data)


def main(input_path, output_path):
    try:
        data = parse_data(input_path)
        write_to_csv(data, output_path)
        print(f"Successfully extracted {len(data)} records to '{output_path}'.")
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_path}'.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract Addresses and Companies from a pdftotext -layout output file."
    )
    parser.add_argument("input_file", help="Path to the parsed text file (e.g., data.txt)")
    args = parser.parse_args()

    input_path = Path(args.input_file)
    output_path = input_path.with_suffix(".csv")

    if input_path == output_path:
        output_path = input_path.with_name(f"{input_path.stem}_parsed.csv")

    main(input_path, output_path)
