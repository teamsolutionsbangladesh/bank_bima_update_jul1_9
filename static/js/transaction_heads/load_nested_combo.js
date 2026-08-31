
function getInitData(){

    let $form = $('#addForm');
    let editId = $form.attr('data-edit-id');
    let editData = editId ? {
        id: editId,
        tran_main_head_id: $form.attr('data-main-head-id'),
        tran_method: $form.attr('data-method'),
        group_id: $form.attr('data-group-id'),
        category_id: $form.attr('data-category-id')
    } : null;

    if (editData) {
        loadTransactionMainHeadsCombo(editData.tran_main_head_id, function(){
            $('#transactionmainheads').val(String(editData.tran_main_head_id));
            loadTransactionMethodsCombo(editData.tran_method, function(){
                $('#transaction_method').val(String(editData.tran_method));
                loadTransactionGroupCombo(editData.group_id, function(){
                    $('#tran_group').val(String(editData.group_id));
                    loadTransactionCategoryCombo(editData.category_id, function(){
                        $('#transaction_category').val(String(editData.category_id));
                        $('#tran_head_id').val(editData.id);
                    });
                });
            });
        });
        return;
    }

            loadTransactionMainHeadsCombo(1, function(){
          $('#transactionmainheads').trigger('change');
            loadTransactionMethodsCombo(0, function(){
            $('#transaction_method').prop('selectedIndex', 0).trigger('change'); // First option
            loadTransactionGroupCombo(0, function(){
                $('#tran_group').prop('selectedIndex', 0).trigger('change'); // First option
                // loadTransactionWithUserCombo();
            });
        });
    });

}

$(document).ready(function () {

    getInitData();

});
