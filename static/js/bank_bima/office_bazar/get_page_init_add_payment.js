
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

    window.__PAGE_INIT_LOADING = true;

    // alert("PAGE ID: " + page_id);

    $.ajax({
        url: "/bank-bima/office-bazar/get-page-init-add-payment/",
        method: "GET",
        data: {
            page_id: page_id,
        },
        success: function(res){
            if (!res.get_page_init_data || !res.get_page_init_data.length) {
                window.__PAGE_INIT_LOADING = false;
                return;
            }

            let row = res.get_page_init_data[0];

            const tran_main_head_id = row.tran_main_head_id;
            const user_tran_method = row.user_tran_method;
            const user_tran_with_id = row.user_tran_with_id;
            const tran_method = row.tran_method;
            const tran_group_id = row.tran_group_id;

            function setIfExists(selector, value) {
                const $select = $(selector);
                if ($select.length && value !== null && value !== undefined && value !== "") {
                    $select.val(String(value));
                }
            }

            loadTransactionMainHeadsCombo(tran_main_head_id, function () {
                setIfExists('#transactionmainheads', tran_main_head_id);

                loadTransactionMethodsCombo(tran_method, function () {
                    setIfExists('#transaction_method', tran_method);

                    loadTransactionGroupCombo(tran_group_id, function () {
                        setIfExists('#tran_group', tran_group_id);

                        loadTransactionWithMethodsCombo(user_tran_method, function () {
                            setIfExists('#transaction_with_method', user_tran_method);

                            loadTransactionWithCombo(user_tran_with_id, function () {
                                setIfExists('#transaction_with', user_tran_with_id);

                                loadTransactionWithUserCombo("", function () {
                                    $('#transaction_with_user').val('');
                                    window.__PAGE_INIT_LOADING = false;
                                    if (typeof loadProducts === 'function') {
                                        loadProducts();
                                    }
                                });
                            });
                        });
                    });
                });
            });
            
        }
    });

}

$(document).ready(function () {

    getInitData();


});
