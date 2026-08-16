function loadStoreCombo() {
    let $select = $('.store-select');

    if ($select.length === 0) {
        console.warn("No .store-select found on this page");
        return;  // Stop if not present
    }

    $.ajax({
        url: '/pharmacy/get-store-combo/',
        // url: "{% url 'get_supplier_combo' %}",
        // url: window.APP_URLS.STORE_COMBO_URL,
        method: 'GET',
        dataType: 'json',
        success: function(response) {

            console.log("Store response:", response);

            let store = response.store_combo || [];
            // let $select = $('#store');
            // let $select = $('.store-select');

            $select.empty(); // Clear existing options

            // ✅ Default option
            $select.append('<option value="">-- Select Store --</option>');

            if (store.length === 0) {
                $select.append('<option value="">No Store Found</option>');
                return;
            }

            $.each(store, function(index, d) {
                $select.append(
                    `<option value="${d.id}">${d.store_name}</option>`
                );
            });

            // ✅ Auto-select first subjects and trigger change
            $select.val(store[0].id).trigger('change');

        },
        error: function(xhr) {
            console.error(xhr.responseText);
            alert("Failed to load store");
        }
    });
};
    
$(document).ready(function () {

    // Delay slightly to ensure DOM is fully ready
    setTimeout(function () {
        loadStoreCombo();
    }, 200);

});