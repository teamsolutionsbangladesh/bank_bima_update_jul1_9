function loadUserRoleCombo(selected_id = null, callback = null){

    // let tran_main_head_id = $('#transactionmainheads').val();
    // let tran_with_method = $('#transaction_with_method').val();

    // alert(tran_main_head_id);
    // alert(tran_with_method);

    $.ajax({
        url: '/combo_load/user-role-combo/',
        method: 'GET',
        // data:{
        //     tran_main_head_id: tran_main_head_id,
        //     tran_with_method: tran_with_method
        // },

        success: function(response){

            let user_role_combo = response.user_role_combo;
            let $select = $('#user_role');
            $select.empty(); // Clear existing options
            // $select.append('<option value="">-- Select Event --</option>');
            $.each(user_role_combo, function(index, e) {
                $select.append(`<option value="${e.id}">${e.name}</option>`);
            });

            $select.val(selected_id);

            if(callback){
                callback();
            }
        },
        error: function() {
            alert("Failed to load user role");
        }
    });
}


// $('#user_role').change(function(){
$(document).ready(function () {

    loadUserRoleCombo(0, function(){

    });

});

