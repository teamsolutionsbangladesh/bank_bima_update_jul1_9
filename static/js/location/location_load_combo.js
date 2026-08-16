function loadDivisionsCombo() {
    let $select = $('.location-select'); // #codex
    let fixedLocationId = ($select.first().data('fixed-location-id') || '').toString(); // #codex
    let fixedLocationName = ($select.first().data('fixed-location-name') || '').toString(); // #codex
    let editTransaction = (window.EDIT_PAYMENT_DATA && window.EDIT_PAYMENT_DATA.transaction) || {}; // codex change
    fixedLocationId = fixedLocationId || (editTransaction.loc_id || '').toString(); // codex change
    fixedLocationName = fixedLocationName || (editTransaction.location_name || '').toString(); // codex change
    if (fixedLocationId) { // #codex
        $select.empty().append(`<option value="${fixedLocationId}" selected>${fixedLocationName || fixedLocationId}</option>`); // #codex
        $select.val(fixedLocationId).prop('disabled', true).trigger('change'); // #codex
        return; // #codex
    } // #codex
    $.ajax({
        // url: '/pharmacy/get-divisions-combo/',
        // url: "{% url 'get_divisions_combo' %}",
        // url: DIVISION_COMBO_URL,
        url: window.APP_URLS.DIVISION_COMBO_URL,
        method: 'GET',
        dataType: 'json',
        success: function(response) {

            console.log("Division response:", response);

            let divisions = response.divisions_combo || [];
            // let $select = $('#location');

            $select.empty(); // Clear existing options

            // ✅ Default option
            $select.append('<option value="">-- Select Location --</option>');

            if (divisions.length === 0) {
                $select.append('<option value="">No Divisions Found</option>');
                return;
            }

            $.each(divisions, function(index, d) {
                $select.append(
                    `<option value="${d.id}">${d.division}</option>`
                );
            });

            // ✅ Auto-select first subjects and trigger change
            $select.val(divisions[0].id).trigger('change');

        },
        error: function(xhr) {
            console.error(xhr.responseText);
            alert("Failed to load divisions");
        }
    });
};
    
$(document).ready(function () {
    loadDivisionsCombo();
});
