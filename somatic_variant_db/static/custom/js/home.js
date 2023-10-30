// get variable from data-attribute in script tag. Must be before document.ready
const data = document.currentScript.dataset;
const ajax_search_url = data.ajaxSearchUrl;
const temp_sample_url = data.tempSampleUrl;
const num_assigned_url = data.numAssignedUrl;
const num_pending_url = data.numPendingUrl;

$(document).ready(function(){

    // handler for the search box
    $('#ws_search').autocomplete({
        source: ajax_search_url,
        minLength: 4,
        delay: 750,
        // select what is displayed as you hover over ech option (raw worksheet ID)
        focus: function( event, ui ) {
            $( "#ws_search" ).val( ui.item.ws );
            return false;
        },
        // set value that is saved from dropdown - just the worksheet ID
        select: function( event, ui ) {
            $( "#ws_search" ).val( ui.item.ws );
            // redirect to the worksheet when selected from the dropdown
            // temp is added so that the URL is made on page load, then replaced with the correct variable by the javascript
            window.location.href = temp_sample_url.replace('temp', ui.item.ws);
            return false;
        },
    })
    // reformat the list options
    .autocomplete('instance')._renderItem = function(ul, item) {
        if (item.sample === null) {
            record = '<div>Worksheet ' + '<b>' + item.ws + '</b></div>';;
        } else {
            record = '<div>Worksheet ' + '<b>' + item.ws + '</b><br>&nbsp&nbsp- contains sample <b>' + item.sample + '</b></div>';
        }
        return $('<li>') 
        .append(record)
        .appendTo(ul);
    };


    // AJAX for number of checks assigned to current user
    $.ajax({
        url: num_assigned_url,
        type: 'GET',
        success: function(data) {
            setTimeout(function() {
                // set number of checks value and CSS
                num_checks_span = document.getElementById('num_assigned_text')
                num_checks_span.innerHTML = '<b>' + data.num_checks + '</b>';
                num_checks_span.classList.remove('badge-warning');
                num_checks_span.classList.add('badge-' + data.css_class);

                // set background colour of the box
                num_checks_alert = document.getElementById('num_assigned_alert');
                num_checks_alert.classList.remove('alert-warning');
                num_checks_alert.classList.add('alert-' + data.css_class);
            }, 500)
        },
        failure: function(data) {
            alert('Got an error');
        }
    });

    // AJAX for number of non-complete worksheets - seperate call as this is likely to take longer
    $.ajax({
        url: num_pending_url,
        type: 'GET',
        success: function(data) {
            setTimeout(function() {
                // set number of checks value and CSS
                num_checks_span = document.getElementById('num_pending_text')
                num_checks_span.innerHTML = '<b>' + data.num_pending + '</b>';
                num_checks_span.classList.remove('badge-warning');
                num_checks_span.classList.add('badge-' + data.css_class);

                // set background colour of the box
                num_checks_alert = document.getElementById('num_pending_alert');
                num_checks_alert.classList.remove('alert-warning');
                num_checks_alert.classList.add('alert-' + data.css_class);
            }, 500)
        },
        failure: function(data) {
            alert('Got an error');
        }
    });

});