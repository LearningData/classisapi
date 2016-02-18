import os
import yaml
import json
import subprocess
import datetime
from fabric.api import *
from fabric.operations import run, get, local

with open('classis/epf_configs.yaml', 'r') as config_file:
    schools = yaml.load(config_file)

env.user = 'azureuser'
env.hosts = ['demo.learningdata.net:3535']
deploy_to = '/home/demo/classisapi'

#Restarts apache server
def restart_apache():
    sudo("service apache2 restart")

#Test the app
def test():
    run("source .env/bin/activate && python manage.py test")

#Get latest tag
def get_tag():
    try:
        version = subprocess.check_output(
            ['git', 'describe', '--abbrev=0', '--tags']
        )
    except:
        version = 'master'

    return version.strip()

#Gets a short hash for the commit the tag points to
def get_tag_hash(tag):
    return subprocess.check_output(
        ['git', 'rev-parse', '--short', tag]
    ).strip()

#Gets the release name as a timestamp
def get_release_name():
    return str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

#Pack latest version app with setuptools
def pack():
    tag = get_tag()
    local('git clone --branch %s' % tag \
          + ' git@github.com:LearningData/classisapi.git ' \
          + ' /tmp/classisapi')
    local('tar -czvf /tmp/classisapi.tar.gz --directory=/tmp  classisapi' \
          " --exclude='.git*'")

#Link the current app directory
def symlinks(release_name):
    run('rm -rf %s/classisapi' % deploy_to)
    run('cp -pr %s/releases/%s %s/classisapi' %
        (deploy_to, release_name, deploy_to))

#Backup the database
def db_backup(release_name):
    file = 'classisapi-%s-pre-deployment.sql' % release_name
    run('mysqldump -p$DB_PASS -u class classisapi > /tmp/%s' % file);

#Run migration for database
def db_migrate():
    run('source .env/bin/activate && python manage.py db upgrade')

#Upload the package to host
def upload(release_name):
    run('mkdir -p %s/releases/%s' % (deploy_to, release_name))
    put('/tmp/classisapi.tar.gz', '/tmp/classisapi.tar.gz')
    run('tar -xzvf /tmp/classisapi.tar.gz -C %s/releases/%s ' \
        '--strip-components 1' %
        (deploy_to, release_name))

#Clean after deployment
def cleanup():
    local('rm -rf /tmp/classisapi')
    local('rm /tmp/classisapi.tar.gz')
    run('rm -rf /tmp/classisapi /tmp/classisapi.tar.gz')

#Setup the app: necesarry folders and files
def setup():
    run('mkdir -p releases')
    run('touch deployment.log')

#Upload production settings
def upload_settings():
    put('settings_prod.json', 'settings.json')

#Update virtual env for the new deployment
def update_venv(release_name):
    run('.env/bin/pip install -r releases/%s/requirements.txt' % release_name)
    run('cp -pr .env releases/%s/' % release_name)

#Install dependencies and requirements
def install():
    #sudo('sh install-dependencies.sh')
    try:
        with open(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'settings_prod.json')
        ) as settings_file:
            ENV_VARS = json.load(settings_file)
    except:
        ENV_VARS = {}

    run('echo "\n#ENVIRONMENT VARIABLES\n" >> .env/bin/activate')
    for key, value in ENV_VARS.iteritems():
        try:
            run('echo "export %s=\"%s\"" >> .env/bin/activate' % (key, value))
        except KeyError:
            pass
    run('.env/bin/python .env/bin/activate_this.py')
    #restart_apache()

#Get the deploying user
def get_user():
    hostname = subprocess.check_output(['hostname']).strip()
    username = subprocess.check_output(['id', '-u', '-n']).strip()
    return username + '@' + hostname

#Updates the deployment.log
def update_log(release_name):
    tag = get_tag()
    hash = get_tag_hash(tag)
    timestamp = str(datetime.datetime.now())
    message = timestamp + ': Branch ' + tag + \
            ' (' + hash + ') as release ' + release_name + \
            ' deployed by ' + get_user()
    run("echo '%s' >> deployment.log" % message)

#Deploy a completely functional app from scratch
def bootstrap():
    pass

#Remove old db dumps
def clean_dumps(max=2):
    output = run('ls -xtr /tmp/classisapi-*-pre-deployment.sql')
    files = output.split()
    remove_files = files[:-max]
    for file in remove_files:
        run('rm %s' % file)

#Remove old releases
def keep_releases(max=3):
    output = run('ls -xtr releases/')
    dirs = output.split()
    remove_dirs = dirs[:-max]
    for dir in remove_dirs:
        run('rm -rf releases/%s' % dir)

#Rollback to previous release
def rollback():
    with cd(deploy_to):
        output = run('ls -xtr releases/')
        dirs = output.split()
        previous_release = dirs[-2:2][0]
        symlinks(previous_release)
        with cd('classisapi'):
            install()
        timestamp = str(datetime.datetime.now())
        message = timestamp + ': Rollback to release ' + previous_release + \
                ' by ' + get_user()
        run("echo '%s' >> deployment.log" % message)

#Deploy app
def deploy():
    release_name = get_release_name()
    pack()
    db_backup(release_name)
    with cd(deploy_to):
        setup()
        upload(release_name)
        update_venv(release_name)
        with cd('releases/%s' % release_name):
            test()
        symlinks(release_name)
        with cd('classisapi'):
            install()
            db_migrate()
        update_log(release_name)
        keep_releases()
    cleanup()
    clean_dumps()

#Task to download icons and reports from remote servers
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
        remote_tar_file = 'school_%s.tar.gz' % type
        run("find " + remote_dir + \
            " -name '*." + ext + "' -exec ls {} \; " \
            "| grep -P '/[a-z0-9]+." + ext + "'" \
            "| tar --transform 's,%s,,' " \
            "-czvf /tmp/%s -T -" % (remote_dir[1:], remote_tar_file))
        get('/tmp/%s' % remote_tar_file, local_dir)
        local("tar -xzvf %s/%s -C %s " \
              "--strip-components 2" % (local_dir, remote_tar_file, local_dir))
        run('rm /tmp/%s' % remote_tar_file)
        local("rm %s/%s" % (local_dir, remote_tar_file))

