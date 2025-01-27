# pg-ansible tests

## Introduction

This folder contains the necessary software infrastructure required to execute
the non-regression test cases of the **hypersql_devops.postgres** Ansible Collection.

The tests are grouped by a common subject into multiple _test cases_. This
common subject could be related to a specific Role we want to test, or a
combination of several Roles with particular parameters for example.

This testing framework relies mainly on `docker` containers, `docker compose`
and `pytest`.

## Testing framework

Executing a test case consists basically in:

1. Spinning up one `docker` container in charge of running the Ansible playbook
   attached to the test case, and the tests themselves.
2. Spinning up one or more `docker` containers in charge of hosting the
   components deployed by the previous execution of the Ansible playbook.
3. Destroying the containers at the end of tests execution.

The tests are written in Python and rely on `pytest` and its `testinfra`
module. Tests related to the same test case must be located in the same file
named: `tests/test_<test_case_name>.py`.

## Directory structure

- `cases`: this folder contains one sub-folder per test case.
- `docker`: docker files and scripts.
- `scripts`: python scripts used to apply additional configuration on the
  containers.
- `tests`: `py.test` files.

### Test case directory

The test case directories are used to store all the required files necessary to
create the docker infrastructure (`docker-compose.yml`) and the Ansible files
(`inventory.yml` template, `playbook.yml`, and `vars.json`) needed to deploy
the components related to the test case.

## Running the tests

### Prerequisites

This testing framework requires the following commands/tools:

- `python3`
- `pip3`
- `docker` and `docker compose`
- `make`

To install the dependencies:

```shell
pip3 install -r requirements.txt
```

### Docker CE and compose plugin installation on Debian11

#### cgroup configuration

In order to use systemd based docker images, make sure the following grub configuration is being used in `/etc/default/grub`:

```shell
GRUB_CMDLINE_LINUX_DEFAULT="quiet cgroup_enable=memory swapaccount=1"
GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=false"
```

Apply grub configuration changes:

```shell
sudo update-grub
```

Reboot the host.

#### Docker CE installation

Packages installation:

```shell
sudo apt -y install \
  apt-transport-https ca-certificates curl gnupg2 software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/docker-archive-keyring.gpg
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"
sudo apt -y install \
  docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

Starting docker:

```shell
sudo systemctl enable --now docker
```

Adding the current user to the `docker` system group:

```shell
sudo usermod -aG docker $USER
newgrp docker
```

### Test execution

The `test-runner.py` script is intended to ease test execution through only one
command line.

Usage:

```shell
usage: test-runner.py [-h] [-j JOBS] [--configuration CONFIGURATION]
                      [--pg-version PG_VERSION [PG_VERSION ...]] [--pg-type PG_TYPE [PG_TYPE ...]]
                      [--os OS [OS ...]] [-k KEYWORD [KEYWORD ...]]

optional arguments:
  -h, --help            show this help message and exit
  -j JOBS, --jobs JOBS  Number of parallel jobs. Default: 4
  --configuration CONFIGURATION
                        Configuration file
  --pg-version PG_VERSION [PG_VERSION ...]
                        Postgres versions list. Default: ['14.6']
  --pg-type PG_TYPE [PG_TYPE ...]
                        Postgres DB engines list. Default: ['PG']
  --os OS [OS ...]      Operating systems list. Default: all
  -k KEYWORD [KEYWORD ...], --keywords KEYWORD [KEYWORD ...]
                        Execute test cases with a name matching the given keywords.
```

### Usage examples

The example below shows how to run the tests for:

- the `install_dbserver` test case
- on `centos7` and `rocky8` operating systems
- PostgreSQL engine only
- for versions `14.5`

```shell
test-runner.py \
  --pg-version 14.5 \
  --os rocky8 centos7 \
  --pg-type PG \
  -k install_dbserver

Test install_dbserver with PG/13 on centos7 ... OK
Test install_dbserver with PG/14 on centos7 ... OK
Test install_dbserver with PG/13 on rocky8 ... OK
Test install_dbserver with PG/14 on rocky8 ... OK

Tests passed: 4/4 100.00%
```

Running the tests for all the test cases, for every OS, for PostgreSQL and
EPAS, in version `14.6`:

```shell
test-runner.py \
  --pg-version 14.6
```

### Manual test execution

When implementing new test cases, it can be more efficient to execute the tests
without using the `test-runner.py` script. This can be done with the following
command lines:

```shell
export HYPERSQL_PG_TYPE=<pg-type>
export HYPERSQL_PG_VERSION=<pg-version>
make -C cases/<test-case> <os>
```

Below is an example of running the tests for test case `init_dbserver`, in
version 14.6 of PostgreSQL, on RockyLinux8:

```shell
export HYPERSQL_PG_TYPE=PG
export HYPERSQL_PG_VERSION=14.6
make -C cases/init_dbserver rocky8
```

Containers hosting Postgres and the components we had tested with the help of
the previous command are not automatically destroyed. For cleaning up those,
the following command should be executed:

```shell
make -C cases/<test-case> clean
```

Because the container are not automatically destroyed, this method is useful
for tests development and debugging: it is possible to open a shell session
on the running container.

```shell
# Fetch the container id from the output of the following command
docker ps
# Start a new bash session on the container
docker exec -it <container-id> /bin/bash
```

### Logs

In case of test failure, standard output and error are stored in dedicated
files located into the `logs` directory. Filenames are `<test_case>.stdout` and
`<test_case>.sterr`.
