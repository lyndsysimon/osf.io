'use strict';
let ko = require('knockout');
let $ = require('jquery');
var Raven = require('raven-js');
var bootbox = require('bootbox');

class ConnectedProject {
    constructor(data) {
        this.title = data.title;
        this.id = data.id;
        this.urls = data.urls;
    }
}

class ExternalAccount {
    constructor(data) {
        this.name = data.display_name;
        this.id = data.id;
        this.connectedNodes = ko.observableArray();

        data.nodes.map(node => {
            this.connectedNodes.push(new ConnectedProject(node));
        });
    }

    deauthorizeNode(node) {
        let self = this;
        let url = node.urls.deauthorize;
        $.ajax({
            url: url,
            type: 'DELETE'
        }).done(data => {
            self.connectedNodes.remove(node);
        }).fail((xhr, status, error) => {
            Raven.captureMessage('Error deauthorizing node: ' + node.id, {
                url: url, status: status, error: error
            });
        });
    }
}

class OAuthAddonSettingsViewModel {
    constructor(name, displayName) {
        this.name = name;
        this.properName = displayName;
        this.accounts = ko.observableArray();
        this.message = ko.observable('');
        this.messageClass = ko.observable('');

        this.updateAccounts();
    }


    setMessage(msg, cls) {
        this.message(msg);
        this.messageClass(cls || '');
    }

    connectAccount() {
        let self = this;
        window.oauthComplete = () => {
            self.updateAccounts();
            self.setMessage('Add-on successfully authorized. To link this add-on to an OSF project, go to the settings page of the project, enable ' + self.properName + ', and choose content to connect.', '.text-success');
        };
        window.open('/oauth/connect/' + self.name + '/');
    }

    askDisconnect(account) {
        var self = this;
        bootbox.confirm({
            title: 'Delete account?',
            message: '<p class="overflow">' +
                'Are you sure you want to delete account <strong>' +
                account.name + '</strong>?' +
                '</p>',
            callback: (confirm) => {
                if (confirm) {
                    self.disconnectAccount(account);
                }
            }
        });
    }

    disconnectAccount(account) {
        var self = this;
        var url = '/api/v1/oauth/accounts/' + account.id + '/';
        $.ajax({
            url: url,
            type: 'DELETE'
        }).done((data) => {
            self.updateAccounts();
        }).fail((xhr, status, error) => {
            Raven.captureMessage('Error while removing addon authorization for ' + account.id, {
                url: url, status: status, error: error
            });
        });
    }

    updateAccounts() {
        var url = '/api/v1/settings/' + this.name + '/accounts/';
        let self=this;
        $.get(url).done(function(data) {
            self.accounts(data.accounts.map(function(account) {
                return new ExternalAccount(account);
            }));
        }).fail(function(xhr, status, error) {
            Raven.captureMessage('Error while updating addon account', {
                url: url, status: status, error: error
            });
        });
    }
}

$('.addon-oauth').get().map((elem) => {
    ko.applyBindings(
        new OAuthAddonSettingsViewModel(
            $(elem).data('addon-short-name'),
            $(elem).data('addon-name')
        ), elem
    );
});