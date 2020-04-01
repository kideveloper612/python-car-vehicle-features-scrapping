import os
import csv
import requests

csv_header = [['YEAR', 'MAKE', 'MODEL', 'SECTION', 'TITLE', 'DESCRIPTION', 'IMAGE']]


def write_direct_csv(lines, filename):
    with open('confirm/%s' % filename, 'a', encoding="utf-8", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(lines)
    csv_file.close()


def write_csv(lines, filename):
    if not os.path.isdir('confirm'):
        os.mkdir('confirm')
    if not os.path.isfile('confirm/%s' % filename):
        write_direct_csv(lines=csv_header, filename=filename)
    write_direct_csv(lines=lines, filename=filename)


def sendRequest(url):
    try:
        page = requests.get(url)
    except Exception as e:
        print("error:", e)
        return False
    # check status code
    if page.status_code != 200:
        return False
    return True


def confirm(f_):
    for origin, directories, files in os.walk(f_):
        for file in files:
            if '.csv' not in file:
                continue
            file_path = f_ + '/' + file
            try:
                with open(file_path, "r") as csv_file:
                    csv_reader = list(csv.reader(csv_file))
                    for line in csv_reader:
                        image_url = line[-1]
                        if 'http' not in image_url:
                            continue
                        res = sendRequest(image_url)
                        if not res:
                            continue
                        new_line = []
                        for ln in line:
                            new_line.append(ln.encode('utf-8').decode('utf-8'))
                        print(new_line)
                        write_csv(lines=[new_line], filename=file)
            except Exception as e:
                print(e)
                with open(file_path, 'r', encoding="utf-8",  errors='ignore') as csv_file:
                    csv_reader = list(csv.reader(csv_file))
                    for line in csv_reader:
                        image_url = line[-1]
                        if 'http' not in image_url:
                            continue
                        res = sendRequest(image_url)
                        if not res:
                            continue
                        new_line = []
                        for ln in line:
                            new_line.append(ln.encode('utf-8').decode('utf-8'))
                        print(new_line)
                        write_csv(lines=[new_line], filename=file)


if __name__ == "__main__":
    print('---------- START -------------')
    path = './image_Confirm'
    confirm(f_=path)
    print('----------- End --------------')