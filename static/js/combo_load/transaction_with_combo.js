function loadTransactionWithCombo(selected_id = null, callback = null){

    let tran_main_head_id = $('#transactionmainheads').val();
    let tran_with_method = $('#transaction_with_method').val();

    // alert(tran_main_head_id);
    // alert(tran_with_method);

    $.ajax({
        url: '/combo_load/transaction-with-combo/',
        method: 'GET',
        data:{
            tran_main_head_id: tran_main_head_id,
            tran_with_method: tran_with_method
        },

        success: function(response){

            let transaction_with_combo = response.transaction_with_combo;
            let $select = $('#transaction_with');
            $select.empty(); // Clear existing options
            $select.append('<option value="">-- Select Please --</option>');
            $.each(transaction_with_combo, function(index, e) {
                $select.append(`<option value="${e.id}">${e.name}</option>`);
            });

            $select.val(selected_id);

            if(callback){
                callback();
            }
        },
        error: function() {
            alert("Failed to load transaction methods");
        }
    });
}


$('#transaction_with_method').change(function(){

    loadTransactionWithCombo(0, function(){

    });

});

