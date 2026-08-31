
$('#transaction_method').change(function(){

    let main_head_id = $('#transactionmainheads').val();

    let method = $(this).val();

    $.ajax({
        url: '/transaction_group/get-transaction-groups-combo/',
        method: 'GET',
        data: {
            'main_head_id': main_head_id,
            'method': method
        },
        success: function(response) {
            let transaction_groups_combo = response.transaction_groups_combo;
            let $select = $('#transactiongroups');
            $select.empty(); // Clear existing options
            // $select.append('<option value="">-- Select Event --</option>');
            $.each(transaction_groups_combo, function(index, e) {
                $select.append(`<option value="${e.id}">${e.name}</option>`);
            });

            // Keep selection empty here; page-init or explicit user choice will set it.
            $select.val('');
        },
        error: function() {
            alert("Failed to load transaction groups!!");
        }
    });
});
    
