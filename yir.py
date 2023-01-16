#!/usr/bin/env python3
import yaml
import json
import pandas as pd
from collections import OrderedDict
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

def pre_processing(df):
    # Add activity day of week
    df["start_date_local_day_of_week"] = pd.to_datetime(df["start_date_local"]).dt.day_of_week
    # Convert start_date_local from Str to DateTime
    df["start_date_local"] = pd.to_datetime(df["start_date_local"])

def generate_summary(df):
    summary = OrderedDict()
    total_num_events = df.shape[0]
    summary["num_events"] = total_num_events

    # Elapsed Time (Provided in Seconds)
    total_elapsed_time_seconds = int(df["elapsed_time"].sum())
    summary["total_elapsed_time"] = {
        "seconds": total_elapsed_time_seconds,
        "minutes": round(total_elapsed_time_seconds / 60, 2),
        "hours": round(total_elapsed_time_seconds / 60 / 60, 2)
    }
    max_elapsed_time_seconds = int(df["elapsed_time"].max())
    max_elapsted_time_activity = json.dumps(df.loc[df["elapsed_time"].idxmax()].to_json())
    summary["longest_elapsed_time"] = {
        "seconds": max_elapsed_time_seconds,
        "minutes": round(max_elapsed_time_seconds / 60, 2), 
        "hours": round(max_elapsed_time_seconds / 60 / 60, 2),
        "activity": max_elapsted_time_activity 
    }
    avg_elapsed_time_seconds = round(int(df["elapsed_time"].mean()), 2)
    summary["avg_elapsed_time"] = {
        "seconds": avg_elapsed_time_seconds,
        "minutes": round(avg_elapsed_time_seconds / 60, 2),
        "hours": round(avg_elapsed_time_seconds / 60 / 60, 2)
    }


    # Distance (Provided in Meters)
    total_distance_meters = int(df["distance"].sum())
    summary["total_distance"] = {
        "meters": total_distance_meters,
        "miles": round(total_distance_meters * 0.000621371192, 2),
        "kilometers": round(total_distance_meters / 1000.00, 2),
        "trips_around_the_world": round(total_distance_meters / 40075020, 2)
    }
    max_distance_meters = int(df["distance"].max())
    max_distance_activity = df.loc[df["distance"].idxmax()].to_json()
    max_distance_activity = 0
    summary["max_distance"] = {
        "meters": max_distance_meters,
        "miles": round(max_distance_meters * 0.000621371192, 2),
        "kilometers": round(max_distance_meters / 1000.00, 2),
        "activity": max_distance_activity
    }   
    avg_distance_meters = round(int(df["distance"].mean()), 2)
    summary["avg_distance"] = {
        "meters": avg_distance_meters,
        "miles": round(avg_distance_meters * 0.000621371192, 2),
        "kilometers": round(avg_distance_meters / 1000.00, 2)
    }

    # Elevation (Provided in Meters)
    total_elevation_gain_meters = int(df["total_elevation_gain"].sum())
    summary["total_elevation_gain"] = {
        "meters": total_elevation_gain_meters,
        "feet": round(total_elevation_gain_meters * 3.280839895, 2),
        "miles": round(total_elevation_gain_meters * 0.000621371192, 2),
        "trips_to_mt_everest_summit": round(total_elevation_gain_meters / 8848.86216, 2)
    }

    sport_type_freq_distribution = df["sport_type"].value_counts().to_dict()
    summary["sport_type_distribution"] = sport_type_freq_distribution

    activity_day_freq_distribution_ints = df["start_date_local_day_of_week"].value_counts().to_dict()
    activity_day_freq_distribution_days = OrderedDict()
    activity_day_freq_distribution_days["Monday"] = activity_day_freq_distribution_ints[0]
    activity_day_freq_distribution_days["Tuesday"] = activity_day_freq_distribution_ints[1]
    activity_day_freq_distribution_days["Wednesday"] = activity_day_freq_distribution_ints[2]
    activity_day_freq_distribution_days["Thursday"] = activity_day_freq_distribution_ints[3]
    activity_day_freq_distribution_days["Friday"] = activity_day_freq_distribution_ints[4]
    activity_day_freq_distribution_days["Saturday"] = activity_day_freq_distribution_ints[5]
    activity_day_freq_distribution_days["Sunday"] = activity_day_freq_distribution_ints[6]

    summary["activity_day_freq_distribution"] = {
        "int": activity_day_freq_distribution_ints,
        "days": activity_day_freq_distribution_days
    }

    return summary

def generate_kudos_summary(df):
    temp_dict = df.sort_values(1, ascending=False).to_dict('records')
    result_dict = OrderedDict()
    for kudoer in temp_dict:
        name = kudoer[0]
        count = kudoer[1]
        result_dict[name] = count
    return result_dict

def main():
    with open('config.yml', 'r') as ymlfile:
        config_yml = yaml.safe_load(ymlfile)
    strava_activity_pickle_fn = config_yml["strava"]["strava_activity_pickle_fn"]
    strava_activity_kudos_pickle_fn = config_yml["strava"]["strava_activity_kudos_pickle_fn"]

    df = pd.read_pickle(strava_activity_pickle_fn)
    df_kudos = pd.read_pickle(strava_activity_kudos_pickle_fn)
    pre_processing(df)

    # Summarize results for each year
    summary_results = OrderedDict()
    years = list(pd.to_datetime(df["start_date_local"]).dt.year.unique())
    curr_year = years[-1]
    for year in years:
        year = int(year)
        filtered_df = df[pd.to_datetime(df["start_date_local"]).dt.year == year]
        summary_results[year] = generate_summary(filtered_df)

        if year == curr_year:
            summary_results[year]["kudos"] = generate_kudos_summary(df_kudos)

    print(json.dumps(summary_results, indent=4))

main()
