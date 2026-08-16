
function getInitData(){

    loadTransactionMainHeadsCombo(1, function(){
        // alert("Loading of tran MAIN HEAD. done");
        // loadTransactionGroupCombo(tran_group_id);
        // loadTransactionGroupCombo(tran_group_id, function(){
        //     // alert("Loading of tran GROUP. done");
        //     loadProducts();
        // });
        loadTransactionWithMethodsCombo('Receive', function(){
            // alert("Loading of tran METHOD. done");
            loadTransactionWithCombo(0, function(){
                // alert("Loading of tran TRAN WITH. done");
                // loadTransactionWithUserCombo();
            });
        });
    });

}

$(document).ready(function () {

    getInitData();


});