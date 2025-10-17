import random


def sample_data() -> None:
    input_path = "data/raw/raw2024.txt"
    output_path = "data/raw/sample2024.txt"

    sample_size = 10000  # choose how many lines you want
    total_lines = 3458645  # if you know it; otherwise count it once

    # compute the probability of keeping a line
    keep_prob = sample_size / total_lines

    with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            if random.random() < keep_prob:
                outfile.write(line)
    return line
