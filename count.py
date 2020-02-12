import csv
import os


def write_direct_csv(lines, filename):
    with open('output/%s' % filename, 'a', encoding="utf-8", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(lines)
    csv_file.close()


def read_csv(file):
    records = []
    with open(file, "r", encoding='utf8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            records.append(row)
    records.pop(0)
    return records


class Total:
    def __init__(self):
        self.csv_header = [['MAKE', 'MODEL', 'ID', 'YEAR', 'GALLERY', 'PDF', 'HOW_TO_VIDEOS', 'FEATURES']]

    def write_csv(self, lines, filename):
        if not os.path.isdir('output'):
            os.mkdir('output')
        if not os.path.isfile('output/%s' % filename):
            write_direct_csv(lines=self.csv_header, filename=filename)
        write_direct_csv(lines=lines, filename=filename)

    def count(self, file_path):
        lines = read_csv(file_path)
        year_array = []
        for line in lines:
            g_years = list(set(line[3].split(',')))
            p_years = list(set(line[5].split(',')))
            h_years = list(set(line[6].split(',')))
            f_years = list(set(line[7].split(',')))
            for g_year in g_years:
                if g_year not in year_array:
                    year_array.append(g_year)
            for p_year in p_years:
                if p_year not in year_array:
                    year_array.append(p_year)
            for h_year in h_years:
                if h_year not in year_array:
                    year_array.append(h_year)
            for f_year in f_years:
                if f_year not in year_array:
                    year_array.append(f_year)
        print(year_array)

        write_lines = []
        for year in range(1981, 2021):
            for line in lines:
                gallery = 0
                pdf = 0
                how_to = 0
                feature = 0
                if str(year) in line[3] or str(year) in line[5] or str(year) in line[6] or str(year) in line[7]:
                    if line[3] != 'NULL':
                        gallery = line[3].split(',').count(str(year))
                    if line[5] != 'NULL':
                        pdf = line[5].split(',').count(str(year))
                    if line[6] != 'NULL':
                        how_to = line[6].split(',').count(str(year))
                    if line[7] != 'NULL':
                        feature = line[7].split(',').count(str(year))
                    write_line = [line[0], line[1], line[2], year, gallery, pdf, how_to, feature]
                    print(write_line)
                    write_lines.append(write_line)
        write_lines.sort(key=lambda x: (x[0], x[1], x[3]))
        self.write_csv(lines=write_lines, filename='total_count.csv')
        empty_write_lines = []
        for line in lines:
            if line[3] == 'NULL' and line[5] == 'NULL' and line[6] == 'NULL' and line[7] == 'NULL':
                write_line = [line[0], line[1], line[2], '', 0, 0, 0, 0]
                empty_write_lines.append(write_line)
        empty_write_lines.sort(key=lambda x: (x[0], x[1]))
        self.write_csv(lines=empty_write_lines, filename='total_count.csv')


print("=======================Start=============================")
if __name__ == '__main__':
    total = Total()
    total.count(file_path='Here is file path')
print("=======================The End===========================")
