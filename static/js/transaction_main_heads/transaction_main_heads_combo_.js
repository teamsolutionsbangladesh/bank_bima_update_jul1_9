function loadTransactionMainHeadsCombo() {
    $.ajax({
        url: '/transaction_main_heads/get-transaction-main-heads-combo/',
        method: 'GET',
        success: function(response) {
            let transaction_main_heads_combo = response.transaction_main_heads_combo;
            let $select = $('#transactionmainheads');
            $select.empty(); // Clear existing options
            // $select.append('<option value="">-- Select Event --</option>');
            $.each(transaction_main_heads_combo, function(index, e) {
                $select.append(`<option value="${e.id}">${e.name}</option>`);
            });

            // ✅ Automatically trigger table load for first even
            if (transaction_main_heads_combo.length > 0) {
                const firstId = transaction_main_heads_combo[0].id;
                $select.val(firstId).trigger('change');
            }
        },
        error: function() {
            alert("Failed to load transaction main heads");
        }
    });
};
    
function get_page_main_head_id() {

    let page_main_head_id = "1020300001";
    alert(page_main_head_id);

    $.ajax({
        url: '/transaction_main_heads/set-transaction-main-head-id/',
        method: 'GET',
        // headers: {
        //     "X-CSRFToken": csrftoken
        // },             
        data: {
            'page_main_head_id': page_main_head_id,

        },           
        success: function(response) {

            let get_transaction_main_head_id = response.get_transaction_main_head_id;

            let main_head_id = get_transaction_main_head_id[0].tran_main_head_id;

            global_tran_with_id = get_transaction_main_head_id[0].user_tran_with_id;

            let tran_group_id = get_transaction_main_head_id[0].tran_group_id;

            $('#transactionmainheads').val(main_head_id).trigger('change');
            
        },
        error: function() {
            alert("Failed to save data.");
        }
    });

}

$(document).ready(function () {
    let global_tran_with_id = "";
    loadTransactionMainHeadsCombo();
    get_page_main_head_id();


});