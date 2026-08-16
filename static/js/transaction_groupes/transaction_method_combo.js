
$('#transactionmainheads').change(function(){

    let main_head_id = $(this).val();

    $.ajax({
        url: '/transaction_group/get-transaction-method-combo/',
        method: 'GET',
        data: {
            'main_head_id': main_head_id
        },
        success: function(response) {
            let transaction_method_combo = response.transaction_method_combo;
            let $select = $('#transaction_method');
            $select.empty(); // Clear existing options
            // $select.append('<option value="">-- Select Event --</option>');
            $.each(transaction_method_combo, function(index, e) {
                $select.append(`<option value="${e.method}">${e.method}</option>`);
            });

            // ✅ Automatically trigger table load for first even
            if (transaction_method_combo.length > 0) {
                const firstId = transaction_method_combo[0].id;
                $select.val(firstId).trigger('change');
            }
        },
        error: function() {
            alert("Failed to load transaction methods");
        }
    });
});
    
