
function pageInitGenerateID(){

    console.log(typeof loadTransactionMainHeadsCombo);

    loadTransactionMainHeadsCombo(null, function(){
        // Keep the create form empty until the user selects a main head.
        // That prevents stale defaults like Receive / blank group from being saved
        // into page_init for pages such as Office Bazar.
    });
    
}

$(document).ready(function () {

    pageInitGenerateID();


});
