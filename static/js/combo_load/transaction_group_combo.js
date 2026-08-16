function loadTransactionGroupCombo(selected_id = null, callback = null){

    let tran_main_head_id = $('#transactionmainheads').val();
    let transaction_method = $('#transaction_method').val();    

    // alert(tran_main_head_id);

    $.ajax({
        url: '/combo_load/transaction-group-combo/',
        method: 'GET',
        data:{
            tran_main_head_id: tran_main_head_id,
            transaction_method: transaction_method,
        },
        success: function(response){
            let transaction_group_combo = response.transaction_group_combo;
            let $select = $('#tran_group');
            $select.empty(); // Clear existing options
            $select.append('<option value="">-- Select Please --</option>');
            $.each(transaction_group_combo, function(index, e) {
                $select.append(`<option value="${e.id}">${e.name}</option>`);
            });

            $select.val(selected_id);

            if(callback){
                callback();
            }
        },
        error: function() {
            alert("Failed to load transaction group");
        }
    });
}

$('#transaction_method').on('change click', function () {

    loadTransactionGroupCombo(0, function(){
        $('#tran_group').prop('selectedIndex', 0); // First option
    
    });

});

$('#tran_group').on('change click', function () {

    // alert("hello");

    loadProducts();

});