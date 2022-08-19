import csv
import sys

from tqdm import tqdm


def main():
    rows = []
    i = 0
    n = int(sys.argv[1])
    prefix = sys.argv[2]
    for c, row in tqdm(enumerate(csv.reader(sys.stdin, delimiter=";", quotechar='"'))):
        if c == 0 and row[0] == "X":
            header = row
            continue
        rows.append(row)
        if len(rows) == n:
            with open(f"{prefix}_{i}.csv", "w") as f:
                writer = csv.writer(f, delimiter=";", quotechar='"')
                writer.writerow(header)
                for row in rows:
                    writer.writerow(row)
            rows = []
            i += 1


if __name__ == "__main__":
    main()
