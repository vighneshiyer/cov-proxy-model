from pathlib import Path
import json
import argparse
from modeling.coverage_parser import parse_line

def parse_file(config_dir, config_num, seed_num, out_dir):
    cov_file = Path(config_dir) / f"{config_num}" / f"{seed_num}.cov.dat"
    conf_file = Path(config_dir) / f"{config_num}" / f"{seed_num}.json"
    conf_f = open(conf_file, "r")
    configs = json.load(conf_f)['plusarg_config']
    conf_f.close()
    f = open(cov_file, "r")
    lines = f.readlines()[1:]
    for idx, line in enumerate(lines):
        count = parse_line(line)[-1]
        path = Path(out_dir) / f"{idx}.csv"
        if not path.exists():
            path.touch()
            config_names = ','.join(configs.keys())
            path.write_text(f"{config_names},count\n")
        with open(path, "a") as out_f:
            config_values = ','.join(configs.values())
            out_f.write(f"{config_values},{count}\n")
    f.close()

def parse_coverages(config_dir, out_dir):
    # TODO: parallelize this
    out_dir = Path(out_dir)
    if not out_dir.exists():
        out_dir.mkdir()
    config_dir = Path(config_dir)
    for config_id in config_dir.iterdir():
        assert config_id.is_dir()
        for seed in config_id.glob("*.cov.dat"):
            seed_num = seed.name.replace(".cov.dat", "")
            config_num = config_id.name
            parse_file(config_dir, config_num, seed_num, out_dir)

def main():
    parser = argparse.ArgumentParser(prog="parse_coverages",
                                     description="Parse coverage files and generate csv files")
    parser.add_argument('--config-dir', help="Path to a directory of coverage files", required=True)
    parser.add_argument('--out-dir', help="Path to a directory to store the output csvs", required=True)
    args = parser.parse_args()

    parse_coverages(args.config_dir, args.out_dir)

if __name__ == "__main__":
    main()