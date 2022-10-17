# Upload-to-Zenodo-EDM

A simple script to create DOIs and upload papers to [Zenodo](http://zenodo.org) for [ International Conference on Educational Data Mining](https://educationaldatamining.org/conferences/).

_To avoid junk uploads to the the real Zenodo account, the scripts use the Zenodo sandbox (`sandbox.zenodo.org`). Once you're sure things are working as intended, then replace `sandbox.zenodo.org` with `zenodo.org`._

## Premilinaries
1. A Zenodo personal access token with `deposit:write` is required. Please visit [Zenodo](https://zenodo.org/account/settings/applications/) to get one. Add the token to [config.py](config.py)

2. To group all uploads to a Zenodo _Community_ (that represent the conference series), [create it](https://zenodo.org/communities/new/) and note its ID. 

3. Update [template.json](template.json) with the information about the current conference series.

## Requirements
```
python==3.7
bibtexparser==1.4.0
tqdm==4.63.0
```

## Basic Usage
- To create DOIs and update the bibtex files:
```
python create_doi.py 
         --bibtex_files <bibtex_files_path> 
         --output_dir <updated_bibtex_files_path>
```

- Go to the [Upload page](https://zenodo.org/deposit), to check the submissions. Then run the code below to upload the papers to Zenodo:
```
python upload_to_zenodo.py 
         --upload_type papers 
         --bibtex_files <updated_bibtex_files_path> 
         --data_path <path_to_paper_pdfs>
```
- To upload the proceedings to Zenodo:
```
python upload_to_zenodo.py 
         --upload_type proceedings 
         --proceedings_bibtex_file <proceedings_bibtex_file_path> 
         --proceedings_file_path <proceedings_file_path>
```


