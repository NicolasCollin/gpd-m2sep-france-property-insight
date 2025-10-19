import random
from pathlib import Path


def sample_data() -> None:
    """
    Sample a large text file by selecting random lines.

    This temporary utility reduces file size for faster development while a
    full data storage solution is being prepared.

    - Always preserves the header line.
    - Writes the sampled lines to a new file called "sample20XX.txt" in data/raw/ folder.

    Meant to run only once per raw data file.
    """
    input_path: Path = Path("data/raw/raw2024.txt")
    output_path: Path = Path("data/raw/sample2024.txt")

    sample_size: int = 10_000  # desired number of lines (excluding header)
    total_lines: int = 3_458_645  # total number of lines including header

    keep_prob: float = sample_size / total_lines

    with input_path.open("r", encoding="utf-8") as infile, output_path.open("w", encoding="utf-8") as outfile:
        # Always write the header
        header = infile.readline()
        outfile.write(header)

        # Sample the remaining lines
        for line in infile:
            if random.random() < keep_prob:
                outfile.write(line)


if __name__ == "__main__":
    sample_data()
