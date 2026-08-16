
function getInitData(){

    // $('#transactionmainheads').on('change click', function () {

    //     loadTransactionMethodsCombo(0, function(){
    //         $('#transaction_method').prop('selectedIndex', 0); // First option

    //         $('#transaction_method').on('change click', function () {

    //             loadTransactionGroupCombo(0, function(){
    //                 $('#tran_group').prop('selectedIndex', 0); // First option
                
    //             });

    //         });            
        
    //     });

    // });

    loadTransactionMainHeadsCombo(1, function(){
        $('#transactionmainheads').prop('selectedIndex', 0); // First option
        loadTransactionMethodsCombo(0, function(){
            $('#transaction_method').prop('selectedIndex', 0).trigger('change'); // First option
            loadTransactionGroupCombo(0, function(){
                $('#tran_group').prop('selectedIndex', 0); // First option
                // loadTransactionWithUserCombo();
            });
        });
    });

}

$(document).ready(function () {

    getInitData();

});
