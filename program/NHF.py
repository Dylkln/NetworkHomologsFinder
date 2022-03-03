import glob
import gzip
import os
import shutil
import time


def read_file(file):
    if file.endswith(".gz"):
        with gzip.open(file, "rt") as f:
            for line in f:
                yield line.strip()
    else:
        with open(file, "r") as f:
            for line in f:
                yield line.strip()


def load_id(input_list):
    return {line for line in read_file(input_list)}


def grep(input_list, network, index, run):
    print(f"doing grep {index}")

    l = {line.strip() for line in read_file(input_list)}
    with gzip.open(run, "wt") as o:
        for line in read_file(network):
            sl = line.split("\t")[:5]
            if sl[0] in l and sl[0] != sl[4]:
                print(line, file=o)

    print("grep done\n")


def create_homologs(run, homologs, index):
    print("retrieving homologs")
    with gzip.open(homologs, "wt") as o:
        for line in read_file(run):
            li = "\t".join(line.split()[:6:4])
            print(li, file=o)

    print(f"homologs {index} done\n")


def create_inputlist(wd, index, homologs, banlist):
    print("retrieving input_list")
    input_list = f"{wd}/base_id/base_id_{index}.gz"
    id_ban = load_id(banlist)

    with gzip.open(input_list, "wt") as il:
        for line in read_file(homologs):
            li = line.split("\t")[1]
            if li not in id_ban:
                print(li, file=il)

    print(f"input list for run {index + 1} done")


def get_file(file, wd):
    fname = f"{wd}/base_id/base_id_0"
    shutil.copyfile(file, fname)
    return fname


def create_file_names(wd, rd, thd, ids, index):
    network = "/shared/projects/bluecloud/input/NetworkEricP/pcov80_pident80/ultimate_80_80.gz"
    run = f"{rd}/run_{index}.gz"
    homologs = f"{thd}/homologs_{index}.gz"
    input_list = get_file(ids, wd) if index == 1 else f"{wd}/base_id/base_id_{index - 1}.gz"

    return network, input_list, run, homologs


def not_empty(run):
    for line in read_file(run):
        return line != ""


def check_run(rd):
    files = glob.glob(f"{rd}/*")
    indices = [int(i.split("_")[-1].split(".")[0]) for i in files]
    if indices:
        return max(indices)
    return 0


def fill_ban_list_file(file, input_list):
    b_id = load_id(input_list)

    if not os.path.exists(file):
        with open(file, "w") as f:
            for i in b_id:
                print(i, file=f)

    else:
        ban = load_id(file)
        with open(file, "a") as f:
            for i in b_id:
                if i not in ban:
                    f.write(f"{i}\n")


def main():
    st = time.time()
    print("starting program")
    wd = "working_dir_grep"
    if not os.path.exists(wd):
        subfolder = ["runs", "temporary_homologs", "base_id"]
        for e in subfolder:
            os.makedirs(wd + "/" + e)
        print("directories created")
    else:
        print("directories already exist")

    rd = wd + "/runs"
    thd = wd + "/temporary_homologs"
    path_id = "/shared/projects/bluecloud/input/MATOU-v1/SMAGs"
    ids = path_id + "/CC_CarbonFix_GenesfromSMAGS"

    index = check_run(rd)

    banlist = f"{wd}/ban_list"
    s = time.time()
    if index == 0:
        index += 1
        network, input_list, run, homologs = create_file_names(wd, rd, thd, ids, index)
        print("doing first run")
    else:
        index += 1
        network, input_list, run, homologs = create_file_names(wd, rd, thd, ids, index)
        print(f"resuming on run {index}")

    grep(input_list, network, index, run)
    fill_ban_list_file(banlist, input_list)
    create_homologs(run, homologs, index)
    create_inputlist(wd, index, homologs, banlist)
    print(f"run {index} complete\n")
    e = time.time()
    print(f"Operations done in {round(e - s, 2)} seconds")

    while not_empty(run):
        s = time.time()
        index += 1
        network, input_list, run, homologs = create_file_names(wd, rd, thd, ids, index)

        print(f"doing run {index}")
        grep(input_list, network, index, run)

        fill_ban_list_file(banlist, input_list)

        create_homologs(run, homologs, index)
        create_inputlist(wd, index, homologs, banlist)
        print(f"run {index} complete\n")
        e = time.time()
        print(f"Operations done in {round(e - s, 2)} seconds")

    end = time.time()
    print(f"run {index} is empty, the program finished his job")
    print(f"Program run time : {round(end - st, 2)} seconds")


if __name__ == '__main__':
    main()
