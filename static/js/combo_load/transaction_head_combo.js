function loadTransactionHeadCombo(selected_id = null, callback = null) {
    let tran_main_head_id = $('#transactionmainheads').val();
    let tran_group_id = $('#tran_group').val();
    let category_id = $('#transaction_category').val();
    let $select = $('#transaction_head');

    $select.empty().append('<option value="">All Transaction Heads</option>');

    if (!tran_main_head_id) {
        if (callback) callback();
        return;
    }

    $.ajax({
        url: '/combo_load/transaction-head-combo/',
        method: 'GET',
        data: {
            tran_main_head_id: tran_main_head_id,
            tran_group_id: tran_group_id,
            category_id: category_id
        },
        success: function (response) {
            $.each(response.transaction_head_combo || [], function (index, item) {
                $select.append(`<option value="${item.id}">${item.name}</option>`);
            });

            $select.val(selected_id || '');
            if (callback) callback();
        },
        error: function () {
            alert('Failed to load transaction heads');
        }
    });
}

$(document).on('change', '#transaction_category', function () {
    loadTransactionHeadCombo();
});
