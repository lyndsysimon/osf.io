var AddonHelper = (function() {

    /**
     * Convert an HTML form to a JS object.
     *
     * @param {jQuery} form
     * @return {Object} The parsed data
     */
    function formToObj(form) {
        var rv = {};
        $.each($(form).serializeArray(), function(_, value) {
            rv[value.name] = value.value;
        });
        return rv;
    }

    /**
     * Submit add-on settings.
     */
    function onSubmitSettings() {
        console.log('hereiam');
        var $this = $(this);
        var addon = $this.attr('data-addon');
        var owner = $this.find('span[data-owner]').attr('data-owner');
        var msgElm = $this.find('.addon-settings-message');

        var url = owner == 'user'
            ? '/api/v1/settings/' + addon + '/'
            : nodeApiUrl + addon + '/settings/';

        $.ajax({
            url: url,
            data: JSON.stringify(formToObj($this)),
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json'
        }).success(function() {
            msgElm.text('Settings updated')
                .removeClass('text-danger').addClass('text-success')
                .fadeOut(100).fadeIn();
        }).fail(function(xhr) {
            var message = 'Error: ';
            var response = JSON.parse(xhr.responseText);
            if (response && response.message) {
                message += response.message;
            } else {
                message += 'Settings not updated.'
            }
            msgElm.text(message)
                .removeClass('text-success').addClass('text-danger')
                .fadeOut(100).fadeIn();
        });

        return false;

    }

    // Expose public methods
    return {
        formToObj: formToObj,
        onSubmitSettings: onSubmitSettings,
    }

})();
