#!/usr/bin/env python3
import argparse
import json

def main():

    parser = argparse.ArgumentParser(description="Read JSON file and print with sorted keys")
    parser.add_argument('filename', type=str, help="Name of PROV-JSON file")
    args = parser.parse_args()

    filename = args.filename
    outfilename = filename.replace('.json', '-sorted.json')

    # load the data
    vo_data = json.load(open(filename))

    # write to json file
    with open(outfilename, 'w') as outfile:
       json.dump(vo_data, outfile, indent=4, sort_keys=True)


if __name__ == '__main__':
	main()