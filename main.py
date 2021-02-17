# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 12:53:53 2021

original file: https://github.com/reichlab/covid19-forecast-hub-validations/blob/main/main.py

@author: Jannik Deuschel
"""

import json
import re
import os
import urllib.request
import glob
from github import Github
import sys
from pathlib import Path

from codebase.test_formatting import forecast_check, validate_forecast_file, print_output_errors
from codebase.validation_functions.forecast_date import filename_match_forecast_date

from codebase.helper.post_image import image_comment

# Pattern that matches a forecast file add to the data-processed folder.
# Test this regex using this link: https://regex101.com/r/fn22tN/1 
pat = re.compile(r"^data-processed/(.+)/\d\d\d\d-\d\d-\d\d-(Poland|Germany)-\1(-case)?\.csv")

pat_meta = re.compile(r"^data-processed/(.+)/metadata-\1\.txt$")

local = os.environ.get('CI') != 'true'

if local:
    token = None
    print("Running on LOCAL mode!!")
else:
    print("Added token")
    token  = os.environ.get('GH_TOKEN')
    print(f"Token length: {len(token)}")
    imgbb_token = os.environ.get('IMGBB_TOKEN')
if token is None:
    g = Github()
else:
    g = Github(token)
repo_name = os.environ.get('GITHUB_REPOSITORY')
if repo_name is None:
    repo_name = 'KITmetricslab/covid19-forecast-hub-de'
repo = g.get_repo(repo_name)

print(f"Github repository: {repo_name}")
print(f"Github event name: {os.environ.get('GITHUB_EVENT_NAME')}")

if not local:
    event = json.load(open(os.environ.get('GITHUB_EVENT_PATH')))
else:
    event = json.load(open("test/test_event.json"))

pr = None
comment = ''
files_changed = []

if os.environ.get('GITHUB_EVENT_NAME') == 'pull_request_target' or local:
    # Fetch the  PR number from the event json
    pr_num = event['pull_request']['number']
    print(f"PR number: {pr_num}")

    # Use the Github API to fetch the Pullrequest Object. Refer to details here: https://pygithub.readthedocs.io/en/latest/github_objects/PullRequest.html 
    # pr is the Pullrequest object
    pr = repo.get_pull(pr_num)

    # fetch all files changed in this PR and add it to the files_changed list.
    files_changed +=[f for f in pr.get_files()]
    
# Split all files in `files_changed` list into valid forecasts and other files
forecasts = [file for file in files_changed if pat.match(file.filename) is not None]
metadatas = [file for file in files_changed if pat_meta.match(file.filename) is not None]
rawdatas = [file for file in files_changed if file.filename[0:8] == "data-raw"]
other_files = [file for file in files_changed if (pat.match(file.filename) is None and pat_meta.match(file.filename) is None and file not in rawdatas)]


if os.environ.get('GITHUB_EVENT_NAME') == 'pull_request_target':
    # IF there are other fiels changed in the PR 
    #TODO: If there are other files changed as well as forecast files added, then add a comment saying so. 
    if len(other_files) > 0 and len(forecasts) >0:
        print(f"PR has other files changed too.")
        if pr is not None:
            pr.add_to_labels('other-files-updated')
    
    if len(metadatas) > 0:
        print(f"PR has metata files changed.")
        if pr is not None:
            pr.add_to_labels('metadata-change')
            
    if len(rawdatas) > 0:
        print(f"PR has raw files changed.")
        if pr is not None:
            pr.add_to_labels('added-raw-data')
    # Do not require this as it is done by the PR labeler action.
    if len(forecasts) > 0:
        if pr is not None:
            pr.add_to_labels('data-submission')
        
        # add picture of forecast to PR
        pic_comment = image_comment(token=imgbb_token, file=os.getcwd() + "/img/test.png")
        pr.create_issue_comment(pic_comment)

    deleted_forecasts = False
    
    # `f` is ab object of type: https://pygithub.readthedocs.io/en/latest/github_objects/File.html 
    # `forecasts` is a list of `File`s that are changed in the PR.
    for f in forecasts:
        # TODO: Add a better way of checking whether a file is deleted or not. Currently, this checks if there are ANY deletion in a forecast file.
        if f.deletions >0:
            deleted_forecasts = True
    if deleted_forecasts:
        # Add the `forecast-updated` label when there are deletions in the forecast file
        pr.add_to_labels('forecast-updated')
        comment += "\n Your submission seem to have updated/deleted some forecasts. Could you provide a reason for the updation/deletion? Thank you!\n\n"

# Download all forecasts
# create a forecasts directory
os.makedirs('forecasts', exist_ok=True)

# Download all forecasts changed in the PR into the forecasts folder
for f in forecasts:
    urllib.request.urlretrieve(f.raw_url, f"forecasts/{f.filename.split('/')[-1]}")

# Download all metadat files changed in the PR into the forecasts folder
for f in metadatas:
    urllib.request.urlretrieve(f.raw_url, f"forecasts/{f.filename.split('/')[-1]}")
    
# Run validations on each file that matches the naming convention
errors = {}
for file in glob.glob("forecasts/*.csv"):

    error_file = forecast_check(file)
    if len(error_file) >0:
    
        errors[os.path.basename(file)] = error_file
    # Check for the forecast date column: Check if dat in filename matches forecast date column
    is_err, err_message = filename_match_forecast_date(file)
    
    if is_err:
        comment += err_message + "\n"

# look for .csv files that dont match pat regex
for file in other_files:
    if file.filename[:14] == "data-processed" and ".csv" in file.filename:

        err_message = " File seems to violate naming convention"
        errors[file.filename] = [err_message]

# Print out errors    
if len(errors) > 0:
    comment+="\n\n Your submission has some validation errors. Please check the logs of the build under the \"Checks\" tab to get more details about the error. "
    print_output_errors(errors, prefix='data')

# add the consolidated comment to the PR
if comment!='' and not local:
    pr.create_issue_comment(comment)

if len(errors) > 1:
    sys.exit("\n ERRORS FOUND EXITING BUILD...")


