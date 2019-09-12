"""
Viz.AI Home Assignment
Lior Trieman (Sep 2019)
"""

# ------------------ #
# *1* IMPORT MODULES #
# ------------------ #
import pydicom
import pandas as pd
import tarfile
from tqdm import tqdm
import sys
import requests
import os
import statistics

# ---------------------------- #
# *2* DOWNLOAD FILE FROM URL   #  ## >python LT_script.py https://s3.amazonaws.com/viz_data/DM_TH.tgz
# ---------------------------- #

ARCHIVE_PATH = str(sys.argv[1])  # "DM_TH.tgz"
print(ARCHIVE_PATH)
url = ARCHIVE_PATH  # https://s3.amazonaws.com/viz_data/DM_TH.tgz
r = requests.get(url, allow_redirects=True)
open('DM_TH_2.tgz', 'wb').write(r.content)
ARCHIVE_PATH = "DM_TH_2.tgz"

# ---------------------- #
# *3* EXTRACT ALL FILES  #
# ---------------------- #

mode = 'r*'
tar = tarfile.open(ARCHIVE_PATH)
slices = []
for member in tqdm(tar.getmembers()):
    f = tar.extractfile(member)
    dcm = pydicom.read_file(f)
    slices.append(dcm)

# -------------------------------------------------- #
# *4* Example: get relevant data from a single slice #
# -------------------------------------------------- #
slice_0 = slices[0]
pixel_data = slice_0.PixelData
patient_name = slice_0.PatientName
patient_age = slice_0.PatientAge
patient_sex = slice_0.PatientSex
institution_name = slice_0.InstitutionName
study_instance_UID = slice_0.StudyInstanceUID
series_instance_UID = slice_0.SeriesInstanceUID
# print("Slice Info.:")


# ------------------------------------------------------------  #
#       ARRANGE FILES ACCORDING TO THE DICOM HIERARCHY
# IN AN APPROPRIATE DIRECTORY STRUCTURE (PATIENT/STUDY/SERIES)
# ------------------------------------------------------------  #
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root
project_dir = ROOT_DIR
# project_dir = "C:\\Users\liort\PycharmProjects\Viz_Ex"
ind = 0  # index initialization
image_dict = {}  # init dict
acq_t_list = []  # init list

for member in tqdm(tar.getmembers()):     # run on all slices/images
    f = tar.extractfile(member)
    os.chdir(project_dir)
    slice_curr = slices[ind]  # current slice using 'ind'
    p_name = slice_curr.PatientName.components  # get patient name
    study_name = slice_curr.StudyInstanceUID  # get study num
    series_name = slice_curr.SeriesInstanceUID  # get series num
    slice_acquisition_time = slice_curr.AcquisitionTime  # time from slice
    # define the name of the directory to be created
    path_name = str(p_name)
    if not os.path.exists(path_name):
        os.makedirs(path_name)
    os.chdir(path_name)
    path_name = str(study_name)
    if not os.path.exists(path_name):
        os.makedirs(path_name)
    os.chdir(path_name)
    path_name = str(series_name)
    if not os.path.exists(series_name):
        os.makedirs(series_name)
    os.chdir(path_name)
    tar.extract(member)
    if not str(p_name[0]) + str(study_name) + str(series_name) in image_dict:
        image_dict[str(p_name[0]) + str(study_name) + str(series_name)] = []
    image_dict[str(p_name[0]) + str(study_name) + str(series_name)].append(slice_acquisition_time)
    ind += 1

total_slices_num = ind  # how many slices do we have in this tar for all patients

# get min and max of each list and get a list of scan times:
scan_time_list = []
for key in image_dict:
    acq_t_list = image_dict[key]
    for item in acq_t_list:
        float(item)
    max_t = max(acq_t_list)
    min_t = min(acq_t_list)
    scan_time = float(max_t)-float(min_t)
    scan_time_list.append(scan_time)  # add scan time to list of times
avg_scan_time = statistics.mean(scan_time_list)  # calc average scan time

print("average scan time for this set of scans:", avg_scan_time)


def get_patient_name_list(slices):
    p_name_list = []
    for ind in range(0, total_slices_num-1):
        slice_curr = slices[ind]
        p_name = slice_curr.PatientName
        p_name_list.append(p_name)
    return p_name_list


def get_patient_age_list(slices):
    p_age_list = []
    for ind in range(0, total_slices_num-1):
        slice_curr = slices[ind]
        p_age = slice_curr.PatientAge
        p_age_list.append(p_age)
    return p_age_list


def get_patient_sex_list(slices):
    p_sex_list = []
    for ind in range(0, total_slices_num-1):
        slice_curr = slices[ind]
        p_sex = slice_curr.PatientSex
        p_sex_list.append(p_sex)
    return p_sex_list


def get_series_num_list(slices):
    series_num_list = []
    for ind in range(0, total_slices_num-1):
        slice_curr = slices[ind]
        series_num = slice_curr.SeriesNumber
        series_num_list.append(series_num)
    return series_num_list


def get_instance_num_list(slices):
    instance_num_list = []
    for ind in range(0, total_slices_num-1):
        slice_curr = slices[ind]
        instance_num = slice_curr.InstanceNumber
        instance_num_list.append(instance_num)
    return instance_num_list


def get_acquisition_time_list(slices):
    acquisition_time_list = []
    for ind in range(0, 405):
        slice_curr = slices[ind]
        acquisition_time = slice_curr.AcquisitionTime
        acquisition_time_list.append(acquisition_time)
    return acquisition_time_list


def get_institution_name_list(slices):
    institution_name_list = []
    for ind in range(0, total_slices_num-1):
        slice_curr = slices[ind]
        institution_name = slice_curr.InstitutionName
        institution_name_list.append(institution_name)
    return institution_name_list


# call the functions:
p_name_list = get_patient_name_list(slices)
p_age_list = get_patient_age_list(slices)
p_sex_list = get_patient_sex_list(slices)
instance_num_list = get_instance_num_list(slices)
series_num_list = get_series_num_list(slices)
acquisition_time_list = get_acquisition_time_list(slices)

p_name_set = set(p_name_list)
p_age_set = set(p_age_list)
p_sex_set = set(p_sex_list)

# print([p_name_set, p_age_set, p_sex_set ])

# create a data-frame with patient data #
df_patients = pd.DataFrame(list(zip(p_name_list, p_age_list, p_sex_list)), columns=['Names', 'age', 'sex'])
# print("df_patients", df_patients.head(5))

# get only 1 record for each patient
df_patients = df_patients.drop_duplicates(keep='first')
print("patient list:/n", df_patients)

# ------------------------------------------------------ #
# how many different hospitals do the data come from? #
# ------------------------------------------------------ #

# get number of different institutes:
institute_name_list = get_institution_name_list(slices)
institute_name_set = set(institute_name_list)
print("no of different institutions:", len(institute_name_set))
print("name of different institutions:", institute_name_set)

