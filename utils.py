import json

template = json.load(open("template.json", "r"))

def is_valid_bibtex(bibtex):
    pass

def get_author_info(bibtex_author):
    # TODO verify other conditions to split author names

    if "and" in bibtex_author:
        names = bibtex_author.split("and")
        return [{"name": name.strip()} for name in names]
    else:
        # assume there is only one author
        name = bibtex_author
        return [{"name": name.strip()}]


def get_metadata(bibtex):
    metadata = {
        "metadata": {
            "title": bibtex["title"],
            "description": bibtex["abstract"] if "abstract" in bibtex else "",
            "creators": get_author_info(bibtex["author"]),
            "partof_pages": bibtex["pages"] if "pages" in bibtex else "",
            #         "keywords": [ "apple", "pear" ],
            "upload_type": "publication",
            "publication_type": "conferencepaper",
            "access_right": "open",
            "imprint_isbn": template["isbn"],
            "imprint_publisher": template["publisher"],
            #         "imprint_place": "Durham, UK",
            "imprint_publisher": bibtex["publisher"] if "publisher" in bibtex else "",
            "partof_title": bibtex["booktitle"] if "booktitle" in bibtex else "",
            #         "license": { "id": "CC-BY-SA-4.0" },
            "conference_dates": f"{bibtex['month']}-{bibtex['year']}",
            "conference_place": bibtex["address"] if "address" in bibtex else "",
            "conference_title": bibtex["booktitle"] if "booktitle" in bibtex else "",
            #         "conference_url": "https://educationaldatamining.org/edm2022/",
            #         "publication_date": "2022-07-25",
            "communities": template["community_identifier"],
            "prereserve_doi": True,
            "contributors": template["contributors"],
        }
    }
    return metadata
