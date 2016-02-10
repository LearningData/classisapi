import os
import yaml
from fabric.api import env, warn_only
from fabric.operations import run, get, local

with open('classis/epf_configs.yaml', 'r') as config_file:
    schools = yaml.load(config_file)

def s(school):
    env.config = schools[school]
    env.hosts = env.config["host"]

def download_remote_files(local_dir, type='icons'):
    if type == 'icons':
        remote_dir = env.config["dir_icons"]
        ext = 'jpeg'
    else:
        remote_dir = env.config["dir_reports"]
        ext = 'pdf'

    local('mkdir -p ' + local_dir)

    if remote_dir != '' and local_dir != '':
        files = []
        with warn_only():
            remote_files = run("find " + remote_dir + \
                               " -name '*." + ext + "' -exec ls {} \; " \
                               "| grep -P '/[a-z0-9]+." + ext + "'")
            files += remote_files.splitlines()
        for file in files:
            get(file, local_dir)
