from . import BaseResource
import re
import os
from urlparse import urlparse
import subprocess

short_att_name_pat = re.compile(r'^HEROKU_POSTGRESQL_([^_]+)_URL$')

class HerokuPostgresql(BaseResource):
    """Heroku Postgresql database."""

    _strs = ['current_transaction', 'database_name', 'database_password', 'database_user', 'following', 'forked_from',
             'plan', 'postgresql_version', 'resource_url', 'target_transaction']
    _ints = ['num_bytes', 'num_connections', 'num_connections_waiting', 'num_tables', 'service_port']
    _dates = ['created_at', 'status_updated_at']
    _bools = ['available_for_ingress', 'hot_standby?', 'is_in_recovery?', 'standalone?']
    _lists = ['info']

    def __init__(self):
        super(HerokuPostgresql, self).__init__()
        self.resource_name = None
        self.attachment_name = None

    def __repr__(self):
        return "<heroku_postgresql v{0}:'{1}'>".format(self.postgresql_version, self.short_attachment_name)

    @property
    def short_attachment_name(self):
        try:
            return re.match(short_att_name_pat, self.attachment_name).groups(0)[0]
        except:
            return self.attachment_name

    def metrics(self):
        """Metrics for this database."""
        return self._h._get_resources(resource=(self.resource_name, 'metrics'), obj=Metrics, app=self)

    def reset(self):
        """Delete all data in database. Careful!"""
        return self._h._http_resource("PUT", (self.resource_name, 'reset'), legacy=True)

    def wait_status(self):
        return self._h._get_resource(resource=(self.resource_name, 'wait_status'), obj=WaitStatus, app=self)

    def maintenance(self):
        return self._h._get_resource(resource=(self.resource_name, 'maintenance'), obj=Maintenance, app=self)

    def exec_sql(self, sql):
        """
        Use psql subprocess to run a sql command on the database. Anything goes!
        Probably best to use psycopg2 for more robust queries...

        :param sql: the sql string to execute
        :return: subprocess output
        """
        uri = urlparse(self.resource_url)
        os.environ["PGPASSWORD"] = uri.password
        os.environ["PGSSLMODE"] = "prefer" if uri.hostname == 'localhost' else 'require'
        cmd = ["psql", "-c", sql]
        if uri.username:
            cmd += ["-U", uri.username]
        cmd += ["-h", uri.hostname, "-p", str(uri.port) or "5432", uri.path[1:]]
        return subprocess.check_output(cmd)

    def ps(self):
        sql = """
            SELECT
              {0},
              {1}
              application_name AS source,
              age(now(),xact_start) AS running_for,
              waiting,
              {2} AS query
            FROM pg_stat_activity
            WHERE
              {2} <> '<insufficient privilege>'
              AND {3}
              AND {0} <> pg_backend_pid()
              ORDER BY query_start DESC
            """.format(self._pid_column, self._state_column, self._query_column, self._state_idle_condition)
        return self.exec_sql(sql)

    @property
    def _nine_two(self):
        return float(self.postgresql_version[:3]) >= 9.2

    @property
    def _pid_column(self):
        return 'pid' if self._nine_two else 'procpid'

    @property
    def _state_column(self):
        return "state, " if self._nine_two else ""

    @property
    def _state_idle_condition(self):
        return "state <> 'idle'" if self._nine_two else "current_query <> '<IDLE>'"

    @property
    def _query_column(self):
        return 'query' if self._nine_two else 'current_query'


class Metrics(BaseResource):
    """ Heroku Postgresql metrics. """

    _dates = ['at']
    _floats = ['load_avg_1m', 'load_avg_5m', 'load_avg_15m']
    _ints = ['memory_cached', 'memory_free', 'memory_total', 'postgres_memory']

    def __repr__(self):
        return "<heroku_postgresql_metrics {0}: mem: {1}, 1m_load: {2}>".format(self.at,
                                                                                self.postgres_memory,
                                                                                self.load_avg_1m)

class WaitStatus(BaseResource):
    """ Heroku Postgresql wait status. """

    _strs = ['message']
    _bools = ['waiting?']

    def __repr__(self):
        return "<heroku_postgresql_waitstatus: {0} ({1})>".format(self.message, self.waiting_msg)

    @property
    def is_waiting(self):
        return getattr(self, "waiting?")

    @property
    def waiting_msg(self):
        if self.is_waiting:
            return "waiting"
        return "not waiting"


class Maintenance(BaseResource):
    """ Heroku Postgresql maintenance. """

    _strs = ['message']

    def __repr__(self):
        return "<heroku_postgresql_maintenance: {0}>".format(self.message)

