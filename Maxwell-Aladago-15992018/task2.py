import sys  # for command line arguments
import time  # for timing
from os.path import isfile

"""
Author: Maxwell Aladago '18
Date: 05/03/2018
Python Version: 3.5.

"""


class Task2(object):
    def __init__(self):
        super(Task2, self).__init__()

    def read_data(self, complex_ebola_file, partial_data_file):
        """
        This function reads in the complex data and the sample for task2

        :param complex_ebola_file:
        :param partial_data_file:
        :return:
         partern: A list containing the values of the sample as a 'pattern'
         complex_data_dic: Is a nested dictionary representation of the complex file. It has the format
            dic ={a:{i:[[date], [val]]}} where 'a' is a locality = country + locality, 'i' is one of the
            two possible indicators (cumulative_cases, cumulative_deaths)
        """
        pattern = []
        complex_data_dic = {}

        with open(partial_data_file, encoding='utf-8-sig') as partial_data:
            for row in partial_data:
                pattern.append(row.split()[0])

        with open(complex_ebola_file) as complex_data:
            complex_data.__next__()
            for row in complex_data:
                row = row.split(",")
                local_key = row[0] + " " + row[1]
                indicator = row[2]
                value = row[4].rstrip("\n")

                # add new keys for both locals and indicators or update as necessary
                if local_key in complex_data_dic:
                    if indicator in complex_data_dic[local_key]:
                        complex_data_dic[local_key][indicator][1].append(value)
                        complex_data_dic[local_key][indicator][0].append(row[3])
                    else:
                        complex_data_dic[local_key][indicator] = [[row[3]], [value]]
                else:
                    complex_data_dic[local_key] = {indicator: [[row[3]], [value]]}

        return pattern, complex_data_dic

    def mine(self, complex_ebola_file, partial_data_file):
        """
        This method digs into the data searching for a pattern the data. If found, all the
        required paramters are returned. Calls the read_data() module() and kmp module()

        :param complex_ebola_file: The name of the complex data file
        :param partial_data_file: The name of the sample data
        :return:
            local: The locality of the data: concatenation of country and localty separated by space
            indicator: A string indicated whether the extracted sample is for deaths or cases
            start_date: The start date of the observed data
            end_date: The end data of the observed data.
        """
        pattern, complex_data_dic = self.read_data(complex_ebola_file, partial_data_file)
        suffix = self.suffix(pattern)
        ln_pattern = len(pattern)

        for local, row in complex_data_dic.items():
            for indicator, vals in row.items():

                # sample length cannot be greater than the len of the document it was extracted from.
                # if pattern length is indeed less than vals[1], compute kmpindex & take a decision
                # if there's the possibility that the sample appeared in multiple localities
                # in complex data, only the first observed pattern is considered
                if len(vals[1]) >= ln_pattern:
                    kpmindex = self.kmp(pattern=pattern, suffixlist=suffix, vals=vals[1])
                    if kpmindex > -1:
                        start_date = vals[0][kpmindex]
                        return local, indicator, start_date

        # If sample is indeed a sample of the data, the pattern will be discovered
        # but in the unlikely event of patterns absence, return dummy text
        return "No ", "pattern", "found"

    def task2(self, complex_ebola_file, partial_data_file):
        """
        The is a cleaner which calls the other functions to complete task2
        :param complex_ebola_file: The path to the complex-sample data
        :param partial_data_file: The file containing the partial data
        :return:
        """
        # time.time() returns seconds
        millseconds_multipler = 1e3

        global time_start
        local, indicator, start_date = self.mine(complex_ebola_file, partial_data_file)

        filename = "task2_result-" + partial_data_file

        with open(filename, 'wt') as results:
            results.write(local + "\n")
            results.write(indicator + "\n")
            results.write(start_date + "\n")
            results.write(str(int((time.time() - time_start) * millseconds_multipler)) + "\n")

    def kmp(self, pattern, suffixlist, vals):
        """
        The knott-Morris-Pratt algorithm for pattern matching. The algorithm
        searches for patterns in a text by intelligently avoiding repetitions.
        First, a suffix pattern is built and that suffix then use to index the
        pattern for searching.
        :param pattern: The pattern to search for. It's a list of the partial data

        :param suffixlist: The suffix built for this pattern. Suffix is passed as a paramter because
        this method is called many times for the same pattern. This way suffix is built once and used
        :param vals:  The vals to search in for the pattern. The len of vals must be at least equal to
        the length of pattern.
        :return:  An integer value >= 0 indicating the starting index of pattern in vals if found. Return
        -1 otherwise

        """
        ln = len(vals)
        ln_pattern = len(pattern)

        # length of text must be greater than or equal to the pattern we are searching for
        if ln_pattern > ln:
            return -1

        i = 0  # index for vals
        j = 0  # index for partern. can never go beyond ln_pattern

        # 1. if there is a match between current item in pattern and current item in vals,
        #  move to next items and compare.
        # 2. Otherwise check whether we've already found the pattern in vals
        # 3. If we haven't found the pattern, a mis-match occurred
        #  a. if there's still items left in vals to search, get the suffix value of j
        # ( cannot be greater than j due to the definition of suffices)
        # start from that suffice and search again, effectively skipping the suffix at the beginning
        # b. If there are no items left to search, the pattern does not exist. return -1

        while i < ln:
            if pattern[j] == vals[i]:
                j += 1
                i += 1
            if j == ln_pattern:
                return i - j

            elif i < ln and pattern[j] != vals[i]:
                if j != 0:
                    j = suffixlist[j - 1]
                else:
                    i = i + 1
        return - 1

    def suffix(self, pattern):
        """
        A method to compute the suffix list of size = len(pattern).
        The suffix is built according to the kmp algorithm description.
        :param pattern: The pattern to build the suffix for
        :return: The suffix to be used for computing the kmp pattern skip indices
        """
        # get a copy of pattern for suffix, pattern values will be overridden
        suffix = list.copy(pattern)
        # The first value of the pattern has no suffix
        j = 0
        suffix[0] = 0
        ln = len(pattern)
        i = 1

        # 1. If a word at i matches another behind it, set the suffix at
        # i to the position of that word and increment both i and j.
        # 2. Otherwise,
        # a. if j is not at the beginning of the pattern, get the suffix
        # of the position immediately before j and continue matching.
        # b. otherwise, set the suffix at the current index, i to zero.
        # index 0 is a special case of b.

        while i < ln:
            if pattern[j] != pattern[i]:
                if j != 0:
                    j = suffix[j - 1]
                else:
                    suffix[i] = 0
                    i = i + 1
            else:
                suffix[i] = j + 1
                i = i + 1
                j = j + 1

        return suffix


def checkFileExist(filename):
    """
    A untility method for checking whether a passed string is the name of a valid file
    :param filename: The name of the file
    """
    if not isfile(filename):
        exit("Error: " + filename + " is not a name of a valid file")


if __name__ == '__main__':
    # program name is at argv[0].
    try:
        complex_filename = sys.argv[1]
        partial_filename = sys.argv[2]
    except IndexError:
        print("Error: The program requires a two strings as arguments")
        sys.exit()

    # very that files can be opened
    checkFileExist(complex_filename)
    checkFileExist(partial_filename)

    # start timer and instantiate task2 and execute functions.
    global time_start
    time_start = time.time()
    t2 = Task2()
    t2.task2(complex_filename, partial_filename)
