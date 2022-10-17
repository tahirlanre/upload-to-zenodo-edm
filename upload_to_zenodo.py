import argparse
from distutils.command.upload import upload
import glob
import json
import requests

from tqdm import tqdm
import bibtexparser

from config import ACCESS_TOKEN
from utils import get_metadata

BASE_URL = "https://sandbox.zenodo.org"
headers = {"Content-Type": "application/json"}
params = {"access_token": ACCESS_TOKEN}

def get_records_from_zenodo():
    records = []
    for i in range(1, 4):
        response = requests.get(
            f"{BASE_URL}/api/deposit/depositions",
            params={"access_token": ACCESS_TOKEN, "page": i, "size": 50},
            headers=headers,
        )
        for record in response.json():
            records.append(record)
    return records


def get_dois_from_bibtex(bibtex_files):
    bibtex_dict = {}
    for fname in tqdm(bibtex_files, desc="Parsing bibtex file"):
        with open(fname) as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)

        bibtex = bib_database.entries[0]
        bibtex_dict[bibtex["doi"]] = bibtex["ID"]
    return bibtex_dict


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--upload_type",
        type=str,
        choices=["papers", "proceedings"],
        required=True,
        help="file type to upload to Zenodo"
    )
    parser.add_argument(
        "--bibtex_files",
        type=str,
        help="path to all updated bibtex files for papers to upload"
    )
    parser.add_argument(
        "--data_path",
        type=str,
        help="path to papers to upload"
    )
    parser.add_argument(
        "--proceedings_bibtex_file",
        type=str,
        help="path to bibtex file for proceedings"
    )
    parser.add_argument(
        "--proceedings_file_path",
        type=str,
        help="path to proceedings file"
    )
    args = parser.parse_args()

    # Sanity checks
    if args.upload_type == "papers":
        if args.bibtex_files is None:
            raise ValueError("Please provide path to bibtex files")
        if args.data_path is None:
            raise ValueError("Please provide data for papers to upload")
    if args.upload_type == "proceedings":
        if args.proceedings_bibtex_file is None:
            raise ValueError("Please provide path to bibtex files")
        if args.proceedings_file_path is None:
            raise ValueError("Please provide path to proceedings file")

    return args

def main():
    
    args = parse_args()
    upload_type = args.upload_type

    if upload_type == "papers":
        # get list of created records from Zenodo
        records = get_records_from_zenodo()

        # get dois from updated bibtex files
        bibtex_dict = get_dois_from_bibtex(
            args.bibtex_files
        )  

        # upload files
        for record in tqdm(records, desc="Uploading files"):
            deposition_id = record["id"]
            paper_id = bibtex_dict[record["metadata"]["prereserve_doi"]["doi"]]
            files = {"file": open(f"{args.data_path}/{paper_id}.pdf", "rb")}
            response = requests.post(
                f"{BASE_URL}/api/deposit/depositions/{deposition_id}/files",
                params=params,
                files=files,
            )
            if response.status_code > 210:
                print(f"Error uploading paper - {paper_id}")
                continue

        # publish records
        for record in tqdm(records, desc="Publishing records"):
            deposition_id = record["id"]
            response = requests.post(
                f"{BASE_URL}/api/deposit/depositions/{deposition_id}/actions/publish",
                params=params,
            )

            if response.status_code > 210:
                paper_id = bibtex_dict[record["metadata"]["prereserve_doi"]["doi"]]
                print(f"Error publishing record - paper {paper_id}")
                continue

    elif upload_type == "proceedings":
        bibtex_file = args.proceedings_bibtex_file

        # create record for proceedings on Zenodo
        response = requests.post(
            f"{BASE_URL}/api/deposit/depositions",
            headers=headers,
            params=params,
        )

        bucket_url = response.json()["links"]["bucket"]
        deposition_id = response.json()["id"]

        proceedings_file = args.proceedings_file_path
        with open(proceedings_file, "rb") as fp:
            r = requests.put(
                f"{bucket_url}/{proceedings_file}",
                data=fp,
                params=params,
            )

        with open(bibtex_file) as fp:
            bib_database = bibtexparser.load(fp)

            bibtex = bib_database.entries[0]

            metadata = get_metadata(bibtex)
            
            # upload proceedings file to Zenodo
            response = requests.put(
                f"{BASE_URL}/api/deposit/depositions/{deposition_id}",
                params=params,
                data=json.dumps(metadata),
                headers=headers,
            )

            # publish record
            response = requests.post(
                f"{BASE_URL}/api/deposit/depositions/{deposition_id}/actions/publish",
                params=params,
            )

if __name__ == "__main__":
    main()
