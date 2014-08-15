from . import BaseResource
import re


pat_dump = re.compile(r'\.dump$')


class Transfer(BaseResource):
    """Heroku Pgbackups Transfer."""

    _strs = ['id', 'from_name', 'from_url', 'to_name', 'to_url', 'type', 'size', 'progress', 'user']
    _pks = ['id']
    _ints = ['user_id']
    _floats = ['duration']
    _dates = ['cleaned_at', 'created_at', 'destroyed_at', 'error_at', 'finished_at', 'started_at', 'updated_at']
    _bools = ['expire']

    def __repr__(self):
        return "<pgtransfer '{0}:{1}-->{2} - {3}'>".format(self.id, self.from_name, self.to_name, self.created_at)

    @property
    def name(self):
        # translate s3://bucket/foo/bar.dump -> bar
        parts = self.to_url.split('/')
        return re.sub(pat_dump, '', parts[-1])


class Backup(Transfer):
    """Heroku Pgbackups Backup."""

    _strs = ['id', 'from_name', 'from_url', 'to_name', 'to_url', 'public_url', 'type', 'size', 'progress', 'user']

    def __repr__(self):
        return "<pgbackup '{0}:{1} - {2}'>".format(self.id, self.from_name, self.created_at)
