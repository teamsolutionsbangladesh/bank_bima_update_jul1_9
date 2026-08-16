
// let page_id = "1020300001";
let urlParams = new URLSearchParams(window.location.search);

let page_id = urlParams.get('page_id');

if (window.EDIT_PAYMENT_DATA && window.EDIT_PAYMENT_DATA.is_edit) {
    page_id = null;
}

function getInitData(){

    if (!page_id) {
        return;
    }

    // alert("PAGE ID: " + page_id);

    $.ajax({
        url: "/general/get-page-init-add-payment/",
        method: "GET",
        data: {
            page_id: page_id,
        },
        success: function(res){
            if (!res.get_page_init_data || !res.get_page_init_data.length) {
                return;
            }

            let row = res.get_page_init_data[0];

            let tran_main_head_id = row.tran_main_head_id;
            let user_tran_method = row.user_tran_method;
            let user_tran_with_id = row.user_tran_with_id;
            let tran_method = row.tran_method;
            let tran_group_id = row.tran_group_id;

            loadTransactionMainHeadsCombo(tran_main_head_id, function(){
                // alert("Loading of tran MAIN HEAD. done");
                // loadTransactionGroupCombo(tran_group_id);
                loadTransactionMethodsCombo(tran_method, function(){
                    loadTransactionGroupCombo(tran_group_id, function(){
                        // alert("Loading of tran GROUP. done");
                        loadProducts();
                    });
                });
                loadTransactionWithMethodsCombo(user_tran_method, function(){
                    // alert("Loading of tran METHOD. done");
                    loadTransactionWithCombo(user_tran_with_id, function(){
                        // alert("Loading of tran TRAN WITH. done");
                        loadTransactionWithUserCombo();
                    });
                });
            });
            
        }
    });

}

$(document).ready(function () {

    getInitData();


});
