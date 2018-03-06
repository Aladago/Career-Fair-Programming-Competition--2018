import sys
import time
from datetime import datetime, timedelta
from os.path import isfile

"""
Author: Maxwell Aladago '18
Date: 05/03/2018
Python Version: 3.5.

"""


class Task1(object):
    def __init__(self):
        super(Task1, self).__init__()

    def read_data(self, filename):
        """
        A method for open and pre-processing the data. Pre-processing step is very small
        - the data is merely separated according to indicator values. i.e the values for death are separated
        from those indicating cases

        :param filename:  The name of the file containing the data
        :return:
            death_stats: The rows of the data belonging to indicator 'cumulative_deaths'
            infection_stats: The rows of the data belonging to indicator 'cumulative_cases'
        """
        with open(filename) as eboladata:
            eboladata.__next__()  # skip header. NOTE: Please change to eboladata.next()
            # python version <= 2.7
            death_dates = []
            death_vals = []
            infections_dates = []
            infections_vals = []
            for row in eboladata:
                row = row.split(",")
                if row[2].endswith("_deaths"):
                    death_dates.append(row[3])
                    death_vals.append(int(row[4]))
                elif row[2].endswith("_cases"):
                    infections_dates.append(row[3])
                    infections_vals.append(int(row[4]))
        return death_dates, death_vals, infections_dates, infections_vals

    def last_occurrence_date(self, dates, values):
        """
        TThis method finds the occurrence of a given indicator.
        Since the values are cumulative, the last occurrence of the indicator is
        the first occurrence of the maximum value in the list
        :param dates: The recording of the date for that particular indicator
        :param values: The respective cumulative values
        :return:
        The date of the last occurrence for the given indicator
        """
        max_cummulative_index = values.index(max(values))
        return dates[max_cummulative_index]

    def rates(self, dates, vals):
        """
        This method answers the questions related to task 1 except the last two; the peaks are processed
        in a different function.
        :param stats: The statistics for a given indicator. eg. cumulative deaths
        :return:
            date_last_stat: The date when last a significant value was recorded for this indicator
            date_peak_rate: The date for the highest rate recorded for this indicator
            rates: rate of for this indicator value. rate is computed as (cur_cum_val - prev_cum_val )/days
            where prev_cum_val is the previous observed comulative value of this start. cur_cum_val is
            commulative value of the results we are dealing with
        """
        rates = []
        peak_rate = 0
        date_peak_rate = ""
        for i in range(1, len(vals)):

            date = datetime.strptime(dates[i], "%d/%m/%Y")
            prev_date = datetime.strptime(dates[i - 1], "%d/%m/%Y")

            # time subtractions returns a timedelta object. days can be called directly on it
            recor_interval_days = (date - prev_date).days
            cur_rate = (vals[i] - vals[i - 1]) / recor_interval_days

            if cur_rate > peak_rate:
                peak_rate = cur_rate
                date_peak_rate = prev_date.strftime("%d/%m/%Y") + "-" + dates[i]

            rates.append([dates[i], cur_rate])

        return date_peak_rate, rates

    def process_peak_rates(self, rates):
        """
        This method runs through the data to detect the values that
        show peaks. I am working with local peaks. I.e if f(x) < f(y) > f(z) for x < y < z,
        f(y) is counted as a peak. Also, plateuxs are ignored
        :param rates: The rates of the statistics as for each recording entry
        :return: The dates of peak recordings.
        """
        ln = len(rates)
        peaks = []

        # special case of index 0
        if ln >= 2 and rates[0][1] > rates[0][1]:
            peaks.append(rates[0][0])

        for i in range(ln - 1):
            cur_rate = rates[i][1]
            if cur_rate > rates[i - 1][1] and cur_rate > rates[i + 1][1]:
                peaks.append(rates[i][0])
        # Another special case of last element
        if rates[ln - 1][1] > rates[ln - 2][1]:
            peaks.append(rates[ln - 1][0])

        return peaks


    def task1(self, filename):
        """
        This module calls others defined in this module to complete the task.
        It also writes the required answers to the same directory directory of this file
        :param filename: The name of the file containing the ebola data. Should have at least 5 columns
        :return:
        """
        # time.time() returns seconds
        pre_process_time = time.time()
        death_dates, death_vals, infection_dates, infection_vals = self.read_data(filename)
        pre_process_time = time.time() - pre_process_time

        # Question a
        a_time = time.time()
        date_last_infection = self.last_occurrence_date(infection_dates, infection_vals)
        a_time = time.time() - a_time

        # Questions b.
        b_time = time.time()
        date_last_death = self.last_occurrence_date(death_dates, death_vals)
        b_time = time.time() - b_time

        # question c
        c_time = time.time()
        ebola_free_date = datetime.strptime(date_last_infection, "%d/%m/%Y") + timedelta(days=42)
        ebola_free_date = datetime.strftime(ebola_free_date, "%d/%m/%Y")
        c_time = time.time() - c_time

        # Question d
        d_time = time.time()
        date_peak_irate, infection_rates = self.rates(infection_dates, infection_vals)
        d_time = time.time() - d_time

        # Question e
        e_time = time.time()
        date_peak_drate, death_rates = self.rates(death_dates, death_vals)
        e_time = time.time() - e_time

        # Question f
        f_time = time.time()
        peak_infection_rates_date = self.process_peak_rates(infection_rates)
        numpeak_infections = len(peak_infection_rates_date)
        f_time = time.time() - f_time

        # question g
        peak_death_rates_date = self.process_peak_rates(death_rates)
        numpeak_deaths = len(peak_death_rates_date)

        # organize output into list to shorten the code. They can then be index
        outputs = [
            date_last_infection, date_last_death, ebola_free_date, date_peak_irate,
            date_peak_drate, str(numpeak_infections) + "\t" + ", ".join(peak_infection_rates_date),
                             str(numpeak_deaths) + "\t" + ", ".join(peak_death_rates_date)
        ]

        times = [pre_process_time, a_time, b_time, c_time, d_time, e_time, f_time]

        # Write answers to files
        filename = "task1_answers-" + filename
        timingsfile = "task1_times-" + filename

        mills = 1e3
        with open(filename, 'wt') as outputfile, open(timingsfile, 'wt') as timesfile:
            for i in range(len(outputs)):
                outputfile.write(outputs[i] + "\n")
                timesfile.write(str((times[i]) * mills) + "\n")

            # special of overall time of the program
            timesfile.write(str((time.time() - start_time) * mills) + "\n")


if __name__ == '__main__':
    # program name is at argv[0].
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Error: The program requires a two strings as arguments")
        sys.exit()

    if not isfile(filename):
        sys.exit("Error: " + filename + " is not a name of a valid file")

    # start timer instantiate class and run programs
    global start_time
    start_time = time.time()
    t1 = Task1()
    t1.task1(filename)
