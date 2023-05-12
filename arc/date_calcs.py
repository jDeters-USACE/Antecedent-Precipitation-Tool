#  This software was developed by United States Army Corps of Engineers (USACE)
#  employees in the course of their official duties.  USACE used copyrighted,
#  open source code to develop this software, as such this software
#  (per 17 USC § 101) is considered "joint work."  Pursuant to 17 USC § 105,
#  portions of the software developed by USACE employees in the course of their
#  official duties are not subject to copyright protection and are in the public
#  domain.
#
#  USACE assumes no responsibility whatsoever for the use of this software by
#  other parties, and makes no guarantees, expressed or implied, about its
#  quality, reliability, or any other characteristic.
#
#  The software is provided "as is," without warranty of any kind, express or
#  implied, including but not limited to the warranties of merchantability,
#  fitness for a particular purpose, and noninfringement.  In no event shall the
#  authors or U.S. Government be liable for any claim, damages or other
#  liability, whether in an action of contract, tort or otherwise, arising from,
#  out of or in connection with the software or the use or other dealings in the
#  software.
#
#  Public domain portions of this software can be redistributed and/or modified
#  freely, provided that any derivative works bear some notice that they are
#  derived from it, and any modified versions bear some notice that they have
#  been modified.
#
#  Copyrighted portions of the software are annotated within the source code.
#  Open Source Licenses, included in the source code, apply to the applicable
#  copyrighted portions.  Copyrighted portions of the software are not in the
#  public domain.


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

from datetime import datetime, timedelta

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

    yesterday_datetime = datetime.today()- timedelta(days=2)
    observation_datetime = datetime.strptime(observation_date, '%Y-%m-%d')
    if observation_datetime > yesterday_datetime:
        observation_datetime = yesterday_datetime
    return observation_datetime

class DateCalc(object):
    """Calculates and stores all dates for the Antecedent Precipitation Tool"""

    def __init__(self, year, month, day, gridded):
        self.observation_datetime = rectify_inputs(year, month, day)
        self.calculate(gridded)

    def calculate(self, gridded):
        """Calculates all dates for the Antecedent Precipitation Tool"""
        self.observation_date = self.observation_datetime.strftime('%Y-%m-%d')
        self.observation_day = self.observation_datetime.strftime('%d')
        self.observation_month = self.observation_datetime.strftime('%m')
        self.observation_year = int(self.observation_datetime.strftime('%Y'))
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
        antecedent_period_start_datetime = self.observation_datetime - timedelta(days=89)
        self.antecedent_period_start_date = antecedent_period_start_datetime.strftime('%Y-%m-%d')
        # Calculate graph start date (~7 months prior to obs_date)
        start_month_datetime = self.observation_datetime - timedelta(days=203)
        graph_start_month = start_month_datetime.strftime('%m')
        graph_start_year = start_month_datetime.strftime('%Y')
        self.graph_start_date = '{}-{}-01'.format(graph_start_year, graph_start_month)
        # Calculate graph end date (end of the previous month next year)
        graph_start_datetime = datetime.strptime(self.graph_start_date, '%Y-%m-%d')
        day_before_datetime = graph_start_datetime - timedelta(days=1)
        graph_end_year = int(day_before_datetime.strftime('%Y')) + 1
        graph_end_month = day_before_datetime.strftime('%m')
        # Test for last date of month to be Leap-year-proof
        last_day_of_month = 27
        while last_day_of_month < 32:
            last_day_of_month += 1
            test_date = '{}-{}-{}'.format(graph_end_year, graph_end_month, last_day_of_month)
            try:
                graph_end_datetime = datetime.strptime(test_date, '%Y-%m-%d')
                self.graph_end_date = graph_end_datetime.strftime('%Y-%m-%d')
            except:
                break
        # Determine actual expected end data (NOAA Data Availability)
        if gridded is False:
            prior_datetime = datetime.today() - timedelta(days=2)
        elif gridded is True:
            prior_datetime = datetime.today() - timedelta(days=4)
        if graph_end_datetime > prior_datetime:
            self.actual_data_end_date = prior_datetime.strftime('%Y-%m-%d')
        else:
            self.actual_data_end_date = self.graph_end_date

if __name__ == '__main__':
    test = DateCalc(2022, 2, 25, False)
    print(test.normal_period_data_start_date)
    print(test.actual_data_end_date)
    print(test.observation_date)
    print(test.antecedent_period_start_date)
