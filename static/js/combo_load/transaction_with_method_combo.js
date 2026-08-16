function loadTransactionWithMethodsCombo(selected_id = null, callback = null){

    let tran_main_head_id = $('#transactionmainheads').val();

    // alert(tran_main_head_id);

    $.ajax({
        url: '/combo_load/transaction-with-method-combo/',
        method: 'GET',
        data:{
            tran_main_head_id: tran_main_head_id
        },

        success: function(response){

            let transaction_with_method_combo = response.transaction_with_method_combo;
            let $select = $('#transaction_with_method');
            $select.empty(); // Clear existing options
            $select.append('<option value="">-- Select Please --</option>');
            $.each(transaction_with_method_combo, function(index, e) {
                $select.append(`<option value="${e.method}">${e.method}</option>`);
            });

            $select.val(selected_id);

            if(callback){
                callback();
            }
        },
        error: function() {
            alert("Failed to load transaction with methods");
        }
    });
}

$('#transactionmainheads').change(function(){

    loadTransactionWithMethodsCombo(0, function(){

    });

});

// $('#transaction_with').change(function(){

//     let tran_with_id = $(this).val();

//     // alert(tran_with_id);

//     $.ajax({
//         url: '/combo_load/transaction-with-method-combo/',
//         method: 'GET',
//         data: {
//             'tran_with_id': tran_with_id,
//         },
//         success: function(response) {
//             let transaction_with_method_combo = response.transaction_with_method_combo;
//             let $select = $('#transaction_with_method');
//             $select.empty(); // Clear existing options
//             // $select.append('<option value="">-- Select Event --</option>');
//             $.each(transaction_with_method_combo, function(index, e) {
//                 $select.append(`<option value="${e.method}">${e.method}</option>`);
//             });

//             // ✅ Automatically trigger table load for first even
//             if (transaction_with_method_combo.length > 0) {
//                 const firstId = transaction_with_method_combo[0].method;
//                 $select.val(firstId).trigger('change');
//             }
//         },
//         error: function() {
//             alert("Failed to load transaction with methods");
//         }
//     });
// });
    
