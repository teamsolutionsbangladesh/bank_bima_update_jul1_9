
function loadTransactionWithUserCombo(selected_id = null, callback = null){ // codex change

    let tran_main_head_id = $('#transactionmainheads').val();
    let tran_with_id = $('#transaction_with').val();

    // alert(tran_main_head_id);
    // alert(tran_with_id);

    $.ajax({
        url: '/combo_load/transaction-with-user-combo/',
        method: 'GET',
        data:{
            tran_main_head_id: tran_main_head_id,
            tran_with_id: tran_with_id
        },

        success: function(response){

            let transaction_with_user_combo = response.transaction_with_user_combo;
            let $select = $('#transaction_with_user');
            $select.empty(); // Clear existing options
            $select.append('<option value="">Select User</option>');
            $.each(transaction_with_user_combo, function(index, e) {
                $select.append(`<option value="${e.id}">${e.user_name}</option>`);
            });

            if (selected_id) $select.val(String(selected_id)); // codex change

            if(callback){ // codex change
                callback(); // codex change
            } // codex change
        },
        error: function() {
            alert("Failed to load transaction with user");
        }
    });
}

$('#transaction_with').change(function(){

    loadTransactionWithUserCombo(0, function(){

    });

});

// $('#transaction_with').change(function(){

//     let main_head_id = $('#transactionmainheads').val();
//     let method = $('#transaction_with_method').val();
//     // let tran_with_user = $(this).val();
//     let tran_with_id = $('#transaction_with').val();

//     // alert(main_head_id);
//     // alert(tran_with_id);

//     $.ajax({
//         url: '/combo_load/transaction-with-user-combo/',
//         method: 'GET',
//         data: {
//             'main_head_id': main_head_id,
//             'method': method,
//             'tran_with_id': tran_with_id,
//         },
//         success: function(response) {
//             let transaction_with_user_combo = response.transaction_with_user_combo;
//             let $select = $('#transaction_with_user');
//             $select.empty(); // Clear existing options
//             // $select.append('<option value="">-- Select Event --</option>');
//             $.each(transaction_with_user_combo, function(index, e) {
//                 $select.append(`<option value="${e.id}">${e.user_name}</option>`);
//             });

//             // ✅ Automatically trigger table load for first even
//             if (transaction_with_user_combo.length > 0) {
//                 const firstId = transaction_with_user_combo[0].id;
//                 $select.val(firstId).trigger('change');
//             }
//         },
//         error: function() {
//             alert("Failed to load transaction with user");
//         }
//     });
// });
