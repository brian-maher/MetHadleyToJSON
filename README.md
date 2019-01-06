# MetHadleyToJSON
Converts current Hadley historical data from the Met Office website to JSON.

This script downloads current data files from the Met Office Hadley Centre
Central England Temperature Data repository (link below) and converts the
data into a JSON file in the format:

{
    "year" {
        "month": {
            "day": {
                "min": ...,
                "mean": ...,
                "max": ...
            }
        }
    }
}

Temperatures are in degrees c - floating point to 1dp. Invalid dates from
the source data are ignored, and invalid values are stored as -999. Invalid
values found are logged (by default to conversion.log).

Data source:
https://www.metoffice.gov.uk/hadobs/hadcet/data/download.html