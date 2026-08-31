function loadTransactionGroupComboOnMainHead(selected_id = null, callback = null){

    let tran_main_head_id = $('#transactionmainheads').val();

    if (!tran_main_head_id) {
        $('#tran_group').empty().append('<option value="">Select Group</option>');
        if (callback) callback();
        return;
    }

    alert(tran_main_head_id);

    $.ajax({
        url: '/combo_load/transaction-group-combo-on-main-head/',
        method: 'GET',
        data:{
            tran_main_head_id: tran_main_head_id,
            
        },
        success: function(response){
            let transaction_group_combo_on_main_head = response.transaction_group_combo_on_main_head;
            let $select = $('#tran_group');
            $select.empty(); // Clear existing options
            $select.append('<option value="">-- Select Please --</option>');
            $.each(transaction_group_combo_on_main_head, function(index, e) {
                $select.append(`<option value="${e.id}">${e.name}</option>`);
            });

            $select.val(selected_id);

            if(callback){
                callback();
            }
        },
        error: function(xhr) {
            console.error("Failed to load transaction groups:", xhr.responseText);
            alert("Failed to load transaction groups");
        }
    });
}

// $('#transaction_method').on('change click', function () {

//     loadTransactionGroupCombo(0, function(){
//         $('#tran_group').prop('selectedIndex', 0); // First option
    
//     });

// });

// $('#tran_group').on('change click', function () {

//     // alert("hello");

//     loadProducts();

// });
