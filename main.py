import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import csv

month_average_file = "month_average.csv"
climate_data_file ="climate_data.csv"

example_file = pd.read_csv(".\\data\\202302A.CSV")
firstline = example_file.columns
del example_file

data_filename = ""
startyear = 2023
endyear = 2026

def generate_csv_month_average_values():

    with open (month_average_file, "w", newline="", encoding="utf-8") as output_file:

        # set ';' as delimiter (German Excel)
        csv_writer = csv.writer(output_file, delimiter=";")

        # copy header
        csv_writer.writerow(firstline)

        # try every filename possible
        for year in range(startyear, endyear+1):
            for month in range(1, 13):

                data_filename = f".\\data\\{year}{month:02d}A.CSV"

                try:
                    # open file to calculate the average from
                    month_data = pd.read_csv(data_filename)
                    

                    # ignore the "Time" column
                    month_data = month_data.drop(columns=["Zeit"], errors="ignore")

                    # try to convert NaN values to Numbers in order to calculate the average values in the next step
                    numeric_data = month_data.apply(
                        lambda column: pd.to_numeric(
                            column.astype(str)
                            .str.replace(",", ".", regex=False)
                            .str.strip(),
                            errors="coerce"
                        )
                    )

                    # calculate the average mean value for each datapoint rounded on the second position
                    average = numeric_data.mean()
                    formatted_averages = [
                        "" if pd.isna(value)
                        else f"{value:.2f}".replace(".", ",") # uncomment the second part if you don't use German decimal system e.g in Excel
                        for value in average
                    ]

                    #write the average value to the values
                    csv_writer.writerow([f"{year}{month:02d}", *formatted_averages])
                    
                except FileNotFoundError:
                    # if the filename doesn't exist
                    print(data_filename, "doesnt exist")

def generate_csv_climate_data():

    # read the month average file
    df = pd.read_csv(month_average_file, sep=";", decimal=",")

    # get month from monthstamp
    df["month"] = df["Zeit"].astype(str).str[4:6]

    # average month lines
    climate_data = df.groupby("month").mean(numeric_only=True).round(2)

    # save as csv
    climate_data.to_csv(
        "climate_data.csv",
        sep=";",
        decimal=",",
        encoding="utf-8-sig"
    )

def generate_climate_diagram():
    # read climate data file
    df = pd.read_csv(climate_data_file, sep=";", decimal=",")

    # generate nd array of rain values
    rain = df["Regen/Monat(mm)"].to_numpy()
    sum_of_rain = rain.sum()

    # generate nd array of temperature
    temperature = df["Temperatur Aussen(℃)"].to_numpy()
    mean_temperature = temperature.mean()

    # add the last and the fist value to the other site of the array (-> continuous line)
    temperature = np.r_[temperature[-1], temperature, temperature[0]]

    # x-Axis
    months_extended = np.arange(0,14)

    # linechart
    plt.style.use("_mpl-gallery")

    fig, ax1 = plt.subplots()

    # Background
    ax1.set_facecolor("xkcd:cream")

    # scale for rain values
    rain_scaled = rain / 2

    # stair diagram rain (fill)
    ax1.stairs(
        rain_scaled,
        edges=np.arange(0.5, 13.5, 1),
        baseline=0,
        fill=True,
        color="xkcd:lightblue"
    )

    # stair diagram rain (outline)
    ax1.stairs(
        rain_scaled,
        edges=np.arange(0.5, 13.5, 1),
        baseline=0,
        color="xkcd:blue",
        linewidth=2.5
    )

    # temperature curve
    ax1.plot(months_extended, temperature, color="red", linewidth=2.5, marker="o")

    # x-Axis month
    ax1.set_xlim(0, 13)
    ax1.set_xticks(np.arange(1, 13))
    ax1.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])

    # y-Axis temperature
    ax1.set_ylim(-15, 50)
    ax1.set_yticks(np.arange(-15, 51, 5))
    ax1.set_yticklabels(np.arange(-15, 51, 5), color="red")
    ax1.set_ylabel("Temperatur (°C)", color="red")
    

    # y-Axis rain
    ax2 = ax1.secondary_yaxis(
        "right",
        functions=(lambda y: y * 2, lambda y: y / 2)
    )
    ax2.set_ylabel("Rain (mm)", color="xkcd:blue")
    ax2.tick_params(axis="y", colors="xkcd:blue")

    # other text typical for climate diagrams
    plt.text(0, -10, f"{mean_temperature:.2f}°C", color="red")
    plt.text(9.2, -10, f"{int(sum_of_rain)}mm", color="xkcd:blue")
    plt.text(0.2, 40, "Bornheim(Germany)\n 120m a.s.l.")

    # save diagram
    plt.savefig("climate_diagram.png", dpi=300, bbox_inches="tight")
    plt.close()

if __name__ == '__main__':
    generate_csv_month_average_values()
    generate_csv_climate_data()
    generate_climate_diagram()