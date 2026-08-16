
function pageInitGenerateID(){

    console.log(typeof loadTransactionMainHeadsCombo);

    loadTransactionMainHeadsCombo(1, function(){
        // alert("Loading of tran MAIN HEAD. done");
        loadTransactionMethodsCombo(0, function(){
            loadTransactionGroupCombo(0, function(){
                // alert("Loading of tran GROUP. done");
                // loadProducts();
            });
        });

        loadTransactionWithMethodsCombo(0, function(){
            // alert("Loading of tran METHOD. done");
            loadTransactionWithCombo(0, function(){
                // alert("Loading of tran TRAN WITH. done");
                // loadTransactionWithUserCombo();
            });
        });
    });
    
}

$(document).ready(function () {

    pageInitGenerateID();


});