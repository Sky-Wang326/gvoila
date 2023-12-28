import csv


def csvLogger(csv_head, data2bsave, save_path):
    file = open(save_path, 'w', newline='', buffering=1)
    writer = csv.writer(file)
    writer.writerow(csv_head)
    for row in data2bsave:
        writer.writerow(row)
    file.close()

