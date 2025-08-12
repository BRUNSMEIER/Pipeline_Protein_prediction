#!/usr/bin/env python3
"""
fasta2json.py – Convert a FASTA file to the JSON schema required by Protenix.

The script supports one or many FASTA records.  Only the first sequence is
written to the "sequence" field (to match the example file you provided);
the total number of records is stored in "count".

Usage:
    python fasta2json.py <input.fasta> [--out output.json]
"""

import argparse
import json
import pathlib
import sys


def parse_fasta(path: pathlib.Path):
    """Return a list of (header, sequence) tuples found in a FASTA file."""
    records, header, seq = [], None, []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header:                              # save the previous record
                    records.append((header, "".join(seq)))
                header, seq = line[1:], []
            else:
                seq.append(line)
        if header:
            records.append((header, "".join(seq)))

    if not records:
        raise ValueError("No valid FASTA records found.")
    return records


def build_json(records):
    """Create a Protenix-style JSON object."""
    header, seq = records[0]           # use the first record as the sequence
    count = len(records)               # total number of FASTA records
    name = (header.split() or ["target"])[0]

    return [
        {
            "sequences": [
                {
                    "proteinChain": {
                        "sequence": seq,
                        "count": count
                    }
                }
            ],
            "name": name
        }
    ]


def main():
    parser = argparse.ArgumentParser(description="Convert FASTA to Protenix JSON.")
    parser.add_argument("fasta", help="input FASTA file")
    parser.add_argument("--out", help="output JSON file (default: <input>.json)")
    args = parser.parse_args()

    in_path = pathlib.Path(args.fasta)
    if not in_path.is_file():
        sys.exit(f"Input FASTA not found: {in_path}")

    out_path = pathlib.Path(args.out) if args.out else in_path.with_suffix(".json")

    data = build_json(parse_fasta(in_path))
    with out_path.open("w") as fp:
        json.dump(data, fp, indent=2)

    print(f"✔ Wrote {out_path} (found {data[0]['sequences'][0]['proteinChain']['count']} FASTA record(s))")


if __name__ == "__main__":
    main()
