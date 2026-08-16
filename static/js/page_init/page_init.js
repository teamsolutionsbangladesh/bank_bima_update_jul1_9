function loadPageInit(){

    $.ajax({
        url: '/load-page-init-list/',
        method: 'GET',
        dataType: 'json',
        success: function(response) {
            let page_init_list = response.page_init_list;
            let tbody = '';

            $.each(page_init_list, function(index,a) {
                tbody += `
                    <tr class="list-row"
                        data-id="${a.id}"
                        data-page_id="${a.page_id}"
                        data-tran_main_head_id="${a.tran_main_head_id}"
                        data-tran_method="${a.tran_method}"
                        data-tran_group_id="${a.tran_group_id}"                        
                        data-user_tran_method="${a.user_tran_method}"
                        data-user_tran_with_id="${a.user_tran_with_id}"
                        data-status="${a.status}">

                        <td>${index+1}</td>
                        <td>${a.id}</td>
                        <td>${a.page_id}</td>
                        <td>${a.tran_main_head_id}</td>
                        <td>${a.tran_method}</td>
                        <td>${a.tran_group_id}</td>                        
                        <td>${a.user_tran_method}</td>
                        <td>${a.user_tran_with_id}</td>
                        <td>${a.status}</td>
                        <td>
                            <button class="btn btn-sm btn-warning editBtn" 
                                data-id="${a.id}"
                                data-page_id="${a.page_id}"
                                data-tran_main_head_id="${a.tran_main_head_id}"
                                data-tran_method="${a.tran_method}"
                                data-tran_group_id="${a.tran_group_id}"                                
                                data-user_tran_method="${a.user_tran_method}"
                                data-user_tran_with_id="${a.user_tran_with_id}"
                                data-status="${a.status}">
                                Edit
                            </button>                        
                            <button class="btn btn-sm btn-danger deleteBtn" 
                                data-id="${a.id}"
                                data-page_id="${a.page_id}">
                                Delete
                            </button>
                        </td>
                    </tr>
                `;
            });

            $('#pageInitTableBody').html(tbody);
        },

        error: function() {
            alert('Failed to load page init list...');
        }
    });
}

$(document).ready(function() {
    loadPageInit();
})



let mode = "save";   // 👈 GLOBAL

$(document).on('click', '#saveBtn', function(e) {
    e.preventDefault();

    let load_head_all;

    if ($("#load_head_all").is(":checked")) {
        load_head_all = 1;
    } else {
        load_head_all = 0;
    }
    let page_id = $('#page_id').val();    
    let transactionmainheads = $('#transactionmainheads').val();
    let transaction_with_method = $('#transaction_with_method').val();
    let transaction_with = $('#transaction_with').val();
    let transaction_method = $('#transaction_method').val();
    let tran_group = $('#tran_group').val();

    if (!page_id) {
        alert("Please enter page_id.");
        return;
    }
    // alert(page_id);
    // alert(transactionmainheads);
    // alert(load_head_all);
    // alert(transaction_with_method);
    // alert(transaction_with);
    // alert(transaction_method);
    // alert(tran_group);
    // alert(mode);
    // return;        
    if(mode === 'save') {
        $.ajax({
            url: '/save-page-init/',
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            data: {
                'page_id': page_id,
                'transactionmainheads': transactionmainheads,
                'load_head_all': load_head_all,
                'transaction_with_method': transaction_with_method,
                'transaction_with': transaction_with,
                'transaction_method': transaction_method,
                'tran_group': tran_group,
            },
            success: function(response){
                alert("Saved successfull");
                loadPageInit();
                // $('#page_id').val('');
            },
            error: function(xhr, status, error){
                console.log(xhr.status);
                console.log(xhr.responseText);
                alert("Error");
            }            
        });
    } else if(mode === 'update') {
        $.ajax({
            url: '/update-page-init/',
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            data: {
                'page_id': page_id,
                'transactionmainheads': transactionmainheads,
                'transaction_with_method': transaction_with_method,
                'transaction_with': transaction_with,
                'transaction_method': transaction_method,
                'tran_group': tran_group,
            },
            success: function(response){
                alert("Updated successfull");
                loadPageInit();
                // $('#page_id').val('');
                // $("#transactionmainheads").val('');
                // $("#transaction_with_method").val('');
                // $("#transaction_with").val('');
                // $("#transaction_method").val('');
                // $("#tran_group").val('');

                mode = "save";
                $('#saveBtn').text('Save');
            }
        });
    }
    $('#page_id').val('');
    $("#transactionmainheads").val('');
    $("#transaction_with_method").val('');
    $("#transaction_with").val('');
    $("#transaction_method").val('');
    $("#tran_group").val('');
  
});



$(document).on('click', '.editBtn', function(e) {
    e.preventDefault();

    // $('#updateBtn').show();

    let page_id = $(this).data('page_id');

    $.ajax({
        url: '/fetch-data-for-edit/',
        method: 'GET',
        data: {'page_id': page_id},
        dataType: 'json',
        success: function(response) { 
            if (response.data.length > 0) {

                console.log(response.data[0].page_id);
                console.log(response.data[0].tran_main_head_id);
                console.log(response.data[0].user_tran_method);
                console.log(response.data[0].user_tran_with_id);
                console.log(response.data[0].tran_method);
                console.log(response.data[0].tran_group_id);

                $("#page_id").val(response.data[0].page_id);
                // $("#transactionmainheads").val(response.data[0].tran_main_head_id);
                // $("#transaction_with_method").val(response.data[0].user_tran_method);
                // $("#transaction_with").val(response.data[0].user_tran_with_id);
                // $("#transaction_method").val(response.data[0].tran_method);
                // $("#tran_group").val(response.data[0].tran_group_id);

                loadTransactionMainHeadsCombo(response.data[0].tran_main_head_id, function(){
                    // alert("Loading of tran MAIN HEAD. done");
                    loadTransactionMethodsCombo(response.data[0].tran_method, function(){
                        loadTransactionGroupCombo(response.data[0].tran_group_id, function(){
                            // alert("Loading of tran GROUP. done");
                            // loadProducts();
                        });
                    });

                    loadTransactionWithMethodsCombo(response.data[0].user_tran_method, function(){
                        // alert("Loading of tran METHOD. done");
                        loadTransactionWithCombo(response.data[0].user_tran_with_id, function(){
                            // alert("Loading of tran TRAN WITH. done");
                            // loadTransactionWithUserCombo();
                        });
                    });
                });                

            }

            mode = "update";
            $('#saveBtn').text('Update');
        }
    })
})

$(document).on('click', '.deleteBtn', function(e) {
    e.preventDefault();
 
    let sub_id = $(this).data('id');

    // alert(sub_id);
    // return;        
    if (confirm("Confirm to remove this subject?")) {
        $.ajax({
            url: '/remove-subject/',
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            data: {
                'sub_id': sub_id,
            },
            success: function(response){

                if (response.status === 'remove') {
                    alert(response.message || "✅ Remove successful!");
                    loadSubject();
                    $('#name').val('');
                } else {
                    alert(response.message || "Error occurred");
                }

            },
            // error: function(){
            //     alert("Delete failed");
            // }        
        });
    }
});

$(document).on('click', '.canceleBtn', function(e) {
    e.preventDefault();

    $('#page_id').val('');
    $("#transactionmainheads").val('');
    $("#transaction_with_method").val('');
    $("#transaction_with").val('');
    $("#transaction_method").val('');
    $("#tran_group").val('');
    mode = "save";
    $('#saveBtn').text('Save');
 
    
});