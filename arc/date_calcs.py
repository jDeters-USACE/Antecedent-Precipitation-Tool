# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

######################################
##  ------------------------------- ##
##          date_calcs.py           ##
##  ------------------------------- ##
##      Copyright: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################

"""Calculates and stores all dates for the Antecedent Precipitation Tool"""

import datetime

def rectify_inputs(year, month, day):
    "Test inputs and produce Datetime"
    if len(str(day)) == 1:
        day = '0' + str(day)
    else:
        day = str(day)
    if len(str(month)) == 1:
        month = '0' + str(month)
    else:
        month = str(month)
    observation_date = '{}-{}-{}'.format(year, month, day)

    yesterday_datetime = datetime.datetime.today()- datetime.timedelta(days=2)
    observation_datetime = datetime.datetime.strptime(observation_date, '%Y-%m-%d')
    if observation_datetime > yesterday_datetime:
        observation_datetime = yesterday_datetime
    return observation_datetime 

class Main(object):
    """Calculates and stores all dates for the Antecedent Precipitation Tool"""
    
    def __init__(self, year, month, day):
        self.observation_datetime = rectify_inputs(year, month, day)
        self.calculate()
    
    def calculate(self):
        """Calculates all dates for the Antecedent Precipitation Tool"""
        self.observation_date = self.observation_datetime.strftime('%Y-%m-%d')
        self.observation_day = self.observation_datetime.strftime('%d')
        self.observation_month = self.observation_datetime.strftime('%m')
        self.observation_year = int(self.observation_datetime.strftime('%Y'))
        # Calculate Start and End dates for the water year in question
        if int(self.observation_month) > 9:
            self.current_water_year_start_date = str(self.observation_year) + '-10-01'
            self.current_water_year_end_date = str(self.observation_year + 1) + '-09-30'
            self.prior_water_year_start_date = str(self.observation_year - 1) + '-10-01'
            self.prior_water_year_end_date = str(self.observation_year) + '-09-30'
            self.following_water_year_start_date = str(self.observation_year + 1) + '-10-01'
            self.following_water_year_end_date = str(self.observation_year + 2) + '-09-30'
            self.normal_period_start_date = str(self.observation_year - 31)+'-10-01'
            self.normal_period_data_start_date = str(self.observation_year - 31)+'-09-01'
            self.normal_period_end_date = str(self.observation_year) + '-09-30'
        else:
            self.current_water_year_start_date = str(self.observation_year - 1)+'-10-01'
            self.current_water_year_end_date = str(self.observation_year)+'-09-30'
            self.prior_water_year_start_date = str(self.observation_year - 2)+'-10-01'
            self.prior_water_year_end_date = str(self.observation_year - 1)+'-09-30'
            self.following_water_year_start_date = str(self.observation_year)+'-10-01'
            self.following_water_year_end_date = str(self.observation_year + 1)+'-09-30'
            self.normal_period_start_date = str(self.observation_year-32)+'-10-01'
            self.normal_period_data_start_date = str(self.observation_year-32)+'-09-01'
            self.normal_period_end_date = str(self.observation_year-1) + '-09-30'
        # Calculate antecedent period start (90 days prior to obs_date)
        antecedent_period_start_datetime = self.observation_datetime - datetime.timedelta(days=89)
        self.antecedent_period_start_date = antecedent_period_start_datetime.strftime('%Y-%m-%d')
        # Calculate graph start date (~7 months prior to obs_date)
        start_month_datetime = self.observation_datetime - datetime.timedelta(days=203)
        graph_start_month = start_month_datetime.strftime('%m')
        graph_start_year = start_month_datetime.strftime('%Y')
        self.graph_start_date = '{}-{}-01'.format(graph_start_year, graph_start_month)
        # Calculate graph end date (end of the previous month next year)
        graph_start_datetime = datetime.datetime.strptime(self.graph_start_date, '%Y-%m-%d')
        day_before_datetime = graph_start_datetime - datetime.timedelta(days=1)
        graph_end_year = int(day_before_datetime.strftime('%Y')) + 1
        graph_end_month = day_before_datetime.strftime('%m')
        # Test for last date of month to be Leap-year-proof
        last_day_of_month = 27
        while last_day_of_month < 32:
            last_day_of_month += 1
            test_date = '{}-{}-{}'.format(graph_end_year, graph_end_month, last_day_of_month)
            try:
                graph_end_datetime = datetime.datetime.strptime(test_date, '%Y-%m-%d')
                self.graph_end_date = graph_end_datetime.strftime('%Y-%m-%d')
            except:
                break
        # Determine actual expected end data (NOAA Data Availability)
        two_days_prior_datetime = datetime.datetime.today() - datetime.timedelta(days=2)
        if graph_end_datetime > two_days_prior_datetime:
            self.actual_data_end_date = two_days_prior_datetime.strftime('%Y-%m-%d')
        else:
            self.actual_data_end_date = self.graph_end_date

if __name__ == '__main__':
    test = Main(2019, 7, 10)
    print(test.graph_start_date)
    print(test.graph_end_date)
