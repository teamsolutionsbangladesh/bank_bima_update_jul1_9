function loadTransactionMethodsCombo(selected_id = null, callback = null){

    let tran_main_head_id = $('#transactionmainheads').val();

    // alert(tran_main_head_id);

    $.ajax({
        url: '/combo_load/transaction-method-combo/',
        method: 'GET',
        data:{
            tran_main_head_id: tran_main_head_id
        },

        success: function(response){

            let transaction_method_combo = response.transaction_method_combo;
            let $select = $('#transaction_method');
            $select.empty(); // Clear existing options
            $select.append('<option value="">-- Select Please --</option>');
            $.each(transaction_method_combo, function(index, e) {
                $select.append(`<option value="${e.method}">${e.method}</option>`);
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

$('#transactionmainheads').on('change click', function () {

    loadTransactionMethodsCombo(0, function(){
        $('#transaction_method').prop('selectedIndex', 0); // First option
    
    });

});

