$(document).ready(function () {

    $('#saveBtn').click(function(e){
        e.preventDefault();

        let tran_main_head_id = $('#transactionmainheads').val();
        let tran_with_method = $('#transaction_with_method').val();
        let tran_with = $('#transaction_with').val();
        let tran_user = $('#tran_user').val();

        // console.log(tran_main_head_id);
        // alert(tran_main_head_id);

        $.ajax({
            url: '/administrator/save-transaction-with-user/',
            method: 'POST',
            headers: {
                "X-CSRFToken": csrftoken
            },             
            data: {
                'tran_main_head_id': tran_main_head_id,
                'tran_with_method': tran_with_method,
                'tran_with': tran_with,
                'tran_user': tran_user,
            },           
            success: function(response) {
                $('#transactionmainheads').trigger('change');
                $('#tran_user').val('');
                alert("Save successfull");

            },
            error: function() {
                alert("Failed to save data.");
            }
        });
    });
});