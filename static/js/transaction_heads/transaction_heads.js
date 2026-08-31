let currentPage = 1;
let loading = false;
let hasMoreData = true;

function loadTransactionHead(page = 1){
    let search_tran_main_head = $('#transactionmainheads').val() || '';
    let search_tran_group = $('#tran_group').val() || '';
    let search_category = $('#transaction_category').val() || '';
    let search_tran_head_id = $('#transaction_head').val() || '';
    let search_tran_head = $('#search_tran_head').val();


    // alert(search_tran_main_head);
    if (loading || !hasMoreData) return;

    loading = true;

    $.ajax({
        url: '/transaction-heads/load-transaction-head/',
        method: 'GET',
        data: {
            page: page,
            limit: 40,
            search_tran_head: search_tran_head,
            search_tran_main_head: search_tran_main_head,
            search_tran_group: search_tran_group,
            search_category: search_category,
            search_tran_head_id: search_tran_head_id,
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
                        <td>${((page - 1) * 40) + index + 1}</td>
                        <td>${a.tran_main_head_name || ''}</td>
                        <td>${a.tran_method}</td>
                        <td>${a.group_name || ''}</td>
                        <td>${a.category_name || ''}</td>
                        <td>${a.tran_head_name}</td>
                        <td>${a.cp}</td>
                        <td>${a.mrp}</td>
                        <td>${a.status}</td>
                        <td>
                            <button class="btn btn-sm btn-warning editBtn" 
                                data-tran_main_head_id="${a.tran_main_head_id}"
                                data-tran_method="${a.tran_method}"
                                data-group_id="${a.group_id}"
                                data-category_id="${a.category_id || ''}"
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

    if (!$('#tran_head_name').length) {
        loadTransactionMainHeadsCombo(null, function () {
            $('#transactionmainheads')
                .prepend('<option value="">All Main Heads</option>')
                .val('');
        });
    }

    loadTransactionHead(currentPage);

    // scroll detection
    let scrollTimeout = null;

    $('#tableContainerRight').on('scroll', function () {

        if (scrollTimeout) return;
        let tableContainer = this;

        scrollTimeout = setTimeout(function () {

            scrollTimeout = null;

            if (
                $(tableContainer).scrollTop() + $(tableContainer).innerHeight()
                >= tableContainer.scrollHeight - 50
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

});

function resetTransactionHeadList() {
    currentPage = 1;
    loading = false;
    hasMoreData = true;
    $('#transactionHeadTableBody').html('');
    loadTransactionHead(currentPage);
}

$(document).on('change', '#transactionmainheads', function () {
    $('#tran_group').empty().append('<option value="">All Groups</option>');
    $('#transaction_category').empty().append('<option value="">All Categories</option>');
    $('#transaction_head').empty().append('<option value="">All Transaction Heads</option>');

    if ($(this).val()) {
        loadTransactionGroupComboOnMainHead(null, function () {
            $('#tran_group option:first').text('All Groups');
            $('#tran_group').val('');
        });
    }
});

$(document).on('change', '#tran_group', function () {
    $('#transaction_head').empty().append('<option value="">All Transaction Heads</option>');
});

$(document).on('click', '#filterBtn', function () {
    resetTransactionHeadList();
});

$(document).on('click', '#printBtn', function () {
    if ($('#transactionHeadTableBody tr').length === 0) {
        alert('No transaction head data to print');
        return;
    }

    let printTable = $('#staffTableRight').clone();
    printTable.find('tr').each(function () {
        $(this).find('th:last, td:last').remove();
    });
    printTable.find('thead')
        .removeClass('table-dark')
        .removeAttr('style');

    let selectedMainHead = $('#transactionmainheads').val()
        ? $('#transactionmainheads option:selected').text()
        : '';
    let selectedGroup = $('#tran_group').val()
        ? $('#tran_group option:selected').text()
        : '';
    let selectedCategory = $('#transaction_category').val()
        ? $('#transaction_category option:selected').text()
        : '';

    $('#transactionHeadPrintArea, #transactionHeadPrintStyle').remove();

    $('body').append(`
        <style id="transactionHeadPrintStyle">
            #transactionHeadPrintArea {
                position: fixed;
                inset: 0;
                z-index: 99999;
                overflow: auto;
                background: #fff;
                padding: 20px;
            }
            #transactionHeadPrintArea h3 {
                text-align: center;
                margin-bottom: 20px;
            }
            #transactionHeadPrintArea .report-filters {
                display: flex;
                gap: 30px;
                margin-bottom: 15px;
            }
            #transactionHeadPrintArea .report-filter-item {
                flex: 1;
            }
            #transactionHeadPrintArea table {
                width: 100%;
                border-collapse: collapse;
                border-spacing: 0;
            }
            #transactionHeadPrintArea th,
            #transactionHeadPrintArea td {
                border: 1px solid #000 !important;
                padding: 6px !important;
                vertical-align: middle;
                line-height: 1.3;
            }
            #transactionHeadPrintArea thead tr {
                height: auto !important;
            }
            #transactionHeadPrintArea thead th {
                background: #fff !important;
                color: #000 !important;
                font-weight: 700 !important;
                text-align: center;
                vertical-align: middle;
                border: 1px solid #000 !important;
                padding: 6px !important;
                opacity: 1 !important;
                box-shadow: none !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
            @page { size: A4 landscape; margin: 10mm; }
            @media print {
                body * {
                    visibility: hidden !important;
                }
                body > *:not(#transactionHeadPrintArea) {
                    display: none !important;
                }
                #transactionHeadPrintArea,
                #transactionHeadPrintArea * {
                    visibility: visible !important;
                }
                #transactionHeadPrintArea {
                    position: static;
                    padding: 0;
                    overflow: visible;
                }
            }
        </style>
        <div id="transactionHeadPrintArea">
            <h3>Transaction Head Report</h3>
            <div class="report-filters">
                <div class="report-filter-item"><strong>Main Head:</strong> ${selectedMainHead}</div>
                <div class="report-filter-item"><strong>Group:</strong> ${selectedGroup}</div>
                <div class="report-filter-item"><strong>Category:</strong> ${selectedCategory}</div>
            </div>
            ${printTable.prop('outerHTML')}
        </div>
    `);

    let clearPrintArea = function () {
        $('#transactionHeadPrintArea, #transactionHeadPrintStyle').remove();
        window.removeEventListener('afterprint', clearPrintArea);
    };

    window.addEventListener('afterprint', clearPrintArea);
    window.print();
});



let mode = $('#tran_head_id').val() ? "update" : "save";   // 👈 GLOBAL
function notifyTransactionHead(message, type) { if (window.toastr) { toastr[type || 'info'](message); } else { alert(message); } } // codex change
	
$(document).on('submit', '#addForm', function(e){ // codex change
	    if (!$('#tran_head_name').length) { return; } // codex change
	    e.preventDefault(); // codex change
	
	    let tran_main_head_id = $('#transactionmainheads').val();
    let tran_method = $('#transaction_method').val();
    let tran_group_id = $('#tran_group').val();
    let category_id = $('#transaction_category').val();
    let tran_head_id = $('#tran_head_id').val();
    let tran_head = $('#tran_head_name').val();
    let tran_head_cp = $('#tran_head_cp').val();
    let tran_head_mrp = $('#tran_head_mrp').val();

    mode = tran_head_id ? "update" : "save";

    // console.log(tran_main_head_id);
    // alert(tran_main_head_id);
    // return;
    if(mode === 'save') {
        notifyTransactionHead("Saving transaction head...", "info"); // codex change
        $('#tran_head_name').val(''); // codex change
        $('#tran_head_cp').val(''); // codex change
        $('#tran_head_mrp').val(''); // codex change
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
                'category_id': category_id,
                'tran_head': tran_head,
                'tran_head_cp': tran_head_cp,
                'tran_head_mrp': tran_head_mrp,
            },           
	            success: function(response) {
	                if (response.status !== 'success') { notifyTransactionHead(response.message || "Failed to save data.", "error"); return; } // codex change
		                resetTransactionHeadList(); // codex change
	                notifyTransactionHead(response.message || "Saved successfully!!", "success"); // codex change
	
	            },
	            error: function(xhr) { // codex change
	                let response = xhr.responseJSON || {}; // codex change
	                notifyTransactionHead(response.message || "Failed to save data.", "error"); // codex change
	            }
	        });
    } else if(mode === 'update') {
        $.ajax({
            url: '/transaction-heads/update-transaction-heads/',
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            data: {
                'tran_head_id': tran_head_id,
                'tran_main_head_id': tran_main_head_id,
                'tran_method': tran_method,
                'tran_group_id': tran_group_id,
                'tran_head': tran_head,
                'category_id': category_id,
                'tran_head_cp': tran_head_cp,
                'tran_head_mrp': tran_head_mrp,                
            },
            success: function(response){

                if (response.status === 'success') {
	                    notifyTransactionHead(response.message, "success"); // codex change
	                    window.location.href = '/transaction-heads/';
	                } else {
	                    notifyTransactionHead(response.message || "Error occurred", "error"); // codex change
	                }
	            },
	            error: function(xhr) { let response = xhr.responseJSON || {}; notifyTransactionHead(response.message || "Failed to update data.", "error"); } // codex change
	        });            
	    }
	});

$(document).on('click', '.editBtn', function(e) {
    e.preventDefault();
    window.location.href = '/transaction-heads/transaction-heads-form/'
        + $(this).data('id')
        + '/edit/';
})

// $(document).on('change', '#transactionmainheads, #tran_group', function() {
//     let groupId = $('#tran_group').val();
//     TransactionCategoryCombo(groupId);
// });
