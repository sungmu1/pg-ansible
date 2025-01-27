from conftest import (
    get_pg_type,
    get_pg_unix_socket_dir,
    get_pg_version,
    get_primary,
    load_ansible_vars,
    os_family,
)


def test_init_dbserver_files():
    ansible_vars = load_ansible_vars()

    pg_data = ansible_vars["pg_data"]
    pg_wal = ansible_vars["pg_wal"]
    pg_user = "postgres"
    pg_group = "postgres"

    host = get_primary()

    for pg_dir in [pg_data, pg_wal]:
        assert host.file(pg_dir).exists, "%s does not exist" % pg_dir

        assert host.file(pg_dir).is_directory, "%s is not a directory" % pg_dir

        assert host.file(pg_dir).user == pg_user, "%s is not owned by postgres" % pg_dir

        assert host.file(pg_dir).group == pg_group, "%s group is not postgres" % pg_dir

    # Test PGWAL
    assert host.file("%s/pg_wal" % pg_data).exists, "%s/pg_wal does not exist" % pg_data
    assert host.file("%s/pg_wal" % pg_data).is_symlink, (
        "%s/pg_wal is not a symlink" % pg_data
    )
    assert (
        host.file("%s/pg_wal" % pg_data).linked_to == pg_wal
    ), "%s/pg_wal is not linked to %s" % (pg_data, pg_wal)


def test_init_dbserver_service():
    host = get_primary()
    pg_version = get_pg_version()

    if os_family() == "RedHat":
        if get_pg_type() == "PG":
            service = "postgresql-%s" % pg_version
    elif os_family() == "Debian":
        if get_pg_type() == "PG":
            service = "postgresql@%s-main" % pg_version

    assert host.service(service).is_running, "Postgres service not running"

    assert host.service(service).is_enabled, "Postgres service not enabled"


def test_init_dbserver_socket():
    host = get_primary()

    if get_pg_type() == "PG":
        sockets = ["tcp://5432", "unix:///var/run/postgresql/.s.PGSQL.5432"]
    for socket in sockets:
        assert host.socket(socket).is_listening, (
            "Postgres is not listening on %s" % socket
        )


def test_init_dbserver_data_directory():
    ansible_vars = load_ansible_vars()
    pg_data = ansible_vars["pg_data"]
    pg_user = "postgres"

    host = get_primary()
    socket_dir = get_pg_unix_socket_dir()

    with host.sudo(pg_user):
        query = "SELECT setting FROM pg_settings WHERE name = 'data_directory'"
        cmd = host.run('psql -At -h %s -c "%s" postgres' % (socket_dir, query))

        data_directory = cmd.stdout.strip()
        assert host.file(data_directory).linked_to == pg_data, (
            "Postgres data_directory is not linked to '%s'" % pg_data
        )
