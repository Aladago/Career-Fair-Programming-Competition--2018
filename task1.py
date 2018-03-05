from datetime import datetime, timedelta
import sys
import time

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
            death_stats: The rows of the data belonging to indicator 'cummulative_deaths'
            infection_stats: The rows of the data belonging to indicator 'cummulative_cases'
        """
        with open(filename) as eboladata:
            death_stats = []
            infection_stats = []
            eboladata.__next__()    # skip header. NOTE: Please change to eboladata.next()
                                    # python version <= 2.7
            for row in eboladata:
                row = row.split(",")
                if row[2].endswith("_deaths"):
                    death_stats.append([row[3], row[4]])
                elif row[2].endswith("_cases"):
                    infection_stats.append([row[3], row[4]])

        return death_stats, infection_stats

    def task1(self, filename):
        """
        This module calls others defined in this module to complete the task.
        It also writes the required answers to the same directory directory of this file
        :param filename: The name of the file containing the ebola data. Should have at least 5 columns
        :return:
        """
        # time.time() returns seconds
        millseconds_multipler = 1e3

        pre_process_time = time.time()
        death_stats, infection_stats = self.read_data(filename)
        pre_process_time = time.time() - pre_process_time

        # Questions b, e. Each question will be assigned the average
        b_e_time = time.time()
        date_last_death, date_peak_drate, death_rates = self.extract_answers(death_stats)
        b_e_time = time.time() - b_e_time
        b_time = e_time = b_e_time/2

        # Questions a, d. Will find the average and use as timing for each question
        a_d_time = time.time()
        date_last_infection, date_peak_irate, infection_rates = self.extract_answers(infection_stats)
        a_d_time = time.time() - a_d_time
        a_time = d_time = a_d_time/2

        # question c
        c_time = time.time()
        ebola_free_date = datetime.strptime(date_last_death, "%d/%m/%Y") + timedelta(days=42)
        ebola_free_date = datetime.strftime(ebola_free_date, "%d/%m/%Y")
        c_time = time.time() -c_time

        # question f
        f_time = time.time()
        peak_infection_rates_date = self.process_peak_rates(infection_rates)
        numpeak_infections = len(peak_infection_rates_date)
        f_time = time.time() - f_time

        # question g
        g_time = time.time()
        peak_death_rates_date = self.process_peak_rates(death_rates)
        numpeak_deaths = len(peak_death_rates_date)
        g_time = time.time() - g_time

        # organize output into list to shorten the code. They can then be index
        outputs = [
            date_last_infection, date_last_death, ebola_free_date, date_peak_irate,
            date_peak_drate, str(numpeak_infections) + " " + str(peak_infection_rates_date),
                             str(numpeak_deaths) + " " + str(peak_death_rates_date)
        ]

        times = [pre_process_time, a_time, b_time, c_time, d_time, e_time, f_time]

        # Write answers to files
        filename = "task1_answers-"+ filename
        timingsfile = "task1_times-"+ filename

        with open(filename, 'wt') as outputfile, open(timingsfile,'wt') as timesfile:
            for i in range(len(outputs)):
                outputfile.write(outputs[i] + "\n")
                timesfile.write(str(int((times[i]) * millseconds_multipler)) + "\n")

            # special of overall time of the program
            timesfile.write(str(int((time.time() - start_time)*millseconds_multipler)) + "\n")

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

        for i in range(ln -1):
            cur_rate = rates[i][1]
            if cur_rate > rates[i -1][1] and cur_rate > rates[i + 1][1]:
                peaks.append(rates[i][0])
        # Another special case of last element
        if rates[ln - 1][1] > rates[ln - 2][1]:
            peaks.append(rates[ln-1][0])

        return peaks

    def extract_answers(self, stats):
        """
        This method answers the questions related to task 1 except the last two; the peaks are processed
        in a different function.
        :param stats: The statistics for a given indicator. eg. cummulative deaths
        :return:
            date_last_stat: The date when last a significant value was recorded for this indicator
            date_peak_rate: The date for the highest rate recorded for this indicator
            rates: rate of for this indicator value. rate is computed as (cur_cum_val - prev_cum_val )/days
            where prev_cum_val is the previous observed commulative value of this start. cur_cum_val is
            commulative value of the results we are dealing with
        """
        rates = []
        val_last_stat = int(stats[0][1])
        date_last_stat = stats[0][0]

        peak_rate = 0
        date_peak_rate = ""

        prev_record_date = datetime.strptime(date_last_stat, "%d/%m/%Y")
        prev_record_value = val_last_stat

        for record in range(1, len(stats)):
            date_curstat = stats[record][0]
            val_curstat = int(stats[record][1])

            if val_curstat > val_last_stat:
                val_last_stat = val_curstat
                date_last_stat = date_curstat

            d_stat = datetime.strptime(date_curstat, "%d/%m/%Y")
            recor_interval_days = (d_stat - prev_record_date).days
            cur_rate = (val_curstat - prev_record_value) / recor_interval_days

            if cur_rate > peak_rate:
                peak_rate = cur_rate
                date_peak_rate = prev_record_date.strftime("%d/%m/%Y") + "-" + date_curstat

            rates.append([date_curstat, cur_rate])

            prev_record_date = d_stat
            prev_record_value = val_curstat

        return date_last_stat, date_peak_rate, rates


if __name__ == '__main__':
       # program name is at argv[0].
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Error: The program requires a two strings as arguments")
        sys.exit()

    # start timer instantiate class and run programs
    global start_time
    start_time = time.time()
    t1 = Task1()
    t1.task1(filename)
