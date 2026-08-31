$(document).ready(function () {

    $('#saveBtn').click(function(e){
        e.preventDefault();

        let tran_main_head_id = $('#transactionmainheads').val();
        let tran_method = $('#transaction_method').val();
        let tran_group_id = $('#transactiongroups').val();
        let tran_head = $('#tran_head').val();

        // console.log(tran_main_head_id);
        // alert(tran_main_head_id);

        $.ajax({
            url: '/transaction-heads/save-transaction-heads/',
            method: 'POST',
            headers: {
                "X-CSRFToken": csrftoken
            },             
            data: {
                'tran_main_head_id': tran_main_head_id,
                'tran_method': tran_method,
                'tran_group_id': tran_group_id,
                'tran_head': tran_head,
            },           
            success: function(response) {
                $('#transactionmainheads').trigger('change');
                $('#tran_head').val('');
                alert("Save successfull");

            },
            error: function() {
                alert("Failed to save data.");
            }
        });
    });
});