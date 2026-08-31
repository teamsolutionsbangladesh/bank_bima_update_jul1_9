let currentPage = 1;
let loading = false;
let hasMoreData = true;

function loadTransactionHead(page = 1){
    let search_tran_main_head = $('#filter_transactionmainheads').val();  
    let search_tran_head = $('#search_tran_head').val();


    // alert(search_tran_main_head);
    if (loading || !hasMoreData) return;

    loading = true;

    $.ajax({
        url: '/transaction-heads/load-transaction-head/',
        method: 'GET',
        data: {
            page: page,
            limit: 10,
            search_tran_head: search_tran_head,
            search_tran_main_head: search_tran_main_head,
        },        
        dataType: 'json',
        success: function(response) {

            let tbody = '';

            if(response.transaction_head_list.length === 0){
                hasMoreData = false;
                loading = false;
                return;
            }

            response.transaction_head_list.forEach((a, index) => {
                tbody += `
                    <tr>
                        <td>${((page - 1) * 10) + index + 1}</td>
                        <td>${a.tran_main_head_id}</td>
                        <td>${a.tran_method}</td>
                        <td>${a.group_id}</td>
                        <td>${a.id}</td>
                        <td>${a.tran_head_name}</td>
                        <td>${a.cp}</td>
                        <td>${a.mrp}</td>
                        <td>${a.status}</td>
                        <td>
                            <button class="btn btn-sm btn-warning editBtn" 
                                data-tran_main_head_id="${a.tran_main_head_id}"
                                data-tran_method="${a.tran_method}"
                                data-group_id="${a.group_id}"
                                data-id="${a.id}"
                                data-tran_head_name="${a.tran_head_name}"
                                data-cp="${a.cp}"
                                data-mrp="${a.mrp}"
                                data-status="${a.status}">
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

            // append instead of html()
            $('#transactionHeadTableBody').append(tbody);

            currentPage++;

            loading = false;
        },

        error: function() {
            loading = false;
            alert('Failed to load transaction head list...');
        }
    });
}

$(document).ready(function() {

    // first load
    loadTransactionHead(currentPage);

    // scroll detection
    let scrollTimeout = null;

    $(window).on('scroll', function () {

        if (scrollTimeout) return;

        scrollTimeout = setTimeout(function () {

            scrollTimeout = null;

            if (
                $(window).scrollTop() + $(window).height()
                >= $(document).height() - 150
            ) {
                loadTransactionHead(currentPage);
            }

        }, 200); // throttle delay
    });

    $("#search_tran_head").on("input", function () {

        currentPage = 1;
        hasMoreData = true;

        $('#transactionHeadTableBody').html('');

        loadTransactionHead(currentPage);
    }) 
 

})


$(document).on("change", ".transactionmainheads", function () {

    currentPage = 1;
    hasMoreData = true;

    $('#transactionHeadTableBody').html('');

    loadTransactionHead(currentPage);
});

$(document).on("change", "#filter_transactionmainheads", function () {

    currentPage = 1;
    hasMoreData = true;

    $('#transactionHeadTableBody').html('');

    loadTransactionHead(currentPage);
});



let mode = "save";   // 👈 GLOBAL

$(document).on('click', '#saveBtn', function(e){
    e.preventDefault();

    let tran_main_head_id = $('#transactionmainheads').val();
    let tran_method = $('#transaction_method').val();
    let tran_group_id = $('#tran_group').val();
    let tran_head_id = $('#tran_head_id').val();
    let tran_head = $('#tran_head').val();
    let tran_head_cp = $('#tran_head_cp').val();
    let tran_head_mrp = $('#tran_head_mrp').val();

    // console.log(tran_main_head_id);
    // alert(tran_main_head_id);
    // return;
    if(mode === 'save') {
        $.ajax({
            url: '/transaction-heads/save-transaction-heads/',
            method: 'POST',
            headers: {
                "X-CSRFToken": csrftoken
            },             
            data: {
                'tran_main_head_id': tran_main_head_id,
                'tran_method': tran_method,
                'tran_group_id': tran_group_id,
                'tran_head': tran_head,
                'tran_head_cp': tran_head_cp,
                'tran_head_mrp': tran_head_mrp,
            },           
            success: function(response) {
                $('#filter_transactionmainheads').trigger('change'); 
                $('#transactionmainheads').trigger('change');
                $('#tran_head').val('');
                alert("Save successfull");

            },
            error: function() {
                alert("Failed to save data.");
            }
        });
    } else if(mode === 'update') {
        $.ajax({
            url: '/transaction-heads/update-transaction-heads/',
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            data: {
                'tran_head_id': tran_head_id,
                'tran_head': tran_head,
                'tran_head_cp': tran_head_cp,
                'tran_head_mrp': tran_head_mrp,                
            },
            success: function(response){

                if (response.status === 'success') {
                    alert(response.message);
                    loadTransactionHead(1);
                    $('#tran_head_id').val('');
                    $('#tran_head').val('');
                    mode = "save";
                    $('#saveBtn').text('Save Account Group');
                } else {
                    alert(response.message || "Error occurred");
                }
            }
        });            
    }
});

$(document).on('click', '.editBtn', function(e) {
    e.preventDefault();
  
    $("#transactionmainheads").val($(this).data('tran_main_head_id'));
    $("#transaction_method").val($(this).data('tran_method'));
    $("#tran_group").val($(this).data('group_id'));
    $("#tran_head_id").val($(this).data('id'));
    $("#tran_head").val($(this).data('tran_head_name'));
    $("#tran_head_cp").val($(this).data('cp'));
    $("#tran_head_mrp").val($(this).data('mrp'));
    $("#status").val($(this).data('status'));

    mode = "update";
    $('#saveBtn').text('Update');

    // $.ajax({
    //     url: '/transaction-with-fetch-data/',
    //     method: 'GET',
    //     data: {'tran_with_id': tran_with_id},
    //     dataType: 'json',
    //     success: function(response) { 
    //         if (response.data.length > 0) {
    //             $("#tran_with").val(response.data[0].name);
    //             $("#tran_method").val(response.data[0].method);

    //         }

    //         mode = "update";
    //         $('#saveBtn').text('Update');
    //     }
    // })
})