from . import BaseResource
import re

url_pattern = re.compile(r'_URL\Z')

class Attachment(BaseResource):
    """Heroku Attachment, such as a postgres db attached to an app."""

    _strs = ['name', 'config_var']
    _dicts = ['resource']
    _bools = ['implicit']

    def post_process_item(self):
        # called from api process item(s)
        self.addon, self.plan = self.resource.get("type").split(":")

    def __repr__(self):
        return "<attachment '{0}'>".format(self.name)

    @property
    def resource_name(self):
        return self.resource.get("name") or re.sub(url_pattern, '', self.config_var)

    @property
    def is_starter_plan(self):
        return "dev" in self.plan or "basic" in self.plan

    @property
    def url(self):
        return self.resource.get("value")