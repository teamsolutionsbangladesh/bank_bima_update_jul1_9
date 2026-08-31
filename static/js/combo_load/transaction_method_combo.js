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
            if (!$select.val() && selected_id !== null && selected_id !== undefined && String(selected_id).trim() !== "") {
                const wanted = String(selected_id).trim().toLowerCase();
                $select.find('option').each(function () {
                    const optionValue = String($(this).val() || '').trim().toLowerCase();
                    const optionText = String($(this).text() || '').trim().toLowerCase();
                    if (optionValue === wanted || optionText === wanted) {
                        $select.val($(this).val());
                        return false;
                    }
                });
            }

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

    if (window.__PAGE_INIT_LOADING) {
        return;
    }

    loadTransactionMethodsCombo(null, function(){
        $('#transaction_method').val('').trigger('change');
    });

});

