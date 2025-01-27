# setup_replication

This Ansible Galaxy Role configures Replication on PostgresSQL versions: 14 on instances previously
configured.

## Requirements

The requirements for this ansible galaxy role are:

1. Ansible
2. `community.general` - utilized when creating aditional users during a
   Postgres Install. Only on primary nodes.
3. `hypersql_devops.postgres` -> `setup_repo` - for repository installation
4. `hypersql_devops.postgres` -> `install_dbserver` - for installation of
   PostgreSQL binaries.
5. `hypersql_devops.postgres` -> `init_dbserver` - for the initialization of
   primary server

## Role variables

When executing the role via ansible there are three required variables:

- **_os_**

Operating Systems supported are: CentOS7 and RHEL7

- **_pg_version_**

  Postgres Versions supported are: `14.0`, `14.1`, `14.2`, `14.3`,`14.3`, `14.5`, `14.6`

- **_pg_type_**

  Database Engine supported are: `PG`

The rest of the variables can be configured and are available in the:

  * [roles/setup_replication/defaults/main.yml](./defaults/main.yml)
  * [roles/setup_replication/vars/PG.yml](./vars/PG.yml)

## Dependencies

The `setup_replication` role does not have any dependencies on any other roles.

## Example Playbook

### Hosts file content

Content of the `inventory.yml` file:

```yaml
---
all:
  children:
    primary:
      hosts:
        primary1:
          ansible_host: xxx.xxx.xxx.xxx
          private_ip: xxx.xxx.xxx.xxx
    standby:
      hosts:
        standby1:
          ansible_host: xxx.xxx.xxx.xxx
          private_ip: xxx.xxx.xxx.xxx
          upstream_node_private_ip: xxx.xxx.xxx.xxx
          replication_type: synchronous
        standby2:
          ansible_host: xxx.xxx.xxx.xxx
          private_ip: xxx.xxx.xxx.xxx
          upstream_node_private_ip: xxx.xxx.xxx.xxx
          replication_type: asynchronous
```

### How to include the `setup_replication` role in your Playbook

Below is an example of how to include the `setup_replication` role:

```yaml
---
- hosts: standby
  name: Setup Postgres replication on Instances
  become: true
  gather_facts: true

  collections:
    - hypersql_devops.postgres

  pre_tasks:
    - name: Initialize the user defined variables
      set_fact:
        pg_version: 14.6
        pg_type: "PG"

  roles:
    - setup_replication
```

Defining and adding variables is done in the `set_fact` of the `pre_tasks`.

All the variables are available at:

  * [roles/setup_replication/defaults/main.yml](./defaults/main.yml)
  * [roles/setup_replication/vars/PG_RedHat.yml](./vars/PG_RedHat.yml)
  * [roles/setup_replication/vars/PG_Debian.yml](./vars/PG_Debian.yml)

## Database engines supported

### Community PostgreSQL

| Distribution                      |               14 |
| --------------------------------- |:----------------:|
| CentOS 7                          |:white_check_mark:|
| CentOS 8                          |:white_check_mark:|
| Ubuntu 20.04 LTS (Focal) - x86_64 |:white_check_mark:|

- :white_check_mark: - Tested and supported

## Playbook execution examples

```bash
# To deploy community Postgres version 14 on CentOS7 hosts with the user centos
$ ansible-playbook playbook.yml \
  -u centos \
  -i inventory.yml \
  --extra-vars="pg_version=14.6 pg_type=PG"
```

## License

BSD

## Author information

Author:
  * [Sang Myeung Lee](https://github.com/sungmu1)

Original Author:
  * EDB Postgres - www.enterprisedb.com
