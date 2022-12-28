import csv

if __name__ == "__main__":
    station_dict = {}
    with open('cta_stations.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0 or line_count == 1:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                station_name = row[3] # STATION_DESCRIPTIVE_NAME (aka station name)
                station_id = row[4]   # MAP_ID (aka station id)
                if station_name not in station_dict:
                    station_dict[station_name] = station_id
                # else:
                    # print(f'Duplicate key: {station_name}')
                line_count += 1
        print(f'Processed {line_count} lines.')
        print(len(station_dict))
        print(station_dict)
        # print(station_dict['Dempster-Skokie (Yellow Line)'])
    
    with open('output.txt', "w") as f:
        f.write("station_dict = ")
        f.write(str(station_dict))