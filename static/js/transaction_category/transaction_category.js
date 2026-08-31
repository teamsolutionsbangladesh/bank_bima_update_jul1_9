// --- Dynamic Pagination & State Engine Global Trackers ---
let currentPage = 1;
let loading = false;
let hasMoreData = true;


$(document).ready(function() {

    // --- 1. Dynamic Dropdown Logic Hook via Helper Combo Scripts ---
    getInitDataOnMainHead();

    // Form Dropdown Change tracking setup
    $('#transactionmainheads').change(function() {
        let mainHeadId = $(this).val();
        if(mainHeadId) {
            // Main head change hole related transaction group load korbe dynamically
            loadTransactionGroupComboOnMainHead(null, function(){
                $('#tran_group').prop('selectedIndex', 0); // Default first option set hobe
            });
        } else {
            $('#tran_group').empty().append('<option value="">Select Group</option>');
        }
    });

    // // --- 2. Live Grid Data Initialization Trigger ---
    loadTransactionCategory();

    // // --- 3. Filter Controls Real-Time Engine Event Triggers (Reset & Reload Flow) ---
    // $(document).on("change", "#tableFilterMainHead", function () {
    //     resetTableDataGrid();
    // });

    // $(document).on("keyup", "#search_category", function () {
    //     resetTableDataGrid();
    // });

   let mode = "save";   // 👈 GLOBAL MODE CONTROL

// --- 4. Form Submission Logic Setup (Save/Update Action Cycle) ---
$(document).on('click', '#saveBtn', function(e){
    e.preventDefault();

    let category_id = $('#category_id').val();   // FIX: previously commented out -> was undefined
    let tran_main_head_id = $('#transactionmainheads').val();
    let tran_group_id = $('#tran_group').val();

    let tran_category_name = $('#category_name').val().trim();

    // Standard Front-end field validation
    if(!tran_main_head_id || !tran_group_id || !tran_category_name) {
        alert("Please fill all required fields!");
        return;
    }

    let saveButton = $('#saveBtn');

    // Dynamic CRUD Path Switching based on Global Mode State
    if(mode === 'save') {
        saveButton.prop('disabled', true).html('⏳ Saving Data...');
        
        $.ajax({
            url: 'save/', // Relative path hook matching Django routing
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },      

            data: {
                'tran_main_head_id': tran_main_head_id,
                'tran_group_id': tran_group_id,
                'tran_category_name': tran_category_name,
            },           

            success: function(response) {

                saveButton
                    .prop('disabled', false)
                    .html('💾 Save Category');

                if(response.status === 'success' || response.success) {

                    alert("Save successful");
                    
                    // Input elements data state clear
                    // $('#category_id').val('');
                    $('#category_name').val('');
                    
                    // Table content refresh matching sequence behavior
                    resetTableDataGrid();

                } else {

                    alert("Error: " + response.message);

                }
            },

            error: function() {

                saveButton
                    .prop('disabled', false)
                    .html('💾 Save Category');

                alert("Failed to save data.");

            }
        });
    } 

    else if(mode === 'update') {

        saveButton
            .prop('disabled', true)
            .html('⏳ Updating Data...');

        $.ajax({

            url: 'update/', // Relative update path integration
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },

            data: {
                'category_id' : category_id,
                'tran_category_name': tran_category_name,         
            },

            success: function(response){

                saveButton.prop('disabled', false);

                if (response.status === 'success' || response.success) {

                    alert(response.message || "Update successful");
                    
                    // Clean values and reset engine state variables back to standard
                    $('#category_id').val('');
                    $('#category_name').val('');
                    
                    mode = "save";

                    saveButton
                        .html('💾 Save Category')
                        .removeClass('btn-success')
                        .addClass('btn-primary');
                    
                    // Refresh grid layout starting back from first page index
                    resetTableDataGrid();

                } else {

                    alert(response.message || "Error occurred");

                }
            },

            error: function() {

                saveButton
                    .prop('disabled', false)
                    .html('🔄 Update Category');

                alert("Failed to update data.");

            }
        });            
    }
});
    // --- 5. Action Event Delegations: Edit & Delete Interface Hooks ---
    
    // Edit Click Operation Hook (Loads UI controls and changes Global Mode flag)
    $(document).on('click', '.editBtn', function(e) {
        e.preventDefault();
      
        let targetId = $(this).data('id');
        let mainHeadId = $(this).data('main_head_id');
        let groupId = $(this).data('group_id');
        let catName = $(this).data('cat_name');

        $("#category_id").val(targetId);
        $("#category_name").val(catName);
        $("#transactionmainheads").val(mainHeadId);

        // Group loading pipeline handle logic dynamically
        loadTransactionGroupComboOnMainHead(groupId, function(){
            $('#tran_group').val(groupId);
        });

        mode = "update"; // Switching system state indicator
        $('#saveBtn').html('🔄 Update').removeClass('btn-primary').addClass('btn-success');
        
        $('html, body').animate({ scrollTop: $('#category_name').offset().top - 150 }, 300);
    });

    // Delete Click Operation Hook
    $(document).on('click', '.deleteBtn', function() {
        let targetId = $(this).data('id');
        if(confirm("Are you sure you want to delete this transaction category item?")) {
            $.ajax({
                url: '/transaction-category/delete/', // 💡 Absolute path set kora hoyeche fix er jonno
                type: 'POST',
                headers: { "X-CSRFToken": csrftoken },
                data: { 'id': targetId },
                dataType: 'json',
                success: function(response) {
                    if(response.status === 'success' || response.success) { // 💡 Django context logic fixed
                        alert("Category item deleted successfully.");
                        loadTransactionCategory(); // reload layout setup
                    } else {
                        alert(response.message || "Failed to delete record.");
                    }
                },
                error: function() {
                    alert("Error connection loss on resource truncation.");
                }
            });
        }
    });

    // Infinite Table Scroll Dynamic Paginated Loader Hook
    $('.table-responsive').on('scroll', function() {
        if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight - 10) {
            if (!loading && hasMoreData) {
            loadTransactionCategory();  }
        }
    });
});

// --- Helper Initialization & Dynamic Database Fetch Scripts Section ---

function getInitDataOnMainHead(){
    // Main Heads pipeline structure fetch
    if (typeof loadTransactionMainHeadsCombo === "function") {
        loadTransactionMainHeadsCombo(1, function(){
            $('#transactionmainheads').prop('selectedIndex', 0); // Initial index load configuration
            loadTransactionGroupComboOnMainHead(null, function(){
                $('#tran_group').prop('selectedIndex', 0);
            });

            // Automatically clone Main Heads to Filter dropdown to solve empty filter screen
            let filterSelect = $('#tableFilterMainHead');
            filterSelect.find('option:not(:first)').remove(); // Keep only "All Main Heads"
            $('#transactionmainheads option').each(function(){
                if($(this).val() !== "") {
                    filterSelect.append(`<option value="${$(this).val()}">${$(this).text()}</option>`);
                }
            });
        });
    }
}

function loadTransactionCategory() {

    $.ajax({
        url: '/transaction-category/load-transaction-category/', // 💡 Absolute path set kora hoyeche fix er jonno
        method: 'GET',
        dataType: 'json',

        success: function(response) {
            let transaction_category_list = response.transaction_category_list;
            let tbody = '';

            $.each(transaction_category_list, function(index, a) {
                tbody += `
                    <tr class="trancategory-row"
                        data-tran_main_head_id="${a.tran_main_head_id}"
                        data-group_id="${a.group_id}"
                        data-id="${a.id}"
                        data-name="${a.name}"
                        data-status="${a.status}">

                        <td>${index + 1}</td>
                        <td>${a.tran_main_head_id}</td>
                        <td>${a.group_id}</td>
                        <td>${a.name}</td>
                        <td>${a.status}</td>
                        <td>
                            <button class="btn btn-sm btn-warning editBtn"
                                data-id="${a.id}"
                                data-main_head_id="${a.tran_main_head_id}"
                                data-group_id="${a.group_id}"
                                data-cat_name="${a.name}">
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

            $('#categoryTableBody').html(tbody);
        },

        error: function(xhr, status, error) {
        console.log("Status:", xhr.status);
        console.log("Error:", error);
        console.log("Response:", xhr.responseText);
    }
    });
}
