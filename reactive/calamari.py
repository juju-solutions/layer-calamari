
from charmhelpers import fetch
from charmhelpers.core import hookenv
from charms.reactive import when, when_not, set_state
import subprocess


@when_not('calamari.installed')
def install_calamari():

    # In (temporary) lieu of resources, we're going to be a fat charm
    hookenv.status_set('maintenance', 'Installing packages')

    subprocess.check_output([
                            'pip',
                            'install',
                            'files/python-apt-0.7.8.tar.gz'
                            ])

    # Configure the sources defined in config.yaml
    fetch.configure_sources()

    packages = ['apache2',
                'libapache2-mod-wsgi',
                'libcairo2',
                'supervisor',
                'python-cairo',
                'libpq5',
                'postgresql',
                'python-twisted',
                'python-txamqp',
                'python-greenlet',
                'python-sqlalchemy',
                'python-gevent',
                # 'curl',
                # 'build-essential',
                # 'openssl',
                # 'libssl-dev'.
                'python-m2crypto',
                'python-virtualenv',
                # 'git',
                # 'python-dev',
                # 'swig',
                # 'libzmq-dev',
                # 'g++',
                'postgresql-9.3',
                # 'postgresql-server-dev-9.3',
                # 'libcairo2-dev',
                'python-pip',
                # 'libpq-dev',
                'ruby',
                # 'debhelper',
                # 'python-mock',
                # 'python-configobj',
                # 'cdbs',
                'gem',
                'ruby1.9.1',
                # 'ruby1.9.1-dev',
                # 'make',
                # 'devscripts',
                'software-properties-common',
                'python-support',
                'salt-master',
                'salt-minion',
                'salt-syndic'
                ]
    fetch.apt_install(fetch.filter_installed_packages(packages))

    # This specific version of salt will only install cleanly via
    # easy_install-2.7 (easy_install isn't enough because of the reactive venv)
    subprocess.check_output(['easy_install-2.7', 'files/salt-2014.7.4.tar.gz'])

    subprocess.check_output(['dpkg', '-i', 'files/diamond_3.4.67_all.deb'])
    subprocess.check_output([
                            'dpkg',
                            '-i',
                            'files/ceph-deploy_1.5.28trusty_all.deb'
                            ])

    # Install dashboard
    subprocess.check_output([
                            'mkdir',
                            '-p',
                            '/opt/calamari/webapp/content/login',
                            '/opt/calamari/webapp/content/manage',
                            '/opt/calamari/webapp/content/admin'
                            ])

    subprocess.check_output([
                            'tar',
                            'zxf',
                            'files/calamari-login.tar.gz',
                            '-C',
                            '/opt/calamari/webapp/content/login'
                            ])

    subprocess.check_output([
                            'tar',
                            'zxf',
                            'files/calamari-manage.tar.gz',
                            '-C',
                            '/opt/calamari/webapp/content/manage'
                            ])

    subprocess.check_output([
                            'tar',
                            'zxf',
                            'files/calamari-admin.tar.gz',
                            '-C',
                            '/opt/calamari/webapp/content/admin'
                            ])

    # Configure salt
    # /etc/salt/master: master: 52.35.93.95 max_open_files: 100000

    subprocess.check_output([
                            'dpkg',
                            '-i',
                            'files/calamari-server_1.3.1.1-1trusty_amd64.deb'
                            ])

    # Check if the admin- settings are available
    hookenv.status_set('blocked', '')

    # Do your setup here.
    #
    # If your charm has other dependencies before it can install,
    # add those as @when() clauses above., or as additional @when()
    # decorated handlers below
    #
    # See the following for information about reactive charms:
    #
    #  * https://jujucharms.com/docs/devel/developer-getting-started
    #  * https://github.com/juju-solutions/layer-basic#overview
    #
    set_state('calamari.installed')

def initialize_calamari():
    # Require these to be set on deploy (block on it)
    # and move this into the config_changed hook. Also, what happens
    # if calamari is already initialized? Is this repeatable?
    config = hookenv.config()
    subprocess.check_output(['calamari-ctl',
                             'initialize',
                             '--admin-username=%s' % config['admin-username'],
                             '--admin-password=%s' % config['admin-password'],
                             '--admin-email=%s' % config['admin-email']
                             ])

    hookenv.status_set('ready', '')

@when('calamari.installed')
@when('config.changed')
def config_changed():
    config = hookenv.config()

    if config.changed('admin-username') or \
       config.changed('admin-password') or \
       config.changed('admin-email'):
        # Re-initialize calamari if the admin- has changed
        initialize_calamari()
