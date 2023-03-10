from LJ_FUNCTION import file_count, LJ_Info, remove_RLJ, LJ_ID

# Define the path to the case study for generating the LJ and Sigma Information
main_path = "Cluster_InfoCSV"
case_study = "Brisbane_2014-11-27"
dir_path = main_path + "/" + case_study
case_study = case_study + "_Cluster"
cluster_amount = file_count(dir_path)
LJ_Info(dir_path, case_study, cluster_amount)

# Remove the redundant lightning jump which happen within a 6 mins range
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5749929/
time_interval = 2
mins_range = 6
gap = int(mins_range / time_interval)
remove_RLJ(dir_path, case_study, cluster_amount, gap)

# Assign ID for each seperated lightning jump within each cluster of the selected case study
LJ_ID(dir_path, case_study, cluster_amount, gap)