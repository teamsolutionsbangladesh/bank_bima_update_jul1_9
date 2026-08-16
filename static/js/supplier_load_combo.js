function loadSupplierCombo() {
    $.ajax({
        // url: '/pharmacy/get-divisions-combo/',
        // url: "{% url 'get_divisions_combo' %}",
        // url: "{% url 'get_supplier_combo' %}",
        url: window.APP_URLS.SUPPLIER_COMBO_URL,
        method: 'GET',
        dataType: 'json',
        success: function(response) {

            console.log("Supplier response:", response);

            let supplier = response.supplier_combo || [];
            // let $select = $('#supplier');
            let $select = $('.supplier-select');

            $select.empty(); // Clear existing options

            // ✅ Default option
            $select.append('<option value="">-- Select Supplier --</option>');

            if (supplier.length === 0) {
                $select.append('<option value="">No Supplier Found</option>');
                return;
            }

            $.each(supplier, function(index, d) {
                $select.append(
                    `<option value="${d.id}">${d.manufacturer_name}</option>`
                );
            });

            // ✅ Auto-select first subjects and trigger change
            $select.val(supplier[0].id).trigger('change');

        },
        error: function(xhr) {
            console.error(xhr.responseText);
            alert("Failed to load supplier");
        }
    });
};
    
$(document).ready(function () {
    loadSupplierCombo();
});