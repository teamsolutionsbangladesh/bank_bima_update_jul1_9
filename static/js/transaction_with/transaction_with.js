
let mode = "save";   // 👈 GLOBAL

function loadTransactionWith(){

    $.ajax({
        url: '/load-transaction-with/',
        method: 'GET',
        dataType: 'json',
        success: function(response) {
            let transaction_with_list = response.transaction_with_list;
            let tbody = '';

            $.each(transaction_with_list, function(index,a) {
                tbody += `
                    <tr class="tranwith-row"
                        data-tran_type="${a.tran_type}"
                        data-tran_name="${a.type_name}"
                        data-id="${a.id}"
                        data-tran_with_name="${a.tran_with_name}"
                        data-method="${a.method}">

                        <td>${index+1}</td>
                        <td>${a.tran_type}</td>
                        <td>${a.type_name}</td>
                        <td>${a.id}</td>
                        <td>${a.tran_with_name}</td>
                        <td>${a.method}</td>
                        <td>
                            <button class="btn btn-sm btn-warning editBtn" 
                                data-tran_type="${a.tran_type}"
                                data-id="${a.id}"
                                data-method="${a.method}">
                                Edit
                            </button>                        
                            <button class="btn btn-sm btn-danger deleteBtn" 
                                data-id="${a.id}">
                                Delete
                            </button>
                        </td>
                    </tr>
                `;
            });

            $('#transactionWithTableBody').html(tbody);
        },

        error: function() {
            alert('Failed to load transaction with list...');
        }
    });
}

$(document).ready(function() {
    loadTransactionMainHeadsCombo(0,function(){

    });    
    loadTransactionWith();
})

$(document).on('click', '#saveBtn', function(e){
    e.preventDefault();

    let transactionmainheads_id = $('#transactionmainheads').val();
    let tran_method = $('#tran_method').val();
    let tran_with_id = $('#tran_with_id').val();
    let tran_with = $('#tran_with').val();    

    // alert(transactionmainheads_id);
    // alert(tran_method);
    // alert(tran_with_id);
    // alert(tran_with);

    if (!transactionmainheads_id) {
        alert("Please select transaction head.");
        return;
    }
    if (!tran_with) {
        alert("Please enter transaction with name.");
        return;
    }
    // alert(mode);
    // return;
    if(mode === 'save') {
        $.ajax({
            url: '/save-transaction-with/',
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            data: {
                'transactionmainheads_id': transactionmainheads_id,
                'tran_method': tran_method,
                // 'tran_with_id': tran_with_id,
                'tran_with': tran_with,
            },
            success: function(response){
                alert("Saved successfull");
                loadTransactionWith();
                $('#tran_with_id').val('');
                $('#tran_with').val('');
            }
        });
    } else if(mode === 'update') {
        $.ajax({
            url: '/update-transaction-with/',
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            data: {
                'transactionmainheads_id': transactionmainheads_id,
                'tran_method': tran_method,
                'tran_with_id': tran_with_id,
                'tran_with': tran_with,
            },
            success: function(response){
                alert("Updated successfull");
                loadTransactionWith();
                $('#tran_with_id').val('');
                $('#tran_with').val('');
                mode = "save";
                $('#saveBtn').text('Save Account Group');
            }
        });            
    }

});


$(document).on('click', '.editBtn', function(e) {
    e.preventDefault();
  
    $("#transactionmainheads").val($(this).data('tran_type'));
    $("#tran_with_id").val($(this).data('id'));
    let tran_with_id = $(this).data('id');

    $.ajax({
        url: '/transaction-with-fetch-data/',
        method: 'GET',
        data: {'tran_with_id': tran_with_id},
        dataType: 'json',
        success: function(response) { 
            if (response.data.length > 0) {
                $("#tran_with").val(response.data[0].name);
                $("#tran_method").val(response.data[0].method);

            }

            mode = "update";
            $('#saveBtn').text('Update');
        }
    })
})

$(document).on('click', '.deleteBtn', function(e) {
    e.preventDefault();
 
    let tran_with_id = $(this).data('id');

    // alert(tran_with_id);
    // return;        

    if (confirm("Are you sure to delete?")) {
        $.ajax({
            url: '/delete-transaction-with/',
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            data: {
                'tran_with_id': tran_with_id,
            },
            success: function(response){

                if (response.status === 'remove') {
                    alert(response.message || "✅ Remove successful!");
                    loadTransactionWith();
                    $('#tran_with_id').val('');
                    $('#tran_with').val('');
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