import random
from pathlib import Path


def random_sample(
    input_path: Path | str,
    output_path: Path | str,
    sample_size: int,
) -> None:
    """
    Sample a large text file by selecting a random subset of lines.

    Args:
        input_path (Path | str): Path to the input text file.
        output_path (Path | str): Path where the sampled file will be saved.
        sample_size (int): Number of lines to sample (excluding the header).

    Raises:
        ValueError: If the input file contains fewer lines than `sample_size`.
    """
    input_path: Path = Path(input_path)
    output_path: Path = Path(output_path)

    reservoir: list[str] = []
    line_count: int = 0

    with input_path.open("r", encoding="utf-8") as infile:
        # Always read header
        header: str = infile.readline()

        # Reservoir sampling
        for line in infile:
            line_count += 1
            if line_count <= sample_size:
                reservoir.append(line)
            else:
                j: int = random.randint(1, line_count)
                if j <= sample_size:
                    reservoir[j - 1] = line

    if line_count < sample_size:
        raise ValueError(f"Cannot sample {sample_size} lines: input file has only {line_count} data lines.")

    # Write sampled lines with header
    with output_path.open("w", encoding="utf-8") as outfile:
        outfile.write(header)
        outfile.writelines(reservoir)

    print(f"Sampled {len(reservoir)} lines to {output_path.resolve()}")
