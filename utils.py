import csv
import cv2

def csvLogger(csv_head, data2bsave, save_path):
    """ save data2bsave to save_path with csv_head as header 
    csv_head: dict keys or just csv head
    data2bsave: list of data, [row]
    savepath: path to save
    """
    file = open(save_path, 'w', newline='', buffering=1)
    writer = csv.writer(file)
    writer.writerow(csv_head)
    for row in data2bsave:
        writer.writerow(row)
    file.close()


def calculate_blurriness(frame):
    """ calculate blurriness of a frame
    frame: a frame, get from VideoFileClip.get_frame(t)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var