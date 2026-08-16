

function loadComboData(target_selector, selected_id = null, callback = null){
    // alert("hello");

    $.ajax({
        url: '/combo_load/fetch-combo-data/',
        method: 'GET',
        success: function(response){

            let fetchdata = response.fetchdata;
            // let $select = $('#transactionmainheads');
            // let $select = $('.transactionmainheads');
            let $select = $(target_selector); 

            $select.empty(); // Clear existing options

            $.each(fetchdata, function(index, e) {
                $select.append(`<option value="${e.id}">${e.name}</option>`);
            });

            $select.val(selected_id);

            if(callback){
                callback();
            }
        },
        error: function() {
            alert("Failed to load combo data");
        }
    });
}

$(document).ready(function () {

    loadComboData('#item_categories', 1, function(){
        
    });
    
    // loadComboData('#filter_transactionmainheads', null, function(){

    // });

});

// function loadItemCategoriesCombo(selected_id = null, callback = null){
//     //  let tran_main_head_id = $('.transactionmainheads').val();
//     // alert(tran_main_head_id);

//     $.ajax({
//         url: '/combo_load/get-item-categories-combo/',
//         method: 'GET',
//         // data:{
//         //     tran_main_head_id: tran_main_head_id,
//         // },
//         success: function(response){

//             let get_item_categories_combo = response.get_item_categories_combo;
//             // let $select = $('#transactionmainheads');
//             let $select = $('#item_categories');

//             $select.empty(); // Clear existing options

//             $.each(get_item_categories_combo, function(index, e) {
//                 $select.append(`<option value="${e.id}">${e.name}</option>`);
//             });

//             $select.val(selected_id);

//             if(callback){
//                 callback();
//             }
//         },
//         error: function() {
//             alert("Failed to load item_catagories");
//         }
//     });
// }

// $('.transactionmainheads').on('change click', function () {

//     loadItemCategoriesCombo(0, function(){
//     });

// });

// $(document).ready(function () {

//     loadItemCategoriesCombo(0, function(){
        
//     });

// });