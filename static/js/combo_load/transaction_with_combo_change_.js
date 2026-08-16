
$('#transactionmainheads').change(function(){

    let main_head_id = $(this).val();
        
    $.ajax({
        url: '/combo_load/transaction-with-combo/',
        method: 'GET',
        data: {
            'main_head_id': main_head_id,
        },
        success: function(response) {
            let transaction_with_combo = response.transaction_with_combo;
            let $select = $('#transaction_with');
            $select.empty(); // Clear existing options
            // $select.append('<option value="">-- Select Event --</option>');
            $.each(transaction_with_combo, function(index, e) {
                $select.append(`<option value="${e.id}">${e.name}</option>`);
            });

            // ✅ Automatically trigger table load for first even
            if (transaction_with_combo.length > 0) {
                const firstId = transaction_with_combo[0].id;
                $select.val(firstId).trigger('change');
            }

            $('#transaction_with').val(global_tran_with_id).trigger('change');

        },
        error: function() {
            alert("Failed to load transaction with");
        }
    });
});
    
