#!/usr/bin/env python3
import yaml
import json
import pandas as pd
import requests
import time

def read_token(token_fp):
    with open(token_fp, 'r') as token_file:
        token = json.load(token_file)
    return token

def collect_activities(access_token, max_results_per_page, max_pages, activity_start_window):
    activities_url = f"https://www.strava.com/api/v3/athlete/activities?access_token={access_token}"
    page = 1
    response = requests.get(activities_url + '&per_page=' + str(max_results_per_page) + '&page=' + str(page) + '&after=' + str(activity_start_window), verify=False)
    response = response.json()
    df = pd.DataFrame(response)

    while page < max_pages:
        page += 1
        response = requests.get(activities_url + '&per_page' + str(max_results_per_page) + '&page=' + str(page) + '&after=' + str(activity_start_window), verify=False)
        if response.status_code != 200:
            print(response.status_code)
            print(response.headers)
            quit()
        response = response.json()
        if not(response): break
        df_new = pd.DataFrame(response)
        df = df.append(df_new, ignore_index=True)
        time.sleep(10)

    try: df = df.drop(columns=['map'])
    except: pass
    return df


def write_activities(df, pickle_fn, csv_fn):
    df.to_pickle(pickle_fn)
    df.to_csv(csv_fn)

def collect_activity_kudos(activity_ids, access_token, max_results_per_page, max_pages, pickle_fn):
    page = 1
    df = pd.DataFrame()
    results = {}
    for activity_id in activity_ids:
        activity_kudos_url = f"https://www.strava.com/api/v3/activities/{activity_id}/kudos?access_token={access_token}"
        response = requests.get(activity_kudos_url + '&per_page=' + str(max_results_per_page) + '&page=' + str(page), verify=False)
        if response.status_code != 200:
            print(response.status_code)
            print(response.headers)
            print("Last Activity for Kudos:")
            print(activity_id)
            df = pd.DataFrame(list(results.items()))
            df.to_pickle(pickle_fn)
            quit()
        response = response.json()
        for i in response:
            print(i)
            kudo_giver = i['firstname'] + ' ' + i['lastname']
            if kudo_giver in results.keys(): results[kudo_giver] += 1
            else: results[kudo_giver] = 1
        time.sleep(15)
    df = pd.DataFrame(list(results.items()))
    return df

def main():

    # Read in Config
    with open('config.yml', 'r') as ymlfile:
        config_yml = yaml.safe_load(ymlfile)
    max_results_per_page = config_yml["strava"]["max_results_per_page"]
    max_pages = config_yml["strava"]["max_pages"]
    activity_start_window = config_yml["strava"]["activity_start_window"]
    strava_activity_pickle_fn = config_yml["strava"]["strava_activity_pickle_fn"]
    strava_activity_kudos_pickle_fn = config_yml["strava"]["strava_activity_kudos_pickle_fn"]
    strava_activity_csv_fn = config_yml["strava"]["strava_activity_csv_fn"]
    strava_activity_kudos_csv_fn = config_yml["strava"]["strava_activity_kudos_csv_fn"]
    token_fp = config_yml["strava"]["token_fp"]

    # Read OAuth Tken
    token = read_token(token_fp)
    access_token = token["access_token"]

    # Collect Activity data & save locally
    df_activities = collect_activities(access_token, max_results_per_page, max_pages, activity_start_window)

    # Get Exercise IDs for current year and then kudos for each activity
    curr_year = list(pd.to_datetime(df_activities["start_date_local"]).dt.year.unique())[0]
    curr_year_df = df_activities[pd.to_datetime(df_activities["start_date_local"]).dt.year == curr_year]
    curr_year_activity_ids = list(curr_year_df["id"])
    df_kudos = collect_activity_kudos(curr_year_activity_ids, access_token, max_results_per_page, max_pages, strava_activity_kudos_pickle_fn)

    # Save exercise data locally
    write_activities(df_activities, strava_activity_pickle_fn, strava_activity_csv_fn)
    write_activities(df_kudos, strava_activity_kudos_pickle_fn, strava_activity_kudos_csv_fn)

main()
