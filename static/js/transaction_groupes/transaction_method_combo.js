
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

            // Keep selection empty here; page-init or explicit user choice will set it.
            $select.val('');
        },
        error: function() {
            alert("Failed to load transaction methods");
        }
    });
});
    
