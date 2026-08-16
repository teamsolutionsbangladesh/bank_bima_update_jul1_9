
function loadTransactionMainHeadsCombo(selected_id = null, callback = null){

    $.ajax({
        url: '/transaction_main_heads/get-transaction-main-heads-combo/',
        method: 'GET',
        success: function(response){

            let transaction_main_heads_combo = response.transaction_main_heads_combo;
            // let $select = $('#transactionmainheads');
            let $select = $('#transactionmainheads, .transactionmainheads');

            $select.empty(); // Clear existing options

            $.each(transaction_main_heads_combo, function(index, e) {
                $select.append(`<option value="${e.id}">${e.name}</option>`);
            });

            $select.val(selected_id);

            if(callback){
                callback();
            }
        },
        error: function() {
            alert("Failed to load transaction main heads");
        }
    });
}


// function loadTransactionMainHeadsCombo(target_selector, selected_id = null, callback = null){
//     // alert("hello");

//     $.ajax({
//         url: '/combo_load/get-transaction-main-heads-combo/',
//         method: 'GET',
//         success: function(response){

//             let transaction_main_heads_combo = response.transaction_main_heads_combo;
//             // let $select = $('#transactionmainheads');
//             // let $select = $('.transactionmainheads');
//             let $select = $(target_selector); 

//             $select.empty(); // Clear existing options

//             $.each(transaction_main_heads_combo, function(index, e) {
//                 $select.append(`<option value="${e.id}">${e.name}</option>`);
//             });

//             $select.val(selected_id);

//             if(callback){
//                 callback();
//             }
//         },
//         error: function() {
//             alert("Failed to load transaction main heads");
//         }
//     });
// }


// $(document).ready(function () {

//     loadTransactionMainHeadsCombo('#transactionmainheads', 1, function(){
        
//     });
    
//     loadTransactionMainHeadsCombo('#filter_transactionmainheads', null, function(){

//     });

// });



// function loadTransactionMainHeadsCombo_() {
//     $.ajax({
//         url: '/transaction_main_heads/get-transaction-main-heads-combo/',
//         method: 'GET',
//         success: function(response) {
//             let transaction_main_heads_combo = response.transaction_main_heads_combo;
//             let $select = $('#transactionmainheads');
//             $select.empty(); // Clear existing options
//             // $select.append('<option value="">-- Select Event --</option>');
//             $.each(transaction_main_heads_combo, function(index, e) {
//                 $select.append(`<option value="${e.id}">${e.name}</option>`);
//             });

//             // ✅ Automatically trigger table load for first even
//             if (transaction_main_heads_combo.length > 0) {
//                 const firstId = transaction_main_heads_combo[0].id;
//                 $select.val(firstId).trigger('change');
//             }
//         },
//         error: function() {
//             alert("Failed to load transaction main heads");
//         }
//     });
// };