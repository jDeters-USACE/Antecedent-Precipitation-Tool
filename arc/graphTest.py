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

import os
import pandas
import pickle
from datetime import datetime

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.split(MODULE_PATH)[0]

convert_to_feet = True

if convert_to_feet is True:
    units = 'in'
else:
    Sunits = 'mm'

# Example data
data_type = 'PRCP'
# Load data (deserialize)
pickle_folder = os.path.join(ROOT, 'cached')
pickle_path = os.path.join(pickle_folder, 'demo_data.pickle')
with open(pickle_path, 'rb') as handle:
    unserialized_data = pickle.load(handle)
Dates = unserialized_data[0]
rolling30day = unserialized_data[1]
graph_start_date = unserialized_data[2]
finalDF = unserialized_data[3]
graph_end_date = unserialized_data[4]
forecast_setting = unserialized_data[5]
normal_low_series = unserialized_data[6]
normal_high_series = unserialized_data[7]
yMax = unserialized_data[8]
rolling_30_day_max = unserialized_data[9]
first_point_y_rolling_total = unserialized_data[10]
first_point_x_date_string = unserialized_data[11]
first_point_xytext = unserialized_data[12]
second_point_y_rolling_total = unserialized_data[13]
second_point_x_date_string = unserialized_data[14]
second_point_xytext = unserialized_data[15]
third_point_y_rolling_total = unserialized_data[16]
third_point_x_date_string = unserialized_data[17]
third_point_xytext = unserialized_data[18]

# Build Stations Table

station_table_values = [["Weather Station Name", "Coordinates", "Elevation (ft)", "Distance (mi)",
                          r"Elevation $\Delta$", r"Weighted $\Delta$", "Days (Normal)", "Days (Antecedent)"],
                         ['SEARCHLIGHT', '35.4661, -114.9217', 3540.026, 40.256, 724.604, 47.285, 11190, 90]] #1
station_table_values.append(['MITCHELL CAVERNS', '34.9436, -115.5469', 4350.066, 10.307, 85.436, 5.519, 80, 0]) #2
station_table_values.append(['MTN PASS', '35.4703, -115.5436', 4729.987, 30.708, 465.357, 28.109, 1, 0]) #3
station_table_values.append(['MTN PASS 1SE', '35.4592, -115.5311', 4776.903, 29.794, 512.273, 28.67, 56, 0]) #4
station_table_values.append(['BAKER', '35.2761, -116.0628', 961.942, 40.437, 3302.688, 151.747, 4, 0]) #5
station_table_values.append(['AMBOY', '34.5592, -115.7442', 647.966, 38.318, 3616.644, 155.826, 20, 0]) #6
station_table_values.append(['NEEDLES AP', '34.7675, -114.6189', 890.092, 48.53, 3374.538, 185.605, 2, 0]) #7
#station_table_values.append(['SACRAMENTO EXECUTIVE AP', '38.506, -121.495', '15.091', 0, 7.547, 0.246, 11339, 278]) #8
#station_table_values.append(['SACRAMENTO EXECUTIVE AP', '38.506, -121.495', '15.091', 0, 7.547, 0.246, 11339, 278]) #9
#station_table_values.append(['SACRAMENTO EXECUTIVE AP', '38.506, -121.495', '15.091', 0, 7.547, 0.246, 11339, 278]) #10
#station_table_values.append(['LINEAR INTERPOLATION', '', '', '', '', '', 7, 2]) #11

num_stations_used = len(station_table_values) - 1

# Import Graphing Modules
from matplotlib import dates
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerLine2D
# Make graph tic marks face outward
from matplotlib import rcParams
rcParams['xtick.direction'] = 'out'
rcParams['ytick.direction'] = 'out'

# Construct Figure
#plt.ion() # MAKES PLOT.SHOW() NON-BLOCKING
fig = plt.figure(figsize=(17, 11))
fig.set_facecolor('0.77')
fig.set_dpi(140)
if data_type == 'PRCP':
#    if num_stations_used < 14:

    ax1 = plt.subplot2grid((9, 10), (0, 0), colspan=10, rowspan=6)
    ax2 = plt.subplot2grid((9, 10), (6, 3), colspan=7, rowspan=2)
    ax3 = plt.subplot2grid((9, 10), (6, 0), colspan=3, rowspan=2)
    ax4 = plt.subplot2grid((9, 10), (8, 3), colspan=7, rowspan=1)
#    if num_stations_used > 10:
#        ax1 = plt.subplot2grid((9, 10), (0, 0), colspan=10, rowspan=5)
#        ax2 = plt.subplot2grid((9, 10), (5, 3), colspan=7, rowspan=2)
#        ax3 = plt.subplot2grid((9, 10), (5, 0), colspan=3, rowspan=2)
#        ax4 = plt.subplot2grid((9, 10), (7, 3), colspan=7, rowspan=1)
    # Add Logo
    images_folder = os.path.join(ROOT, 'images')
    logoFile = os.path.join(images_folder, "RD.png")
    logoFile = os.path.join(images_folder, "RD_1_0.png")
    logo = plt.imread(logoFile)
#    img = fig.figimage(X=logo, xo=0.35, yo=0.85)
    img = fig.figimage(X=logo, xo=118, yo=20)


else:
    ax1 = plt.subplot2grid((9, 10), (0, 0), colspan=10, rowspan=7)
    ax2 = plt.subplot2grid((9, 10), (7, 3), colspan=7, rowspan=2)
    ax3 = plt.subplot2grid((9, 10), (7, 0), colspan=3, rowspan=2)

import matplotlib.dates as dates
import matplotlib.ticker as ticker
# Configure ticks on main graph
ax1.xaxis.set_major_locator(dates.MonthLocator())
# 16 is a slight approximation since months differ in number of days.
ax1.xaxis.set_minor_locator(dates.MonthLocator(bymonthday=16))
ax1.xaxis.set_major_formatter(ticker.NullFormatter())
ax1.xaxis.set_minor_formatter(dates.DateFormatter('%b\n%Y'))
for tick in ax1.xaxis.get_minor_ticks():
    tick.tick1line.set_markersize(0)
    tick.tick2line.set_markersize(0)
    tick.label1.set_horizontalalignment('center')
ax1.tick_params(axis='x', which='minor', bottom=False)


# Remove axis from second subplot (For displaying tables)
ax2.axis('off')
ax3.axis('off')
ax2.axis('tight')
ax3.axis('tight')
if data_type == 'PRCP':
    ax4.axis('off')
    ax4.axis('tight')

# Create a truncated date range to allow for incomplete current water years
truncate = str(Dates[len(rolling30day)-1])[:10]
truncDates = pandas.date_range(graph_start_date, truncate)

# Plot Data on Graph
ax1.plot(truncDates.to_pydatetime(),
            finalDF[graph_start_date:graph_end_date],
            color='black',
            linewidth=1,
            drawstyle='steps-post',
            label='Daily Total')

# PLOT FORECAST DATA (If enabled)
if forecast_setting is True:
    try:
        ax1.plot(days,
                    mm,
                    color='red',
                    linewidth=1.2,
                    drawstyle='steps-post',
                    label='Daily Total Forecast')
    except:
        pass

# Plot Rollin 30-day total
if data_type != 'SNWD':
    ax1.plot(truncDates.to_pydatetime(),
                rolling30day[graph_start_date:graph_end_date],
                linewidth=1.2,
                label='30-Day Rolling Total',
                color='blue')

# Plot area between normal high and normal low 30-day rolling totals
ax1.fill_between(Dates.to_pydatetime(),
                    normal_low_series[graph_start_date:graph_end_date],
                    normal_high_series[graph_start_date:graph_end_date],
                    color='orange',
                    label='30-Year Normal Range',
                    alpha=0.5)

# Set the minimum Y value to 0 and the Max Y value to just above the max value
if yMax == None:
    max30 = rolling_30_day_max
    max20 = normal_high_series[graph_start_date:graph_end_date].max()
    if max30 > max20:
        yMax = max30*1.03
    else:
        yMax = max20*1.03
    ax1.set_ylim(ymin=0, ymax=yMax)
else:
    ax1.set_ylim(ymin=0, ymax=float(yMax))
    yMax = yMax

# Force the Min and Max X Values to the Graph Dates
graph_start_datetime = datetime.strptime(graph_start_date, '%Y-%m-%d')
graph_end_datetime = datetime.strptime(graph_end_date, '%Y-%m-%d')
ax1.set_xlim([graph_start_datetime, graph_end_datetime])



# Configure Labels
handles, labels = ax1.get_legend_handles_labels()
ax1.legend(handles, labels)
ax1.set_ylabel(u'Rainfall (Inches)', fontsize=20)

# Mark / Label Sampling Points
if data_type == 'PRCP':
    ax1.set_title("Antecedent Precipitation and 30-Year Normal Range from NOAA's Daily Global Historical Climatology Network",
                  fontsize=20)
#            ax1.set_title('NOAA - National Climatic Data Center - Daily Global'
#                          ' Historical Climatology Network - Rainfall Data',
#                          fontsize=20)

    if first_point_y_rolling_total is not None:
        first_point_label = first_point_x_date_string
        ax1.annotate(first_point_label, xy=(first_point_x_date_string, first_point_y_rolling_total), xycoords='data',
                        xytext=first_point_xytext,
                        textcoords='offset points',
                        size=13,
                        # bbox=dict(boxstyle="round", fc="0.8"),
                        arrowprops=dict(arrowstyle="simple",
                                        fc="0.4", ec="none",
                                        connectionstyle="arc3,rad=0.5"),
                    )

    if second_point_y_rolling_total is not None:
        second_point_label = second_point_x_date_string
        ax1.annotate(second_point_label, xy=(second_point_x_date_string, second_point_y_rolling_total), xycoords='data',
                        xytext=second_point_xytext,
                        textcoords='offset points',
                        size=13,
                        # bbox=dict(boxstyle="round", fc="0.8"),
                        arrowprops=dict(arrowstyle="simple",
                                        fc="0.4", ec="none",
                                        connectionstyle="arc3,rad=0.5"),
                    )

    if third_point_y_rolling_total is not None:
        third_point_label = third_point_x_date_string
        ax1.annotate(third_point_label, xy=(third_point_x_date_string, third_point_y_rolling_total), xycoords='data',
                        xytext=third_point_xytext,
                        textcoords='offset points',
                        size=13,
                        # bbox=dict(boxstyle="round", fc="0.8"),
                        arrowprops=dict(arrowstyle="simple",
                                        fc="0.4", ec="none",
                                        connectionstyle="arc3,rad=0.5"),
                    )

# Build Rain Table
col_labels = ['30 Days Ending',
              r"30$^{th}$ %ile" + " ({})".format(units),
              r"70$^{th}$ %ile" + " ({})".format(units),
              "Observed Rainfall",
              'Wetness Condition',
              'Condition Value',
              'Month Weight',
              'Product']
row_labels = ["1st Prior 30",
              '2nd Prior 30',
              '3rd Prior 30',
              'Result']
rain_table_vals = [['30 Days Ending', r"30$^{th}$ %ile" + "  ({})".format(units), r"70$^{th}$ %ile" + "  ({})".format(units), "Observed ({})".format(units),
                    'Wetness Condition', 'Condition Value', 'Month Weight', 'Product'],
                   ['2017-1-23', 50.343, 120.34, 150.3434, 'Wet', 3, 3, 9],
                   ['2016-12-24', 50.343, 120.343, 150.3434, 'Wet', 3, 2, 6],
                   ['2016-11-25', 50.343, 120.343, 150.3434, 'Wet', 3, 1, 3],
                   ['Result', "", "", "", "", "", "", 'Wetter than Normal - 18']]

# Build Description Table
description_table_values = [["Coordinates", '35.040, -115.408'],
                            ["Observation Date", '2018-04-30'],
                            ["Elevation (ft)", '4264.63'],
                            [r"WebWIMP H$_2$O Budget", 'Dry Season'],
                            ["Drought Index (PSDI)", 'Severe drought']]

# Define Colors
lightgrn = (0.5, 0.8, 0.5)
lightblu = (0.4, 0.5, 0.8)
lightred = (0.8, 0.5, 0.5)
light_grey = (0.87, 0.87, 0.87)
white = (1,1,1)
black = (0,0,0)

# Plot Description Table
description_table_colors = [[light_grey, white],
                            [light_grey, white],
                            [light_grey, white],
                            [light_grey, lightred],
                            [light_grey, lightred]]
table2 = ax3.table(cellText=description_table_values,
                   colWidths=[0.4, 0.54],
                   cellColours=description_table_colors,
                   loc='center left')
table2.auto_set_font_size(False)
table2.set_fontsize(10)

colors1 = [[light_grey, light_grey, light_grey, light_grey, light_grey, light_grey, light_grey, light_grey],
           [white, white, white, white, white, white, white, white],
           [white, white, white, white, white, white, white, white],
           [white, white, white, white, white, white, white, white],
           [white, white, white, white, white, white, white, lightblu]]

station_table_colors = [[light_grey, light_grey, light_grey, light_grey, light_grey, light_grey, light_grey, light_grey]]
for row in station_table_values[1:]:
    station_table_colors.append([white, white, white, white, white, white, white, white])

# Plot Rain Table
the_table = ax2.table(cellText=rain_table_vals,
#                      rowLabels=row_labels,
#                      colLabels=col_labels,
                      cellColours=colors1,
                      colWidths=[0.112, 0.111, 0.111, 0.120, 0.135, 0.114, 0.1, 0.18],
                      loc='center')
the_table.auto_set_font_size(False)
the_table.set_fontsize(10)

# Plot Stations Table
table3 = ax4.table(cellText=station_table_values,
                   cellColours=station_table_colors,
                   colWidths=[0.25, 0.15, 0.095, 0.097, 0.087, 0.087, 0.104, 0.132],
                   loc='center')
table3.auto_set_font_size(False)
table3.set_fontsize(10)

# determine bottom value by table rows
if len(station_table_values) < 5:
    bValue = 0.01
elif len(station_table_values) == 5:
    bValue = 0.02
elif len(station_table_values) == 6:
    bValue = 0.03
elif len(station_table_values) == 7:
    bValue = 0.035
elif len(station_table_values) == 8:
    bValue = 0.04
elif len(station_table_values) == 9:
    bValue = 0.050
elif len(station_table_values) == 10:
    bValue = 0.055
elif len(station_table_values) == 11:
    bValue = 0.059
elif len(station_table_values) == 12:
    bValue = 0.068

# Determine horizontal separation value by table rows
if len(station_table_values) < 10:
    hValue = 0.00
elif len(station_table_values) < 12:
    hValue = 0.17
else:
    hValue = 0.19

# Remove space between subplots
plt.subplots_adjust(wspace=0.00,
                    hspace=hValue,
                    left=0.045,
                    bottom=bValue,
                    top=0.968,
                    right=0.99)


fig_path = 'C:\\Temp\\test.pdf'
fig_exists = os.path.exists(fig_path)
fig_num = 1
while fig_exists:
    try:
        os.remove(fig_path)
        break
    except Exception:
        fig_path = 'C:\\Temp\\test{}.pdf'.format(fig_num)
        fig_num += 1
        fig_exists = os.path.exists(fig_path)
test_saving = True
if not test_saving:
    plt.show()
else:
    fig.savefig(fig_path, facecolor='0.77')
    import pylab
    pylab.close(fig)
    import subprocess
    subprocess.Popen(fig_path, shell=True)