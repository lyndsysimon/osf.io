import abc
import http

from framework.exceptions import HTTPError
from framework.exceptions import PermissionsError

from website.oauth.models import ExternalAccount

from website.util import api_url_for, web_url_for
from . import utils

class CitationsProvider(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, provider_name):

        self.provider_name = provider_name

    @abc.abstractmethod
    def _serialize_urls(self, node_addon):
        """Collects and serializes urls needed for AJAX calls"""

        external_account = node_addon.external_account
        ret = {
            'auth': api_url_for('oauth_connect',
                                service_name=self.provider_name),
            'settings': web_url_for('user_addons'),
        }
        if external_account and external_account.profile_url:
            ret['owner'] = external_account.profile_url

        return ret

    @abc.abstractmethod
    def _serialize_model(self, node_addon, user):

        return {}

    def serialize_settings(self, node_settings, current_user):
        """Serializes parameters for building UI for widget and settings pages
        """
        node_account = node_settings.external_account
        user_accounts = [account for account in current_user.external_accounts
                         if account.provider == 'mendeley']

        user_is_owner = node_account and node_account in user_accounts

        user_settings = current_user.get_addon('mendeley')
        user_has_auth = bool(user_settings and user_accounts)

        user_account_id = None
        if user_has_auth:
            user_account_id = user_accounts[0]._id

        result = {
            'nodeHasAuth': node_settings.has_auth,
            'userIsOwner': user_is_owner,
            'userHasAuth': user_has_auth,
            'urls': self._serialize_urls(node_settings),
            'userAccountId': user_account_id,
            'validCredentials': True
        }
        if node_account is not None:
            result['folder'] = node_settings.selected_folder_name
            result['ownerName'] = node_account.display_name

        result.update(self._serialize_model(node_settings, current_user))
        return result

    def user_accounts(self, user):
        """ Gets a list of the accounts authorized by 'user' """
        return {
            'accounts': [
                utils.serialize_account(each)
                for each in user.external_accounts
                if each.provider == self.provider_name
            ]
        }

    def set_config(self, node_addon, user, external_account_id, external_list_id):
        external_account = ExternalAccount.load(external_account_id)

        if external_account not in user.external_accounts:
            raise HTTPError(http.FORBIDDEN)

        return external_account

    def add_user_auth(self, node_addon, user, external_account_id):

        external_account = ExternalAccount.load(external_account_id)

        try:
            node_addon.set_auth(external_account, user)
        except PermissionsError:
            raise HTTPError(http.FORBIDDEN)

        result = self.serialize_settings(node_addon, user)
        return {'result': result}

    @abc.abstractmethod
    def remove_user_auth(self, node_addon, user):

        node_addon.clear_auth()
        result = self.serialize_settings(node_addon, user)
        return {'result': result}

    def widget(self, node_addon):

        ret = node_addon.config.to_json()
        ret.update({
            'complete': node_addon.complete,
        })
        return ret

    @abc.abstractmethod
    def citation_list(self, node_addon, user, list_id, show='all'):

        return {}