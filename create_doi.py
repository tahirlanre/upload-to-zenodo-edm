import argparse
import glob
import json
import requests
import time
import os

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from tqdm import tqdm

from config import ACCESS_TOKEN
from utils import get_metadata

BASE_URL = "https://sandbox.zenodo.org"
headers = {"Content-Type": "application/json"}
params = {"access_token": ACCESS_TOKEN}

def main(args):

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    for fname in tqdm(glob.glob(args.bibtex_files), desc="Parsing bibtex file"):
        with open(fname) as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)

        bibtex = bib_database.entries[0]

        # skip bibtex for the full proceedings
        if bibtex["ENTRYTYPE"] == "proceedings":
            continue

        metadata = get_metadata(bibtex)

        # add submission
        response = requests.post(f"{BASE_URL}/api/deposit/depositions", json={}, headers=headers, params=params)
        if response.status_code > 210:
            print(
                f"{bibtex['ID']} - Error happened during submission, status code: {response.status_code}"
            )
            continue

        deposition_id = response.json()["id"]

        # add metadata
        response = requests.put(
            f"{BASE_URL}/api/deposit/depositions/{deposition_id}",
            params=params,
            data=json.dumps(metadata),
            headers=headers,
        )
        if response.status_code > 210:
            print(
                f"{bibtex['ID']} - Error happened when adding metadata, status code: {response.status_code}"
            )
            continue

        doi = response.json()["metadata"]["prereserve_doi"]["doi"]
        bib_database.entries[0]["doi"] = doi

        output_path = os.path.join(args.output_dir, f"{bibtex['ID']}.bib")

        writer = BibTexWriter()
        with open(output_path, "w") as bibfile:
            bibfile.write(writer.write(bib_database))

        time.sleep(2)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bibtex_files",
        type=str,
        required=True,
        help="path to all bibtex files for papers to upload",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="path to store updated bibtex files"
    )

    args = parser.parse_args()

    main(args)
