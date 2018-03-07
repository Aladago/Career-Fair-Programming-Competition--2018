import sys
import time     # for timing
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
        max_cumulative_index = values.index(max(values))
        return dates[max_cumulative_index]

    def rates(self, dates, vals):
        """
        This method answers the questions related to task 1 except the last two; the peaks are processed
        in a different function.
        :param dates: The dates for a given indicator. eg. cumulative deaths
        :param vals: the cumulative values for the indicator
        :return:
            date_last_stat: The date when last a significant value was recorded for this indicator
            date_peak_rate: The date for the highest rate recorded for this indicator
            rates: rate of for this indicator value. rate is computed as (cur_cum_val - prev_cum_val )/days
            where prev_cum_val is the previous observed comulative value of this start. cur_cum_val is
            cumulative value of the results we are dealing with
        """
        rates = []
        peak_rate = 0
        date_peak_rate = ""
        prev_date = self.compute_days(dates[0])

        for i in range(1, len(vals)):

            date = self.compute_days(dates[i])
            interval = date - prev_date
            cur_rate = (vals[i] - vals[i - 1]) / interval

            if cur_rate > peak_rate:
                peak_rate = cur_rate
                date_peak_rate = dates[i - 1] + "-" + dates[i]

            rates.append([dates[i], cur_rate])
            prev_date = date

        return date_peak_rate, rates

    def process_peak_rates(self, rates):
        """
        This method runs through the data to detect the values that
        show peaks. I am working with local peaks. I.e if f(x) < f(y) > f(z) for x < y < z,
        f(y) is counted as a peak. Also, flat planes are ignored
        :param rates: The rates of the statistics as for each recording entry
        :return: The dates of peak recordings.
        """
        ln = len(rates)
        peaks = []

        # special case of index 0
        if ln >= 2 and rates[0][1] > rates[1][1]:
            peaks.append(rates[0][0])
        for i  in range(1,ln-1):
            cur_rate = rates[i][1]
            if cur_rate > rates[i - 1][1] and cur_rate > rates[i + 1][1]:
                peaks.append(rates[i][0])

        # Another special case of last element
        if rates[ln - 1][1] > rates[ln - 2][1]:
            peaks.append(rates[ln - 1][0])

        return peaks

    def compute_days(self, date):
        """
        This function returns the number of days from data 00/00/00 till the current date.
        I decided to use this method because the python datetime.strftime() and datetime.strptime()
        methods are expensive. I observed that they were the major bottle necks in my implementation
        hence, the need for this function
        :param date: The string to get the number of days since the 'big bang'. should have the format
        'dd/mm/yyyy
        :return:

        """
        date_fields = [int(df) for df in date.split("/")]
        day = date_fields[0]
        month = date_fields[1]
        year = date_fields[2]

        # assume february is 28. Later add a day for each leap year in the range
        # add -1 for indexing purposes
        days_in_months = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        # compute leap years for days passed february.This is only the case when the month is
        # March (3) or above

        # A leap year is said to be divisible by both 100 and 4 or divisible by 4 but not 100.
        # number of leap years can therefore be computed by taking the
        # sum of the number of years divisible by 400(4*100) + the number of years divisible by
        # 4 - those divisible by 100.

        # all divisions are integer divisions
        if month > 2:
            num_leap_years = (year//400) + (year//4) - (year//100)
        else:
            # do not int current year in leap year computation
            y = year -1
            num_leap_years = (y// 400) + (y// 4) - (y// 100)

        num_days = (year * 365) + day + num_leap_years + sum(days_in_months[1:month])
        return num_days

    def get_ebola_free_date(self, date, days_after):
        """
        This function returns the date a given locality will be declared ebola free given
        the last occurrence of a case. This function is linear in terms of the number of days
        but still faster than the python builtin timedelta object
        The logic is simply adding num_days to date.
        :param date: The date a case was last recorded
        :param:days_after: the number of days to add to date
        :return: String, the date the country will be declared ebola free after days_after
        """
        d_fields = [int(x) for x in date.split("/")]
        day = d_fields[0]
        month = d_fields[1]
        year = d_fields[2]

        # add negative one for indexing purpoes
        days_leap = [-1, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        days_not_leap = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if self.is_leap_year(year):
            days_months = days_leap
        else:
            days_months = days_not_leap

        i = 1
        while i < days_after:
            month_days = days_months[month]
            while i < days_after and day <= month_days:
                day += 1
                i += 1

            # if our current month is december and we still have days
            # increment year. Also update months list to the year format of the
            # new year.
            if i < days_after and month == 12:
                year += 1
                month = 1
                day = 1
                if self.is_leap_year(year):
                    days_months = days_leap
                else:
                    days_months = days_not_leap
            elif i < days_after:
                month += 1
                day = 1

        return str(day) +"/" + str(month) +"/" + str(year)

    def is_leap_year(self,year):
        """
        Returns true if a given year is leap year. Otherwise, returns false.
        :param year: The year to check whether it's leap. should be of type int
        :return: boolean: True if year is leap. returns false otherwise.
        """
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

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

        # Question c
        c_time = time.time()
        ebola_free_date = self.get_ebola_free_date(date_last_infection, 43)
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
            outputfile.write("\n".join(outputs))
            timesfile.write("\n".join([str(t) for t in times]))
            # Write overall time of the program last
            timesfile.write("\n" + str((time.time() - start_time) * mills) + "\n")


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


