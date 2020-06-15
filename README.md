  # Antecedent Rainfall Calculator

## What is it?

An automation tool that evaluates three climatological parameters to assist in the making and documenting of various determinations required by policy for the execution of USACE&#39;s Regulatory Program.

## Usage

Rapidly, accurately, and effortlessly determine whether any of the following problematic circumstances exist for a given Latitude, Longitude, and Date:

- Dry Season
- Drought Conditions
- Lower than normal antecedent precipitation
- Greater than normal antecedent precipitation
- Automatically document the basis of these decisions for the administrative record.

## Utility

- **Site Visit:** Determine whether you should use the problematic circumstances portion of the delineation manual and regional supplement
- **Data Sheet Review:** Determine whether the applicant or their agent should have used the problematic circumstances portion of the delineation manual and regional supplement
- **Satellite / Aerial Imagery Interpretation:** Determine whether the seasonality, drought conditions, and antecedent precipitation are appropriate for a given image to be used for:
  - **Hydrology Indicators:** Saturation on aerial imagery, Inundation on aerial imagery
  - **Connectivity:** Continuous saturation or inundation visible between potential WotUS
  - **Apparent differences in vegetation:**
    - Reduced vigor of upland crops in suspected depressions or swales
    - Greener vegetation in suspected depressions or swales compared to dry/yellow surrounding vegetation
    - Location and extent of any other wetland signatures (e.g. vernal pool stratified vegetation rings)

Basic Methodology for each determination

- **Wet/Dry Season Determination**
  - **Protocol:** Based on ERDC instructions for calculating dry season provided in the regional supplements to the 1987 Delineation Manual
  - **Data Source:** WebWIMP (The Web-based, Water-Budget, Interactive, Modeling Program)
- **Drought Conditions:**
  - **Protocol:** Based on ERDC recommendations in the regional supplements to the 1987 Delineation Manual, which suggests using drought indices, specifically the Palmer Drought Severity Index (PDSI) to help inform drought conditions.
  - **Data source:** Climate Division scale PDSI data calculated and hosted by NOAA monthly

- **Antecedent Precipitation Condition**
  - **Protocol:** Combined method of 30-day rolling totals and NRCS Engineering Field Handbook weighting factors (Combined Method) (see Section 4.3, Sprecher and Warne (2000)).
    - Sprecher, S.W. and Andrew G. Warne, A.G., 2000. _ **Accessing and Using Meteorological Data to Evaluate Wetland Hydrology** _. WRAP Technical Notes Collection_,_ ERDC/EL TR-WRAP-00-1. U.S. Army Engineer Research and Development Center, Vicksburg, MS. ([http://el.erdc.usace.army.mil/elpubs/pdf/wrap00-1/wrap00-1.pdf](http://el.erdc.usace.army.mil/elpubs/pdf/wrap00-1/wrap00-1.pdf))
    - Natural Resources Conservation Service, 1997. _ **Hydrology tools for wetland determination** _. Chapter 19, Engineering field handbook_._ D. E. Woodward, ed. USDA-NRCS, Fort Worth, TX. ([http://www.info.usda.gov/CED/ftp/CED/EFH-Ch19.pdf](http://www.info.usda.gov/CED/ftp/CED/EFH-Ch19.pdf))

  - **WETS Tables were discontinued, so the protocol was amended:** New monthly 30th and 70th percentile data was needed, but since we were generating this data ourselves anyway, we took the opportunity to improve the procedure.
  - **Problems with old monthly procedure**
    - Months vary in length, yet we are comparing monthly totals to 30-day rolling totals.

    - Precipitation varies throughout the month
      - However, the monthly total protocol simply graphs straight lines between the last days of each month.
      - Ex. If it only rains at the end of September in a given area, this method artificially spreads that rain out evenly across each day.
  - **Solution - Compare 30-day rolling totals to 30-day rolling totals**
    - We get 30 years and 1 month of precipitation data, and use it to calculate 30 years of 30-day rolling totals.
    - We then calculate the 30th and 70th percentile values for each day of the year
    - Now, when we compare the current year 30-day rolling total to the 30-year normal, we are directly comparing the same exact type of measurement, at the same resolution.

- **Station Selection**

**Manual Procedure**

    - The original method required a PM to manually locate weather station data that they deemed most appropriate to use for their site, with a note that it should be relatively close and at a similar elevation.
    - No real parameters were provided for when a station is too far, or how you can be sure there is not a closer station that you have overlooked.
    - Most PMs were using only the stations used to create the WETS tables, which are limited to approximately 1 or 2 per county in California.
    - If any dates were missing from the record, PMs were having to backfill from the other WETS station in the county, which might be drastically further away.

**Problems with the manual method**

    - Weather patterns vary greatly over relatively small lateral distances, especially if those distances are accompanied with large changes in elevation.
    - There are typically quite a few stations closer in distance and elevation, but PMs don&#39;t know how to find them all, and most people don&#39;t know how to calculate distance using geographic coordinates. Even if they did, sorting through all of the available stations based on distance and elevation difference would be extremely time-consuming.
    - The completeness of the record needs to be considered, as you can&#39;t create a 30-year normal from disparate data sources.
    - This would require PMs to download a large number of complete records from every available weather station, do the math on how many of dates from the pertinent range are missing from each dataset, and factor this information into the selection of their primary weather station.

**Solution - Automated Querying of NOAA&#39;s data by programmatically**

    - Acquiring a list of every weather station in the U.S.
    - Locating those within a specific distance from the observation point
    - Sorting the selected stations by a weighted difference value

      - Incorporates both distance and difference in elevation
      - Created experimentally by matching the result to the best professional judgment of contributing PMs around the country.

- For the Primary Station

  - Eliminating stations with insufficient records for the 30 year normal period and the relevant portion of the current year supporting the Antecedent Precipitation calculation

- For the Missing Dates (Secondary Station, etc.)

  - Sorting the remaining station by the weighted difference value
  - Weighted differences are recalculated in relation to the Primary Station&#39;s location and elevation, rather than the observation point
  - Attempt to backfill the missing dates from the Primary Station with the resorted stations until there are no missing dates.

**Forthcoming improvements in the newest version**

- Secondary Station candidates will be ranked by similarity.

  - The average difference in PRCP values on overlapping dates will be calculated
  - The weighted Difference values will be augmented to incorporate the avg. diff

- NOAA&#39;s new Daily Gridded PRCP Dataset will be used, when:

  - No suitably complete Primary Station records are available, or
  - Additional stations needed to complete the record are: Very far from the Primary Station, or situated at very different elevations than the Primary Station
  - Currently, these situations, which arise in limited portions of the United States with poor weather station coverage, create problematic 30-year normal ranges, which cannot truly reflect the normal conditions in any one location.
  - The new Gridded Daily PRCP Dataset has its own issues, but in these particularly challenging scenarios, it will provide a better good faith effort to use the best available science to make our determinations.

  - Data source:Precipitation data from best available local weather stations from NOAA&#39;s Daily Global Historical Climatology Network (DGHCN)
