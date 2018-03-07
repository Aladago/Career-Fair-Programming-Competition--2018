import sys  # for command line arguments
import time  # for timing
from os.path import isfile

"""
Author: Maxwell Aladago '18
Date: 05/03/2018
Python Version: 3.5.

"""
"""
The class employs two of the most popular pattern searching algorithms - 
The Knutt-Morris-Pratt algorithm and the Boyer-Moore algorithm, both published in 
1977. The KMP algorithm is used when the length of the pattern is below a certain 
arbitrary threshold. I used 10 here. This implementation of Boyer-Moore algorithms uses,
both bad item skip rule and good suffix rules for pattern re-alignments:
Any of the method works independently through
References: 
1.  Mandumula, K. K. (2011). Knuth-morris-pratt. Indiana State University. Retrieved from http://cs
.indstate.edu/̃kmandumula/kranthi.pdf

"""


class Task2(object):
    def __init__(self):
        super(Task2, self).__init__()
        self._pattern = []             # pattern of the partial data file.
        self._pattern_ln = 0           # the length of the pattern

        # The values of the following variables do not change after they are set.
        # Setting them as instance variables modifies the functions api and
        # reduces the time for passing references in function calls.
        # The good thing is, each of them are only actually constructed depending on
        # algorithm being used. eg. if Knutt-Morris-Pratt(kmp) is used, bm_god_suffix and
        # and bad_item_skips are not constructed.

        # All of them are constructed from self._pattern in linear time.

        self._kmp_suffix = []           # the skip suffix values of the pattern for kmp algorithm.
        self._bm_good_suffix = []       # The good suffix table of the pattern for boyer-more
        self._bad_item_skips = {}       # The bad item skip values of the patten for boyer-moore

    def construct_pattern(self, partial_data_file):
        """
        This method constructs a list from the partial data file.
        The list is used as a pattern for searching.
        :param partial_data_file: The partial ebola file
        :return:
            Modifies the contents of self._pattern & self._pattern_ln
        """
        with open(partial_data_file, encoding='utf-8-sig') as partial_data:
            self._pattern = [row.split()[0] for row in partial_data]

        self._pattern_ln = len(self._pattern)

    def read_complex_data(self, complex_ebola_file):
        """
        This function reads in the complex data. It performs pre-processing tasks as well
         by generating creating a dictionary out of the complex file
        :param complex_ebola_file:
        :return:
         complex_data_dic: Is a nested dictionary representation of the complex file. It has the format
            dic ={a:{i:[[date], [val]]}} where 'a' is a locality = country + locality, 'i' is one of the
            two possible indicators (cumulative_cases, cumulative_deaths)
        """
        complex_data_dic = {}

        with open(complex_ebola_file) as complex_data:
            complex_data.__next__()
            for row in complex_data:
                row = row.split(",")
                local_key = " ".join(row[0:2])
                indicator = row[2]
                value = row[4][0:-1]

                # add new keys for both locals and indicators or update values as necessary
                # Inner try deals with missing indicator key but presence of local_key.
                # Inner try block throws error in except when local_key does not exist.
                # Outer except catches the error and creates the required object.
                # this's marginally faster than using if statements because keys which exist already
                # are not hashed twice during updates.
                try:
                    try:
                        complex_data_dic[local_key][indicator][0].append(row[3])
                        complex_data_dic[local_key][indicator][1].append(value)
                    except KeyError:
                        complex_data_dic[local_key][indicator] = [[row[3]], [value]]
                except KeyError:
                    complex_data_dic[local_key] = {indicator: [[row[3]], [value]]}

        return complex_data_dic

    def mine(self, complex_data_dic, use_kmp=False):
        """
        This method digs into the data searching for a pattern the data. If found, all the
        required parameters are returned. Calls search pattern()

        :param complex_data_dic: An object of type dict, built from the complex data file.
        :param use_kmp: boolean indicating whether to use kmp or boyer-moore. default is False
        :return:
            local: The locality of the data: concatenation of country and locality separated by space
            indicator: A string indicated whether the extracted sample is for deaths or cases
            start_date: The start date of the observed data
            end_date: The end data of the observed data.
        """
        for local, row in complex_data_dic.items():
            for indicator, values in row.items():

                # sample length cannot be greater than the len of the document it was extracted from.
                # if pattern length is indeed less than vals[1], compute kmpindex & take a decision
                # if there's the possibility that the sample appeared in multiple localities
                # in complex data, only the first observed pattern is considered
                if len(values[1]) >= self._pattern_ln:
                    search_index = self.search_pattern(values[1], use_kmp)
                    if search_index > -1:
                        start_date = values[0][search_index]
                        return local, indicator, start_date

        # If sample is indeed a sample of the data, the pattern will be discovered
        # but in the unlikely event of patterns absence, return dummy text
        return "No ", "pattern", "found"

    def search_pattern(self, values, use_kmp=False):
        """
        This method defines a consistent API for the two search algorithms.
        This allows mine to called each of the methods without first checking which one is good
        :param values: The values to search from for self._pattern
        :param use_kmp: A boolean indicating which algorithm to use for the search. The default is set to
            use knutt-morris-pratt.
        :return:
        """
        if use_kmp:
            return self.kmp(values)
        else:
            return self.boyer_moore(values)

    def kmp(self, values):
        """
        The knutt-Morris-Pratt algorithm for pattern matching. The algorithm
        searches for patterns in a text by intelligently avoiding repetitions.
        First, a suffix pattern is built and that suffix then use to index the
        pattern for searching.

        :param values:  The values to search in for the pattern. The len of values
         must be at least equal to the length of pattern.
        :return:
            An integer >= 0 indicating the starting index of pattern in vals if found. Return
            -1 otherwise
        """

        ln = len(values)

        # length of text must be greater than or equal to the pattern we are searching for
        if self._pattern_ln > ln:
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
            if self._pattern[j] == values[i]:
                j += 1
                i += 1
            if j == self._pattern_ln:
                return i - j

            elif i < ln and self._pattern[j] != values[i]:
                if j != 0:
                    j = self._kmp_suffix[j - 1]
                else:
                    i = i + 1
        # pattern has not been found
        return - 1

    def boyer_moore(self, values):
        """
        A boyer-moore search technique. Works very well for large patterns due to bigger skips.
        :param values:
        :return: The starting index of the pattern in text on success. returns -1 otherwise
        """

        ln = len(values)
        index = 0

        while index <= ln - self._pattern_ln:
            unmatched_end = self._pattern_ln - 1

            while unmatched_end >= 0 and self._pattern[unmatched_end] == values[index + unmatched_end]:
                unmatched_end = unmatched_end - 1

            # we have found the pattern at index
            if unmatched_end < 0:
                return index
            else:
                mismatch = values[index + unmatched_end]
                # It's possible the mismatched item does not appear in the text at all.
                # calling the dictionary on it will raise an error but but setting
                # the 'skip' step to -1 will enable us to make a step of unmatched_index + 1
                # for all mismatches which do not appear in the pattern
                step = -1
                try:
                    step = self._bad_item_skips[mismatch]
                except KeyError:
                    pass

                # avoid backward steps in case step is bigger than unmatched_index
                step = max(1, unmatched_end - step)
                index = index + max(step, self._bm_good_suffix[unmatched_end + 1])

        # pattern is not in values
        return -1

    def suffix(self):
        """
        A method to compute the suffix list of size = len(pattern).
        The suffix is built according to the kmp algorithm description.
        :return: The suffix to be used for computing the kmp pattern skip indices
        """
        # generate a list of zeros of the same length as the pattern.
        # each item in the pattern has a skip value in case of mismatch
        self._kmp_suffix = [0] * self._pattern_ln

        # The first value of the pattern has no suffix
        j = 0
        self._kmp_suffix[0] = 0
        i = 1

        # 1. If a word at i matches another behind it, set the suffix at
        # i to the position of that word and increment both i and j.
        # 2. Otherwise,
        # a. if j is not at the beginning of the pattern, get the suffix
        # of the position immediately before j and continue matching.
        # b. otherwise, set the suffix at the current index, i to zero.
        # index 0 is a special case of b.

        while i < self._pattern_ln:
            if self._pattern[j] != self._pattern[i]:
                if j != 0:
                    j = self._kmp_suffix[j - 1]
                else:
                    self._kmp_suffix[i] = 0
                    i = i + 1
            else:
                self._kmp_suffix[i] = j + 1
                i = i + 1
                j = j + 1

    def bad_item_list(self):
        """
        A method for pre-processing the skip values for
        the bad item rule of Boyer-Moore's algorithm
        :return:
            : Method modifies the contents of self._bad_item_skips by setting them
            to the proper.
        """
        # keep values to be used for skipping in case of mismatches.
        for i in range(self._pattern_ln):
            self._bad_item_skips[self._pattern[i]] = i

    def bm_suffix_table(self):
        """
        This method constructs the look up table for god suffix shifts as specified by the
        boyer-more algorithm
        :return:
        Modifies the contents of self._bm_good_suffix
        """
        ln = self._pattern_ln
        # suffix table to determine max skips for suffices.
        # suffix table should have dimension ln + 1
        self._bm_good_suffix = [0] * (ln + 1)
        # hold borders of suffices which are prefixes too.
        borders = [0] * (ln + 1)

        s_index = ln  # indexing the suffix_skip list
        b_index = ln + 1  # indexing the border position list

        borders[s_index] = b_index  # the first item on the right has no suffix

        while s_index > 0:
            while b_index <= ln and self._pattern[s_index - 1] != self._pattern[b_index - 1]:

                # since there is a suffix, check whether there isn't a shorter suffix which has
                # already been set at this position.
                # set it to the length of this suffix ( suffix_border_index - suffix_index) if
                # has not been set
                # Update the suffix_border index to its current border value irrespective of
                # the value was previously set or not

                if self._bm_good_suffix[b_index] == 0:
                    self._bm_good_suffix[b_index] = b_index - s_index

                b_index = borders[b_index]

            # update indices.
            s_index = s_index - 1
            b_index = b_index - 1

            # border at current suffix index is the value of the border index.
            borders[s_index] = b_index

        # update the suffix skip values for items in the pattern next to each other:
        # This shows phenomenon seen where suffix_skips[i] == 0
        same_next_items_skip = borders[0]
        for i in range(ln):
            if self._bm_good_suffix[i] == 0:
                self._bm_good_suffix[i] = same_next_items_skip

            # When current index passes the skip length of same_item,
            # update the skip length of same next items
            if i == same_next_items_skip:
                same_next_items_skip = borders[i]

    def task2(self, complex_ebola_file, partial_data_file):
        """
        The is a cleaner which calls the other functions to complete task2
        :param complex_ebola_file: The path to the complex-sample data
        :param partial_data_file: The file containing the partial data
        :return:
        """

        global time_start
        self.construct_pattern(partial_data_file)
        complex_data_dic = self.read_complex_data(complex_ebola_file)

        # make a choice to use knutt-morris-pratt for search or boyer-morris
        # calling suffix() modifies the contents of self._kmp_suffix.
        # bad_item_list() modifies the contents of self_bad_item_skips
        # .bm_suffix_table() modifies the contents of self._bm_good_suffix
        if self._pattern_ln < 10:
            self.suffix()
            use_kmp = True
        else:
            self.bad_item_list()
            self.bm_suffix_table()
            use_kmp = False

        local, indicator, start_date = self.mine(complex_data_dic, use_kmp)
        filename = "task2_result-%s" % partial_data_file

        # time.time() returns seconds
        mills = 1e3
        contents = [local, indicator, start_date]
        with open(filename, 'wt') as results:
            results.write("\n".join(contents))
            # write overall runtime last
            results.write("\n" + str((time.time() - time_start) * mills) + "\n")


def check_file_exist(filename):
    """
    A utility method for checking whether a passed string is the name of a valid file
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

    # verify that files can be opened
    check_file_exist(complex_filename)
    check_file_exist(partial_filename)
    # start timer and instantiate task2 and execute functions.
    global time_start
    time_start = time.time()
    t2 = Task2()
    t2.task2(complex_filename, partial_filename)
