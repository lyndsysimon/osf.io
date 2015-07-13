<%inherit file="project/project_base.mako"/>
<%def name="title()">Edit ${node['title']} registration</%def>

<div id="draftRegistrationScope"> 
  <div class="row">
    <h3>Edit draft registration</h3>
    <span class="btn-group">
      <a data-bind="click: submit" id="submitForReview" class="btn btn-default" type="button">
        <i class="fa fa-save"></i> Submit for review
      </a>
    </span>
    <div class="col-md-12">
      <%include file="project/registration_editor.mako"/>
    </div>
  </div>
</div>

<%def name="javascript_bottom()">
${parent.javascript_bottom()}
<script>
  <% import json %>
  window.contextVars = $.extend(true, {}, window.contextVars, {
  draft: ${json.dumps(draft)},
  
  });
</script>
<script src=${"/static/public/js/registration-edit-page.js" | webpack_asset}> </script>
</%def>