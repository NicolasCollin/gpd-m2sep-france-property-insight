"""
script we used to produce sample2024.txt
will likely not be used again as we will move on SQLAlchemy and .db files
"""

import random
from pathlib import Path
from typing import List, Union


def random_sample(
    input_path: Union[Path, str],
    output_path: Union[Path, str],
    sample_size: int,
) -> None:
    """
    Sample a large text file by selecting a random subset of lines.

    Args:
        - input_path: Path to the input text file.
        - output_path: Path where the sampled file will be saved.
        - sample_size: Number of lines to sample (excluding the header).

    Raises:
        ValueError: If the input file contains fewer lines than `sample_size`.
    
    Returns:
        - None
    
    Output:
        - Save sample.txt file to output_path.
    """

    # Ensure Path objects
    input_path_obj: Path = Path(input_path)
    output_path_obj: Path = Path(output_path)

    # Create parent directories for output if they don't exist
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    reservoir: List[str] = []
    line_count: int = 0

    # Read input file
    with input_path_obj.open("r", encoding="utf-8") as infile:
        # Read header
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
    with output_path_obj.open("w", encoding="utf-8") as outfile:
        outfile.write(header)
        outfile.writelines(reservoir)

    print(f"Sampled {len(reservoir)} lines to {output_path_obj.resolve()}")


if __name__ == "__main__":
    random_sample(
        input_path="data/raw/raw2024.txt",
        output_path="data/raw/sample2024.txt",
        sample_size=1000,
    )
