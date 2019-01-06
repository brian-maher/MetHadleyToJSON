#!/usr/bin/env python3

'''
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
'''

import json
import logging
from urllib.request import build_opener

'''
__author__ = "Brian Maher"
__copyright__ = "N/A"
__credits__ = ["Brian Maher"]
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Brian Maher"
__email__ = "brian.maher@kcl.ac.uk"
__status__ = "Prototype"
'''

min_url = 'https://www.metoffice.gov.uk/hadobs/hadcet/cetmindly1878on_urbadj4.dat'  # noqa
mean_url = 'https://www.metoffice.gov.uk/hadobs/hadcet/cetdl1772on.dat'  # noqa
max_url = 'https://www.metoffice.gov.uk/hadobs/hadcet/cetmaxdly1878on_urbadj4.dat'  # noqa

url_referrer = 'https://www.metoffice.gov.uk/hadobs/hadcet/data/download.html'  # noqa

outfile = 'data.json'
logfile = 'conversion.log'

month_list = ['January', 'February', 'March', 'April', 'May',
              'June', 'July', 'August', 'September', 'October',
              'November', 'December']

days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
days_in_month_leap = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

counts = {}


def _process(data, inurl, temptype):
    counts[temptype] = 0

    opener = build_opener()
    opener.addheaders = [('Referer', url_referrer)]
    print("Downloading: {}".format(inurl))
    with opener.open(inurl) as f:
        for line in f.readlines():
            segment = line.split()
            year = int(segment[0])
            day = int(segment[1])
            if year not in data:
                new_year = {m: {} for m in month_list}
                for i in range(0, 12):
                    if year % 4 == 0:
                        # Leap year!
                        new_year[month_list[i]] = {
                            k: {} for k in range(1, days_in_month_leap[i] + 1)}
                    else:
                        new_year[month_list[i]] = {
                            k: {} for k in range(1, days_in_month[i] + 1)}
                data[year] = new_year

            for month in range(2, 14):
                temp = float(segment[month])
                if temp == -999.0:
                    # Either we have a day that doesn't exist
                    # or invalid data
                    if year % 4 == 0:
                        # leap year
                        if day > days_in_month_leap[month - 2]:
                            logging.debug(
                                'Invalid date ({}): {}/{}/{}'.format(
                                    temptype, day,
                                    month_list[month - 2], year))
                        else:
                            temp = -999
                            logging.error(
                                "Invalid data ({}): {}/{}/{}".format(
                                    temptype, day,
                                    month_list[month - 2], year))
                    else:
                        if day > days_in_month[month - 2]:
                            logging.debug(
                                'Invalid date ({}): {}/{}/{}'.format(
                                    temptype, day,
                                    month_list[month - 2], year))
                        else:
                            temp = -999
                            logging.error(
                                "Invalid data ({}): {}/{}/{}".format(
                                    temptype, day,
                                    month_list[month - 2], year))

                else:
                    temp = temp / 10
                    data[year][month_list[month - 2]][day][temptype] = temp
                    counts[temptype] += 1


def main():

    data = {}

    logging.basicConfig(filename='conversion.log',
                        level=logging.INFO,
                        format='%(levelname)s: %(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S')

    _process(data, min_url, 'min')
    _process(data, mean_url, 'mean')
    _process(data, max_url, 'max')

    # Report our findings!
    logging.info('Found data for {} years'.format(len(data)))

    for k, v in counts.items():
        logging.info("Found {} values for {}".format(v, k))

    logging.info("Found {} total values".format(sum(counts.values())))

    with open(outfile, 'w') as fp:
        json.dump(data, fp, sort_keys=True, indent=4)

    logging.info('Output written to {}'.format(outfile))


if __name__ == "__main__":
    main()
