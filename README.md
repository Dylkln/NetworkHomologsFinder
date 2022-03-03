# NetworkHomologsFinder

NHF is a program that finds homologs in a sequence similarity network.
It takes a sequence similarity network and an ID list in input, and returns "run" files and homologs in output.

## Download the program

1. Clone git repository

> HTTPS link

```
git clone https://github.com/Dylkln/NetworkHomologsFinder.git
```

> SSH link

```
git clone git@github.com:Dylkln/NetworkHomologsFinder.git
```

## How to use the program

```
python program/NHF.py -n <NETWORK FILE> -i <ID LIST FILE> -wd <WORKING DIRECTORY>
```

To run the test, use:

```
python program/NHF.py -n test_NHF/network_NHF_test.gz -i test_NHF/list_NHF_test -wd working_dir_NHF
```