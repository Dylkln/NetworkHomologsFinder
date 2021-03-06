import glob
import gzip
import os
import shutil
import time
import argparse


def arguments():
    """
    set arguments
    """

    parser = argparse.ArgumentParser()

    # Mandatory arguments
    parser.add_argument("-n", "--network_file", dest="network",
                        type=str, required=True,
                        help="The path to the network file")
    parser.add_argument("-i", "--id_list", dest="id_list",
                        type=str, required=True,
                        help="The path to the id list file")
    parser.add_argument("-wd", "--working_directory", dest="wd",
                        type=str, required=False, default=None,
                        help="The path to the working directory")

    return parser.parse_args()


def read_file(file):
    """
    Reads a file

    :param file:
        A file (gzipped or not)
    :return:
        a line of the file
    """
    if file.endswith(".gz"):
        with gzip.open(file, "rt") as f:
            for line in f:
                yield line.strip()
    else:
        with open(file, "r") as f:
            for line in f:
                yield line.strip()


def load_id(input_list):
    """
    Loads id in memory
    :param input_list:
        A list of ID in a file
    :return:
        A set of ID
    """
    return {line for line in read_file(input_list)}


def grep(input_list, network, index, run):
    """
    Search for the IDs contained in the input list in the network

    :param input_list:
        A list of ID in a file
    :param network:
        A sequence similarity network
    :param index:
        The run index
    :param run:
        The run file
    """

    print(f"doing grep {index}")
    l = {line.strip() for line in read_file(input_list)}

    with gzip.open(run, "wt") as o:
        for line in read_file(network):
            sl = line.split("\t")[:5]
            if sl[0] in l and sl[0] != sl[4]:
                print(line, file=o)

    print("grep done\n")


def create_homologs(run, homologs, index):
    """
    Creates homologs file based on the run

    :param run:
        The run file
    :param homologs:
        The homologs file
    :param index:
        The run index
    """
    print("retrieving homologs")
    with gzip.open(homologs, "wt") as o:
        for line in read_file(run):
            li = "\t".join(line.split()[:6:4])
            print(li, file=o)

    print(f"homologs {index} done\n")


def create_inputlist(wd, index, homologs, banlist):
    """
    Creates the list of ID for the next run

    :param wd:
        The working directory
    :param index:
        The run index
    :param homologs:
        The homologs file
    :param banlist:
        The ban list of ID
    """
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
    """
    Copy the file used as input list into the working directory
    :param file:
        The ID list file
    :param wd:
        The working directory
    :return:
        The path to the file
    """
    fname = f"{wd}/base_id/base_id_0"
    shutil.copyfile(file, fname)
    return fname


def create_file_names(wd, rd, thd, ids, index, net):
    """
    Creates file names

    :param wd:
        The working directory
    :param rd:
        The run directory
    :param thd:
        The homologs directory
    :param ids:
        The path to ID list
    :param index:
        The run index
    :param net:
        The network file
    :return:
        Variable names
    """
    network = net
    run = f"{rd}/run_{index}.gz"
    homologs = f"{thd}/homologs_{index}.gz"
    input_list = get_file(ids, wd) if index == 1 else f"{wd}/base_id/base_id_{index - 1}.gz"

    return network, input_list, run, homologs


def not_empty(run):
    """
    Checks if the run is empty

    :param run:
        The run file
    :return:
        True or False
    """
    for line in read_file(run):
        return line != ""


def check_run(rd):
    """
    Checks the run number

    :param rd:
        The run directory
    :return:
        an index
    """
    files = glob.glob(f"{rd}/*")
    indices = [int(i.split("_")[-1].split(".")[0]) for i in files]
    if indices:
        return max(indices)
    return 0


def fill_ban_list_file(file, input_list):
    """
    Fills the ban list

    :param file:
        The ban list file
    :param input_list:
        The ID list file
    """
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
    """
    Main program function
    """
    args = arguments()

    print("You launched NHF with these parameters :")
    print(f"Network : {args.network}")
    print(f"ID list file : {args.id_list}")
    print(f"Working directory : {args.wd}")
    st = time.time()

    print("starting program")

    if not os.path.exists(args.wd):
        subfolder = ["runs", "temporary_homologs", "base_id"]
        for e in subfolder:
            os.makedirs(args.wd + "/" + e)
        print("directories created")
    else:
        print("directories already exist")

    rd = args.wd + "/runs"
    thd = args.wd + "/temporary_homologs"

    index = check_run(rd)

    banlist = f"{args.wd}/ban_list"

    s = time.time()
    if index == 0:
        index += 1
        network, input_list, run, homologs = create_file_names(args.wd, rd, thd, args.id_list,
                                                               index, args.network)
        print("doing first run")
    else:
        index += 1
        network, input_list, run, homologs = create_file_names(args.wd, rd, thd, args.id_list,
                                                               index, args.network)
        print(f"resuming on run {index}")

    grep(input_list, network, index, run)
    fill_ban_list_file(banlist, input_list)
    create_homologs(run, homologs, index)
    create_inputlist(args.wd, index, homologs, banlist)
    print(f"run {index} complete\n")
    e = time.time()
    print(f"Operations done in {round(e - s, 2)} seconds")

    while not_empty(run):
        s = time.time()
        index += 1
        network, input_list, run, homologs = create_file_names(args.wd, rd, thd, args.id_list,
                                                               index, args.network)

        print(f"doing run {index}")
        grep(input_list, network, index, run)

        fill_ban_list_file(banlist, input_list)

        create_homologs(run, homologs, index)
        create_inputlist(args.wd, index, homologs, banlist)
        print(f"run {index} complete\n")
        e = time.time()
        print(f"Operations done in {round(e - s, 2)} seconds")

    end = time.time()
    print(f"run {index} is empty, the program finished his job")
    print(f"Program run time : {round(end - st, 2)} seconds")


if __name__ == '__main__':
    main()
