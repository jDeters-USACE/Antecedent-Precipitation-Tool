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
##       watershed_summary.py       ##
##  ------------------------------- ##
##      Writen by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################

# Import Standard Libraries
import time
from datetime import datetime

# Import 3rd Party Libraries
import numpy
import matplotlib.pyplot as plt
import pylab
import matplotlib.patheffects as path_effects



def parse_results(results_list):
    parse_result = []
    # List Red coloration items
    red_items = [
        "Dry Season",
        'Mild drought',
        'Moderate drought',
        'Severe drought',
        'Extreme drought'
    ]
    # Define colors for cell color matrices
    light_green = (0.5, 0.8, 0.5)
    light_blue = (0.4, 0.5, 0.8)
    light_red = (0.8, 0.5, 0.5)
    light_grey = (0.85, 0.85, 0.85)
    white = (1, 1, 1)
    black = (0, 0, 0)
    pie_red = '#ff9999'
    pie_green = '#99ff99'
    pie_blue = '#66b3ff'
    pie_orange = '#ffcc99'
    # Get Numbers of each Main APT Condition and all APT Values
    antecedent_precipitation_score_sum = 0
    num_wet = 0
    num_normal = 0
    num_dry = 0
    num_total = 0
    for result_tuple in results_list:
        # Add current antecedent_precipiation_score
        antecedent_precipitation_score_sum += result_tuple[0]
        num_total += 1
        if result_tuple[1] == 'Wetter than Normal':
            num_wet += 1
        elif result_tuple[1] == 'Normal Conditions':
            num_normal += 1
        elif result_tuple[1] == 'Drier than Normal':
            num_dry += 1
    # Find average antecedent_precipitation_score
    average_antecedent_precipitation_score = round((antecedent_precipitation_score_sum / num_total), 2)
    # Determine name and color of Preliminary Decision
    if average_antecedent_precipitation_score < 10:
        preliminary_determination = "Drier than Normal"
        preliminary_determination_color = light_red
    elif average_antecedent_precipitation_score >= 10 and average_antecedent_precipitation_score < 15:
        preliminary_determination = 'Normal Conditions'
        preliminary_determination_color = light_green
    elif average_antecedent_precipitation_score >= 15:
        preliminary_determination = 'Wetter than Normal'
        preliminary_determination_color = light_blue
    # Get percentages for each AP Class for Pie Chart
    pie_sizes = []
    pie_labels = []
    pie_colors = []
    if num_wet > 0:
        wet_percent = round((num_wet / num_total), 2)
        pie_sizes.append(wet_percent)
        pie_labels.append('Wetter than Normal')
        pie_colors.append(pie_blue)
    if num_normal > 0:
        normal_percent = round((num_normal / num_total), 2)
        pie_sizes.append(normal_percent)
        pie_labels.append('Normal Conditions')
        pie_colors.append(pie_green)
    if num_dry > 0:
        dry_percent = round((num_dry / num_total), 2)
        pie_sizes.append(dry_percent)
        pie_labels.append('Drier than Normal')
        pie_colors.append(pie_red)
    # Get unique set of result conditions
    results_set = list(set(results_list))
    # Sort results by ap score
    results_set.sort(key=lambda x: x[0], reverse=True)
    # Determine frequency of each unique condition set
    sampling_points_table_values = []
    sampling_points_table_colors = []
    # Add First row of values and colors
    sampling_points_table_values.append([
        'Antecedent Precipitation Score',
        'Antecedent Precipitation Condition',
        r"WebWIMP H$_2$O Balance",
        'Drought Index (PDSI)',
        '# of Points'])
    sampling_points_table_colors.append([light_grey, light_grey, light_grey, light_grey, light_grey])
    for result_tuple in results_set:
        # Get count of unique list's occurance
        count = results_list.count(result_tuple)
        result_list = list(result_tuple)
        # Add occurance to end of list
        final_list = result_list + [count]
        # Append list to sampling_points_table_values
        sampling_points_table_values.append(final_list)
        # Create color row for sampling_points_table_colors
        color_row = []
        # Determine which color to add for each item in row
        for item in final_list:
            # Can't say "if item in red_items because some PDSI values
            #  are marked with (2011-11) or similar indications that they
            #  are using the previous month's PDSI Value, so we'll work
            red = False
            for red_item in red_items:
                if red_item in str(item):
                    red = True
                    break
            if red is True:
                color_row.append(light_red)
            else:
                color_row.append(white)
        # Append color row to sampling_points_table_colors
        sampling_points_table_colors.append(color_row)
    # Add items to result list
    parse_result.append(average_antecedent_precipitation_score)
    parse_result.append(preliminary_determination)
    parse_result.append(preliminary_determination_color)
    parse_result.append(pie_sizes)
    parse_result.append(pie_labels)
    parse_result.append(pie_colors)
    parse_result.append(sampling_points_table_values)
    parse_result.append(sampling_points_table_colors)
    return parse_result



def create_summary(site_lat, site_long, observation_date, geographic_scope, huc, huc_size, results_list, watershed_summary_path, grid_selection):
    """Creates Summary of results and prints to pdf"""
    # Define Colors
    light_grey = (0.85, 0.85, 0.85)
    white = (1, 1, 1)

    # Parse results list using function
    parsed_results = parse_results(results_list)

    # Unpack function results
    avg_ap_score = parsed_results[0]
    preliminary_determination = parsed_results[1]
    preliminary_determination_color = parsed_results[2]
    pie_sizes = parsed_results[3]
    pie_labels = parsed_results[4]
    pie_colors = parsed_results[5]
    sampling_points_table_values = parsed_results[6]
    sampling_points_table_colors = parsed_results[7]

    # Construct Figure
    #plt.ion() # MAKES PLOT.SHOW() NON-BLOCKING
    fig = plt.figure(figsize=(13.5, 8.5))
    fig.set_facecolor('0.90')

    # Add Logo
    fig.set_dpi(135)
    import os
    MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
    ROOT = os.path.split(MODULE_PATH)[0]
    images_folder = os.path.join(ROOT, 'images')
    logoFile = os.path.join(images_folder, 'Traverse_80%_1920.png')
    logo = plt.imread(logoFile)
    img = fig.figimage(X=logo, xo=0, yo=0)
    img.set_zorder(0)

    ax1 = plt.subplot2grid((20, 9), (3, 1), colspan=4, rowspan=3)
    ax2 = plt.subplot2grid((20, 9), (7, 1), colspan=4, rowspan=2)
    ax3 = plt.subplot2grid((20, 9), (10, 1), colspan=4, rowspan=2)
    ax4 = plt.subplot2grid((20, 9), (13, 0), colspan=9, rowspan=9)
    ax5 = plt.subplot2grid((20, 18), (3, 11), colspan=4, rowspan=7)
    ax1.set_zorder(1)
    ax2.set_zorder(1)
    ax3.set_zorder(1)
    ax4.set_zorder(1)
    ax5.set_zorder(1)

    #pie_colors = [light_red, light_green, light_blue]
    patchyes, texts, autotexts = ax5.pie(pie_sizes,
                                         colors=pie_colors,
                                         labels=pie_labels,
                                         autopct='%1.1f%%',
                                         shadow=True,
                                         startangle=90)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'), path_effects.Normal()])

    for text in texts:
        text.set_color('white')
        text.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'), path_effects.Normal()])




#    for text in texts:
#        text.set_color('grey')
#    for autotext in autotexts:
#        autotext.set_color('grey')
#     Equal aspect ratio ensures that pie is drawn as a circle
#    ax4.axis('equal')

    # Remove axis from subplots (For displaying tables)
    ax1.axis('off')
    ax2.axis('off')
    ax3.axis('off')
    ax4.axis('off')
    ax5.axis('off')
    ax1.axis('tight')
    ax2.axis('tight')
    ax3.axis('tight')
    ax4.axis('tight')
    ax5.axis('tight')

    from matplotlib import patheffects

    # Add Axis Titles
    title_text_object = fig.suptitle('Antecedent Precipitation Tool v2.0 - Watershed Sampling Summary', fontsize=17, color='white')
    title_text_object.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'), path_effects.Normal()])
    ax1_title_object = ax1.set_title('User Inputs', color='white')
    ax1_title_object.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'), path_effects.Normal()])
    ax2_title_object = ax2.set_title('Intermediate Data', color='white')
    ax2_title_object.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'), path_effects.Normal()])
    ax3_title_object = ax3.set_title('Preliminary Result', color='white')
    ax3_title_object.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'), path_effects.Normal()])
    ax4_title_object = ax4.set_title('Sampling Point Breakdown', color="white")
    ax4_title_object.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'), path_effects.Normal()])

    # Create Inputs Table
    inputs_table_values = [
        ['Coordinates', '{}, {}'.format(round(float(site_lat), 6), round(float(site_long), 6))],
        ['Date', observation_date],
        ['Geographic Scope', geographic_scope],
        ['Used Gridded Precipitaton', grid_selection]
    ]

    # Create Inputs Table Colors
    inputs_table_colors = [
        [light_grey, white],
        [light_grey, white],
        [light_grey, white],
        [light_grey, white]
    ]

    # Plot inputs_table
    inputs_table = ax1.table(cellText=inputs_table_values,
                             cellColours=inputs_table_colors,
                             colWidths=[0.4, 0.355],
                             cellLoc='center',
                             loc='lower center')

    inputs_table.auto_set_font_size(False)
    inputs_table.set_fontsize(12)
    inputs_table.scale(1, 1)

    # Create Intermediate Data Table
    try:
        # Tests if huc is an actual huc or custom watershed
        huc_test = float(huc)
        watershed_name_label = 'Hydrologic Unit Code'
        watershed_name_column_width = 0.24
    except Exception:
        # Values for Custom Watershed (Float convert failed)
        watershed_name_label = 'Custom Watershed Name'
        name_length = len(huc)
        if name_length < 22:
            watershed_name_column_width = .34
        elif name_length < 30:
            watershed_name_column_width = .40
        else:
            watershed_name_column_width = 0.5
        watershed_name_column_width = name_length / 62
    num_sampling_points = len(results_list)
    intermediate_table_values = [
        [watershed_name_label, huc],
        ['Watershed Size', r'{} mi$^2$'.format(huc_size)],
        ['# Random Sampling Points', num_sampling_points]
    ]
    # Create Intermediate Data Table Colors
    intermediate_table_colors = [
        [light_grey, white],
        [light_grey, white],
        [light_grey, white]
    ]
    # Plot intermediate_data_table
    intermediate_data_table = ax2.table(cellText=intermediate_table_values,
                                        cellColours=intermediate_table_colors,
                                        colWidths=[0.40, watershed_name_column_width],
                                        cellLoc='center',
                                        loc='lower center')
    intermediate_data_table.auto_set_font_size(False)
    intermediate_data_table.set_fontsize(12)
    intermediate_data_table.scale(1, 1)

    # Create Preliminary Determination Table
    prelim_determ_table_values = [
        ['Average Antecedent Precipitation Score', avg_ap_score],
        ['Preliminary Determination', preliminary_determination]
    ]

    # Create Preliminary Determination Table Colors
    prelim_determ_table_colors = [
        [light_grey, white],
        [light_grey, preliminary_determination_color]
    ]

    # Plot preliminary determination table
    prelim_determ_table = ax3.table(cellText=prelim_determ_table_values,
                                    cellColours=prelim_determ_table_colors,
                                    colWidths=[0.58, 0.29],
                                    cellLoc='center',
                                    loc='center')
    prelim_determ_table.auto_set_font_size(False)
    prelim_determ_table.set_fontsize(12)
    prelim_determ_table.scale(1, 1)

    # Plot Sampling Points Breakdown Table
    sampling_point_table = ax4.table(cellText=sampling_points_table_values,
                                    cellColours=sampling_points_table_colors,
                                    colWidths=[0.21, 0.23, 0.16, 0.175, 0.08],
                                    cellLoc='center',
                                    loc='upper center')
    sampling_point_table.auto_set_font_size(False)
    sampling_point_table.set_fontsize(12)
    sampling_point_table.scale(1, 1)

    # Get string of today's date
    today_datetime = datetime.today()
    today_str = today_datetime.strftime('%Y-%m-%d')
    # Add Generated on today's date text
    #date_generated_text = ax1.text(0.027, 0.153, "Generated on {}".format(today_str), size=10, color='white')
    date_generated_text = fig.text(0.45, 0.93, "Generated on {}".format(today_str), size=10, color='white')
    date_generated_text.set_path_effects([path_effects.Stroke(linewidth=3, foreground='black'), path_effects.Normal()])

    # Remove space between subplots
    plt.subplots_adjust(wspace=0.00,
                        hspace=0.00,
                        left=0.00,
                        bottom=0.00,
                        top=1.00,
                        right=1.00)

    if watershed_summary_path is None:
        # Display Figure
        plt.show()
        time.sleep(1)
    else:
        # Save PDF
        print('Saving Watershed Summary figure...')
        fig.savefig(watershed_summary_path, facecolor='0.90')

        # Closing figure in memory safe way
        print('Closing figure...')
        pylab.close(fig)
        print('')
        return True


if __name__ == '__main__':
    RESULTS_LIST = [
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Not available"),
        (8,"Drier than Normal","Wet Season","Extreme wetness (2020-01)"),
        (8,"Drier than Normal","Wet Season","Severe wetness (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Incipient wetness (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Incipient drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (11,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (10,"Normal Conditions","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)"),
        (8,"Drier than Normal","Wet Season","Mild drought (2020-01)")
    ]

    # Save output as PDF
    import os
    WATERSHED_SUMMARY_PATH = 'C:\\Temp\\test.pdf'
    fig_exists = os.path.exists(WATERSHED_SUMMARY_PATH)
    fig_num = 1
    while fig_exists:
        try:
            os.remove(WATERSHED_SUMMARY_PATH)
            break
        except Exception:
            WATERSHED_SUMMARY_PATH = 'C:\\Temp\\test{}.pdf'.format(fig_num)
            fig_num += 1
            fig_exists = os.path.exists(WATERSHED_SUMMARY_PATH)

    # Don't save
#    WATERSHED_SUMMARY_PATH = None

    # Normal HUC Run
    create_summary(site_lat="38.4008283",
                   site_long="-120.8286800",
                   observation_date="2020-02-10",
                   geographic_scope='HUC8 Watershed',
                   huc='180400120000',
                   huc_size=1266.29,
                   results_list=RESULTS_LIST,
                   watershed_summary_path=WATERSHED_SUMMARY_PATH)

    # Custom Watershed Run
#    create_summary(site_lat="38.4008283",
#                   site_long="-120.8286800",
#                   observation_date="2020-02-10",
#                   geographic_scope='Custom Polygon',
#                   huc='Cosumnes River (ESRI)',
#                   huc_size=1266.29,
#                   results_list=RESULTS_LIST,
#                   watershed_summary_path=WATERSHED_SUMMARY_PATH)

    if WATERSHED_SUMMARY_PATH:
        import subprocess
        subprocess.Popen(WATERSHED_SUMMARY_PATH, shell=True)

len('Cosumnes River (ESRI)')
