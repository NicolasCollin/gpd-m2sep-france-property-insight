import random


def sample_data() -> None:
    input_path = "data/raw/raw2024.txt"
    output_path = "data/raw/sample2024.txt"

    sample_size = 10000  # number of lines you want
    total_lines = 3458645  # total lines including header

    keep_prob = sample_size / total_lines

    with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
        # Always write the header
        header = infile.readline()
        outfile.write(header)

        # Sample the remaining lines
        for line in infile:
            if random.random() < keep_prob:
                outfile.write(line)


if __name__ == "__main__":
    sample_data()
