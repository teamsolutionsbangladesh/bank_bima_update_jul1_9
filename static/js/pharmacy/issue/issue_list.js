$(document).ready(function () {
    function setTodayDate() {
        const today = new Date();
        const localDate =
            today.getFullYear() + "-" +
            String(today.getMonth() + 1).padStart(2, "0") + "-" +
            String(today.getDate()).padStart(2, "0");

        document.getElementById("start_date").value = localDate;
        document.getElementById("end_date").value = localDate;
    }

    setTodayDate();
    
    // $('#addMedicineModal').on('shown.bs.modal', function () {
    //     $("#supplierSearch").focus();
    // });

    let purchaseList = [];    
    // let currentIndex = 0;
    let currentRequest = null;
    let offset = 0;
    let query = "";
    let isLoading = false;
    let limit = 50;

    function loadPurchaseList(q = "", newOffset = 0, append = false) {

        if (isLoading) return;

        // 🛑 Abort previous request
        if (currentRequest) {
            currentRequest.abort();
        }

        isLoading = true;
        // currentIndex = 0;

        currentRequest = $.ajax({
            url: "/purchase-list-load/",
            method: "GET",
            data: { q: q, offset: newOffset },
            success: function (response) {

                let fetched = response.results || [];

                if (append) {
                    purchaseList = purchaseList.concat(fetched);
                } else {
                    purchaseList = fetched;
                    offset = newOffset;
                    
                    // ✅ Reset ONLY if this is new search
                    if (newOffset === 0) {
                        currentIndex = 0;
                    }
                }

                renderTable();
                isLoading = false;
            },
            // error: function (xhr, status) {
            //     if (status !== "abort") {
            //         console.error("AJAX Error:", status);
            //     }
            //     isLoading = false;
            // }
        });
    }    

    function renderTable() {
        let html = "";
        purchaseList.forEach((p, i) => {  
            html += `
                <tr data-index="${i}"
                    tabindex="0"
                    class="${i === currentIndex ? 'table-active' : ''}">
                    <td>${i + 1}</td>
                    <td>${p.tran_id}</td>
                    <td>${p.tran_date}</td>
                    <td>${p.tran_supplier}</td>
                    <td style="text-align:right;">${p.bill_total}</td>
                    <td style="text-align:right;">${p.discount}</td>
                    <td style="text-align:right;">${p.net_total}</td>
                    <td style="text-align:right;">${p.advance}</td>
                    <td style="text-align:right;">${p.due_collection}</td>
                    <td style="text-align:right;">${p.due_discount}</td>
                    <td style="text-align:right;">${p.due}</td>
                    <td style="text-align:center;">
                        <button class="btn btn-sm btn-primary editBtn" data-tran-id="{{ p.tran_id }}">Edit</button>
                        <button class="btn btn-sm btn-success" disabled>Verified</button>
                    </td>
                </tr>
            `;
        });
        $("#purchaseListTableBody").html(html);
        scrollToActiveRow();
    }

    
    function scrollToActiveRow() {
        let $activeRow = $("#purchaseListTableBody tr.table-active");

        if ($activeRow.length) {
            $activeRow[0].scrollIntoView({
                block: "nearest"
            });
        }
    }    
  
    let typingTimer;
    let typingDelay = 300; // 300ms delay
    $("#supplierSearch").on("input", function () {

        clearTimeout(typingTimer);

        let value = $(this).val().trim();

        typingTimer = setTimeout(function () {

            query = value;
            offset = 0;

            loadPurchaseList(query, offset, false);

        }, typingDelay);

    });


    $(document).on("keydown", function (e) {

        if (purchaseList.length === 0) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();

            if (currentIndex < purchaseList.length - 1) {
                currentIndex++;
                updateHighlight();
            }

            if (currentIndex >= purchaseList.length - 5) {
                offset += limit;
                loadPurchaseList(query, offset, true);
            }
        }

        if (e.key === "ArrowUp") {
            e.preventDefault();

            if (currentIndex > 0) {
                currentIndex--;
                updateHighlight();
            }
        }

    });

 
    // $(document).on("keydown", function (e) {

    //     if (e.key !== "Enter") return;

    //     if ($('#productSearch, #quantity, #addProductBtn').is(':focus')) return;

    //     // If products not loaded → do nothing
    //     if (products.length === 0) return;

    //     // If Enter pressed inside search AND no row selected yet
    //     if ($("#productSearch").is(":focus") && currentIndex === 0) {
    //         // Allow selection of first row
    //         e.preventDefault();
    //     }

    //     // If a valid row is selected
    //     if (currentIndex >= 0 && currentIndex < products.length) {

    //         e.preventDefault();

    //         let selectedProduct = products[currentIndex];
    //         if (!selectedProduct) return;

    //         $("#productSearch").val(selectedProduct.name);
    //         $("#productid").val(selectedProduct.id);
    //         $("#cp").val(selectedProduct.cp);
    //         $("#mrp").val(selectedProduct.mrp);
    //         // Focus quantity AFTER current event loop
    //         setTimeout(function() {
    //             $("#quantity").focus().select();
    //         }, 0);
    //     }
    // });    

    // When Enter pressed in #supplierSearch
    $('#supplierSearch').on('keydown', function(e) {
        if (e.key === "Enter") {
            e.preventDefault();

            if (purchaseList.length === 0) return;

            let selectedProduct = purchaseList[currentIndex];
            if (!selectedProduct) return;

            $(this).val(selectedProduct.name);
            $("#productid").val(selectedProduct.id);
            $("#cp").val(selectedProduct.cp);
            $("#mrp").val(selectedProduct.mrp);

            // Focus quantity after current event
            setTimeout(function() {
                $("#quantity").focus().select();
            }, 0);
        }
    });


    // When Enter pressed on Add button → trigger click
    $('#addProductBtn').on('keydown', function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            $(this).click();
        }
    });

    $('#addProductBtn').on('click', function() {
        // e.preventDefault(); // stop form reload

        let supplierSearch = $('#supplierSearch').val();

        // 🔥 DUPLICATE CHECK
        let duplicate = false;
        $("#selectedMedicineList tr").each(function () {
            let existingName = $(this).find("td:eq(1)").text().trim();
            if (existingName === supplierSearch) {
                duplicate = true;
            }
        });

        if (duplicate) {
            alert("❌ This product is already selected!");
            $('#supplierSearch').focus().select();
            return; // stop executing
        }

        let qty = Number($('#quantity').val().trim());
        let cp  = Number($('#cp').val().trim());
        let mrp  = Number($('#mrp').val().trim());        
        let total = qty * cp;

        if (!supplierSearch || supplierSearch.trim() === "") {
            alert("⚠️ Please enter product name!");
            $('#supplierSearch').focus();
            return;
        }

        // Check if empty or zero
        if (isNaN(qty) || qty <= 0) {
            alert("⚠️ Please enter a valid quantity!"); // error message
            $('#quantity').focus().select(); // focus back to quantity
            return; // stop further execution
        }
        
        if (isNaN(cp) || cp <= 0) {
            alert("⚠️ Please enter a valid cost price!");
            $('#cp').focus().select();
            return;
        }

        if (isNaN(mrp) || mrp <= 0) {
            alert("⚠️ Please enter a valid mrp price!");
            $('#mrp').focus().select();
            return;
        }

        if (mrp <= cp) {
            alert("⚠️ Invalid MRP!\n\nMRP must be greater than Cost Price (CP).");
            $('#mrp').focus().select();
            return;
        }

        // Continue adding product logic here
        // addProduct(); // your existing function to add product

        addToSelectedList(supplierSearch, cp, qty, total);

        setTimeout(function () {
            $('#supplierSearch').focus().select();
            return;
        }, 100);
        
    });

    function updateHighlight() {

        let rows = $("#purchaseListTableBody tr");

        rows.removeClass("table-active");

        if (currentIndex >= 0 && currentIndex < rows.length) {

            let $row = rows.eq(currentIndex);

            $row.addClass("table-active");

            $row[0].scrollIntoView({
                block: "nearest"
            });
        }
    }

    $(document).on("click", "#purchaseListTableBody tr", function () {

        // Remove previous highlight
        $("#purchaseListTableBody tr").removeClass("table-active");

        // Highlight clicked row
        $(this).addClass("table-active");

        // Optional: update currentIndex
        currentIndex = $(this).data("index");

    });


    $(document).on("keydown", "#purchaseListTableBody tr", function (e) {

        if (e.key === "ArrowDown") {
            e.preventDefault();

            // Move highlight down
            if (currentIndex < purchaseList.length - 1) {
                currentIndex++;
                updateHighlight();
                $("#purchaseListTableBody tr").eq(currentIndex).focus();
            }

            // 🔥 Load more when reaching last 5 rows
            if (
                currentIndex >= purchaseList.length - 5 &&
                !isLoading
            ) {
                offset += limit;
                loadPurchaseList(query, offset, true);
            }
        }

        if (e.key === "ArrowUp") {
            e.preventDefault();

            if (currentIndex > 0) {
                currentIndex--;
                updateHighlight();
                $("#purchaseListTableBody tr").eq(currentIndex).focus();
            }
        }

    });

    $(".table-responsive").on("scroll", function () {

        let $this = $(this);

        if ($this.scrollTop() + $this.innerHeight() >= this.scrollHeight - 10) {

            offset += limit;

            loadPurchaseList(query, offset, true);
        }
    });


    //========================================================

    loadPurchaseList();
});
// get CSRF from cookie
// get CSRF from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

$('#saveAllBtn').on('click', function (e) {
    e.preventDefault();

    let purchaseList = [];

    // selected medicines table
    $('#selectedMedicineList tr').each(function () {
        let row = $(this);
        // array style for Python index-access
        purchaseList.push([
            row.data('product-id'),                           // tran_head_id
            parseFloat(row.find('td:eq(2)').text()) || 0,    // quantity
            parseFloat(row.find('td:eq(3)').text()) || 0,    // cp
            parseFloat(row.find('td:eq(4)').text()) || 0,    // tot_amount
            parseFloat(row.find('td:eq(5)').text()) || 0,    // discount
            row.data('unit-id'),                              // unit_id
            row.data('expiry')                                // expiry
        ]);
    });

    if (!purchaseList.length) {
        alert("No record selected!");
        return;
    }

    let payload = {
        store: parseInt($('.store-select').val()) || null,
        location: parseInt($('.location-select').val()) || null,
        supplier: parseInt($('.supplier-select').val()) || null,
        invoice: $('#purchaseinvoice').val(),
        payment_method: $('#payment_method').val(),
        bill_amount: parseFloat($('#invoiceAmount').val()) || 0,
        discount: parseFloat($('#discount').val()) || 0,
        net_amount: parseFloat($('#netAmount').val()) || 0,
        receive: parseFloat($('#advanced').val()) || 0,
        due: parseFloat($('#balance').val()) || 0,
        tran_date: $('#date').val(),
        purchaseList: purchaseList
    };

    $.ajax({
        url: "/pharmacy/save-purchase/",
        type: "POST",
        headers: { "X-CSRFToken": csrftoken },
        contentType: "application/json",
        data: JSON.stringify(payload),
        success: function (response) {
            alert("Saved Successfully!");
            $("#selectedMedicineList").empty();   // clear table
            $('#supplierSearch').focus();
            console.log(response);
        },
        error: function(xhr){
            console.error(xhr.status, xhr.responseText);
            alert("Save failed! Check console for error.");
        }
    });
});
