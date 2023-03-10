import os
import math
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta
from LJ_FUNCTION import spec_year, start_end_row, ICCG_Collect, plot_func, polygon_func, initial_centroid, next_moment_cluster, blank_plot, target_cluster_plot, centroid_record, centroid_record_func

###############################################Define Variables############################################
gap = 2
hrs = 24
mins = 60
time_interval = int(hrs * mins / gap)
case_lon = -29.35
case_lat = 152.6333
case_range = 6
DBSCAN_scale = 20
DBSCAN_dist = 0.25
case_area = "Brisbane"
case_date = "2014-11-27"
date_format = "%Y-%m-%d"
case_study = case_area + "_" + case_date

# Construct the specific polygon
min_lon, max_lon, min_lat, max_lat, area_polygon = polygon_func(case_lat, case_lon, case_range)

################################################Read In Data###############################################
# Obtain the csv file name and only read the 'date' data for preprocessing
filename='/g/data/er8/lightning/data/wz_ltng/wz_ltng_' + case_date[0:4] + '.csv'

# Compute the start and end rows of the case study from the csv and extract the data
start_row, end_row, light_date, i_date = start_end_row(case_date)
df_date = pd.read_csv(filename, sep=',', skiprows = range(start_row, end_row), nrows = light_date.iloc[i_date]["Lightning_Count"])

############################################Start Cluster Tracking#########################################
# Create the coordinate, timestamp information for each instance
df_date["coordinate"] = df_date[["longitude", "latitude"]].apply(list, axis = 1)
df_date["datetime"] = df_date['date'] + " " + df_date["time"]
df_date["datetime"] = pd.to_datetime(df_date["datetime"])

# Collect the lightning within each minutes in the target area
## First set the default datetime with the given dataframe (e.g. 2014-01-01 00:00:00)
datetime_default = datetime.strptime(df_date.iloc[0]["date"], date_format)

## Then set time gap to split the dataframe (e.g. 2 minutes)
## In this code, we investigate on the selected date data within each minute (24 * 60 / 2 groups of data)
current_start_time = datetime_default
current_end_time = datetime_default + timedelta(minutes = gap)

track_num = 0       # Tracking ID (initial) of the Cluster in the Cast Study
initial = True      # Set the condition for checking whether the recorded moment as starting or not
track_TS = {}       # Lightning Amount of each Cluster
track_cluster = {}  # Cluster's path with Cluster Label (closest to the tracked cluster) of all lightning at each time
track_centroid = [] # Centroid list for adding in new tracked cluster center
for j in range(time_interval):
    # Extract Coordinates' Information from the Total Lightning Dataframe
    IC, CG, ICCG = ICCG_Collect(current_start_time, current_end_time, df_date, area_polygon)
    current_end_time += timedelta(minutes = gap)
    current_start_time += timedelta(minutes = gap)
    coordinate_list = (np.array(ICCG["coordinate"].tolist()))

    # Try to apply the DBSCAN for clustering purpose with pre-determined hyper-parameters
    try:
        clustering = DBSCAN(eps = DBSCAN_dist, min_samples = DBSCAN_scale).fit(coordinate_list)
        ICCG["Cluster_Label"] = clustering.labels_
    
        # Generate the list for storing the clustering type (label) without the outlier(s)
        try:    
            cluster_list = clustering.labels_
            cluster_list = list(filter(lambda cluster_list: cluster_list != -1, cluster_list))
            check_cluster = list(set(cluster_list))
        except:
            None
        # Compute the centroid of cluster for both initial minute or the following minute(s)
        # Store the initial centroid of the major cluster
        if initial == True:
            centroid, initial, cluster_size, major_cluster = initial_centroid(ICCG, cluster_list)
            track_TS[track_num] = [cluster_size]
            track_cluster[track_num] = [major_cluster]
            track_centroid.append([centroid.x, centroid.y])
            track_num += 1
            special_start = True
        # Store the current minute's clusters' centroids
        else:
            current_centroid = next_moment_cluster(ICCG, check_cluster)
            special_start = False
        
        # Create a temporary list for updating the centroid
        temp_centroid = track_centroid.copy()
        
        # Check the closest current centroid to the recorded track_centroid
        # Store the lightning amount of the closest centroid (cluster)
        # If there is cluster that is too far away from the track_centroid, consider to switch the attention
        for i in range(len(track_centroid)):
            distance_dict = {}
            if special_start == True:
                break
            for k in range(len(current_centroid)):
                distance = math.dist(track_centroid[i], current_centroid[k])

                # Skip the centroid which is too far away from the exist centroid(s) for now
                # Record the distance of current centroid(s) which is close to the exist centroid(s)
                if distance >= 1.5:
                    continue
                else:
                    distance_dict[k] = distance

            # Fill the track of cluster information with 0 & NaN if no valid cluster is detected
            if len(distance_dict) < 1:
                track_TS[i].append(0)
                track_cluster[i].append("NaN")
                continue
            
            # Record the new cluster information into the track for further usage (TS & Cluster Plotting)
            else:
                sorted_distance_dict = sorted(distance_dict.items(), key=lambda x:x[1])
                temp_centroid[i] = current_centroid[sorted_distance_dict[0][0]]
                track_TS[i].append(ICCG.loc[ICCG['Cluster_Label'] == sorted_distance_dict[0][0]].shape[0])
                track_cluster[i].append(sorted_distance_dict[0][0])

        # Set breakpoint if processing the initial centroid
        if special_start == False:
            for i in range(len(current_centroid)):
                inside = True
                for k in range(len(track_centroid)):
                    distance = math.dist(track_centroid[k], current_centroid[i])
                    if distance >= 1.5:
                        inside = False
                    else:
                        inside = True
                        break
                # Record the cluster's centroid which is too far away from the exist centroid(s)
                if inside == False:
                    temp_centroid.append(current_centroid[i])
                    track_TS[track_num] = [0] * (j+1)
                    track_TS[track_num][j] = ICCG.loc[ICCG['Cluster_Label'] == i].shape[0]
                    track_cluster[track_num] = ["NaN"] * (j+1)
                    track_cluster[track_num][j] = i
                    track_num += 1
            track_centroid = temp_centroid.copy()

    # If there is no lightning at the moment, append 0 to the Time-Series record        
    except:
        for i in track_TS:
            track_TS[i].append(0)
            track_cluster[i].append("NaN")

# Fill 0 to the first cluster lightning amount list if the first strike
if len(track_TS[0]) < time_interval:
    track_TS[0] = [0] * (time_interval - len(track_TS[0])) + track_TS[0]

# Store the lightning amount at each time-interval within the selected tracked cluster to csv
df_cluster = pd.DataFrame.from_dict(track_TS)
df_cluster.to_csv('Cluster_TSCSV/' + case_study + '.csv', index=False, header=True)

# ###########################################Start Cluster Plotting##########################################
# ##########################################Start Centroid Recording#########################################
## Set time gap to split the dataframe (e.g. 2 minutes)
## In this code, we investigate on the selected date data within each minute (24 * 60 / 2 groups of data)
current_start_time = datetime_default
current_end_time = datetime_default + timedelta(minutes = gap)

# Start Target Cluster(s)' Track Plotting / Recording Information
target_cluster_track = list(track_TS)
centroid_record_list = []
for i in range(len(target_cluster_track)):
    centroid_record_list.append({"Coordinate" : [], "Scale_KM": [], "TOT_dense" : [], "IC_num" : [], "CG_num" : [], "IC_amp" : [], "CG_amp" : []})

for j in range(time_interval):
    # Extract Coordinates' Information from the Total Lightning Dataframe
    IC, CG, ICCG = ICCG_Collect(current_start_time, current_end_time, df_date, area_polygon)
    current_end_time += timedelta(minutes = gap)
    current_start_time += timedelta(minutes = gap)
    coordinate_list = (np.array(ICCG["coordinate"].tolist()))

    # Try to apply the DBSCAN for clustering purpose with pre-determined hyper-parameter(s)
    try:
        clustering = DBSCAN(eps = DBSCAN_dist, min_samples = DBSCAN_scale).fit(coordinate_list)
        ICCG["Cluster_Label"] = clustering.labels_
        for k in target_cluster_track:
            ''' 
            This Sectin is only for Visualisation purpose, please ignore it if plot is unnecessary
            ax = plt.axes(projection = ccrs.PlateCarree())
            plt.suptitle("Brisbane Lightning Cluster" + '\n' + str(current_start_time))
            ax.set_extent([min_lon, max_lon, min_lat, max_lat], ccrs.PlateCarree())
            target_cluster_plot(k, track_cluster[k], j, current_start_time, ICCG, ax)
            '''
            centroid_record_list = centroid_record_func(centroid_record_list, track_cluster, k, j, ICCG, True)
    except:
        for k in target_cluster_track:
            ''' 
            This Sectin is only for Visualisation purpose, please ignore it if plot is unnecessary
            # ax = plt.axes(projection = ccrs.PlateCarree())
            # plt.suptitle("Brisbane Lightning Cluster" + '\n' + str(current_start_time))
            # ax.set_extent([min_lon, max_lon, min_lat, max_lat], ccrs.PlateCarree())
            # blank_plot(k, j, current_start_time, ax)
            '''
            centroid_record_list = centroid_record_func(centroid_record_list, track_cluster, k, j, ICCG, False)

# Store the target cluster(s)' information to csv for further usage
dir_path = os.path.join('Cluster_InfoCSV/', case_study)
if not os.path.isdir(dir_path):
    os.mkdir(dir_path)
for i in range(len(centroid_record_list)):    
    df_centroid = pd.DataFrame.from_dict(centroid_record_list[i])
    file_path = 'Cluster_InfoCSV/' + case_study + "/" + case_study + "_Cluster" + str(i) + '.csv'
    df_centroid.to_csv(file_path, index=False, header=True)