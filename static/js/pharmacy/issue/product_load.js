$(document).ready(function () {

    // $('#addMedicineModal').on('shown.bs.modal', function () {
    //     $("#productSearch").focus();
    // });

    let products = [];    
    // let currentIndex = 0;
    let currentRequest = null;
    let offset = 0;
    let query = "";
    let isLoading = false;
    let limit = 50;

    function loadProducts(q = "", newOffset = 0, append = false) {

        if (isLoading) return;

        // 🛑 Abort previous request
        if (currentRequest) {
            currentRequest.abort();
        }

        isLoading = true;
        // currentIndex = 0;

        currentRequest = $.ajax({
            url: "/product-search/",
            method: "GET",
            data: { q: q, offset: newOffset },
            success: function (response) {

                let fetched = response.results || [];

                if (append) {
                    products = products.concat(fetched);
                } else {
                    products = fetched;
                    offset = newOffset;
                    
                    // ✅ Reset ONLY if this is new search
                    if (newOffset === 0) {
                        currentIndex = 0;
                    }
                }

                renderTable();
                isLoading = false;
            },
            error: function (xhr, status) {
                if (status !== "abort") {
                    console.error("AJAX Error:", status);
                }
                isLoading = false;
            }
        });
    }    

    function renderTable() {
        let html = "";
        products.forEach((p, i) => {  
            html += `
                <tr data-index="${i}"
                    tabindex="0"
                    class="${i === currentIndex ? 'table-active' : ''}">
                    <td>${i + 1}</td>
                    <td>${p.name}</td>
                    <td>${p.category_name}</td>
                    <td>${p.manufacturer}</td>
                    <td>${p.form}</td>
                    <td>${p.quantity}</td>
                    <td>${p.cp}</td>
                    <td>${p.mrp}</td>
                    <td>${p.id}</td>
                </tr>
            `;
        });
        $("#medicineListTableBody").html(html);
        scrollToActiveRow();
    }

    
    function scrollToActiveRow() {
        let $activeRow = $("#medicineListTableBody tr.table-active");

        if ($activeRow.length) {
            $activeRow[0].scrollIntoView({
                block: "nearest"
            });
        }
    }    
  
    let typingTimer;
    let typingDelay = 300; // 300ms delay
    $("#productSearch").on("input", function () {

        clearTimeout(typingTimer);

        let value = $(this).val().trim();

        typingTimer = setTimeout(function () {

            query = value;
            offset = 0;

            loadProducts(query, offset, false);

        }, typingDelay);

    });


    $(document).on("keydown", function (e) {

        if (products.length === 0) return;

        if (e.key === "ArrowDown") {
            e.preventDefault();

            if (currentIndex < products.length - 1) {
                currentIndex++;
                updateHighlight();
            }

            if (currentIndex >= products.length - 5) {
                offset += limit;
                loadProducts(query, offset, true);
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

    // When Enter pressed in #productSearch
    $('#productSearch').on('keydown', function(e) {
        if (e.key === "Enter") {
            e.preventDefault();

            if (products.length === 0) return;

            let selectedProduct = products[currentIndex];
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

    // When Enter pressed in #quantity → focus Add button
    $('#quantity').on('keydown', function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            setTimeout(function() {
                $("#addProductBtn").focus();
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

        let productSearch = $('#productSearch').val();

        // 🔥 DUPLICATE CHECK
        let duplicate = false;
        $("#selectedMedicineList tr").each(function () {
            let existingName = $(this).find("td:eq(1)").text().trim();
            if (existingName === productSearch) {
                duplicate = true;
            }
        });

        if (duplicate) {
            alert("❌ This product is already selected!");
            $('#productSearch').focus().select();
            return; // stop executing
        }

        let qty = Number($('#quantity').val().trim());
        let cp  = Number($('#cp').val().trim());
        let mrp  = Number($('#mrp').val().trim());        
        let total = qty * cp;

        if (!productSearch || productSearch.trim() === "") {
            alert("⚠️ Please enter product name!");
            $('#productSearch').focus();
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

        addToSelectedList(productSearch, cp, qty, total);

        setTimeout(function () {
            $('#productSearch').focus().select();
            return;
        }, 100);
        
    });

    function updateHighlight() {

        let rows = $("#medicineListTableBody tr");

        rows.removeClass("table-active");

        if (currentIndex >= 0 && currentIndex < rows.length) {

            let $row = rows.eq(currentIndex);

            $row.addClass("table-active");

            $row[0].scrollIntoView({
                block: "nearest"
            });
        }
    }

    $(document).on("click", "#medicineListTableBody tr", function () {

        // Remove previous highlight
        $("#medicineListTableBody tr").removeClass("table-active");

        // Highlight clicked row
        $(this).addClass("table-active");

        // Optional: update currentIndex
        currentIndex = $(this).data("index");

    });


    $(document).on("keydown", "#medicineListTableBody tr", function (e) {

        if (e.key === "ArrowDown") {
            e.preventDefault();

            // Move highlight down
            if (currentIndex < products.length - 1) {
                currentIndex++;
                updateHighlight();
                $("#medicineListTableBody tr").eq(currentIndex).focus();
            }

            // 🔥 Load more when reaching last 5 rows
            if (
                currentIndex >= products.length - 5 &&
                !isLoading
            ) {
                offset += limit;
                loadProducts(query, offset, true);
            }
        }

        if (e.key === "ArrowUp") {
            e.preventDefault();

            if (currentIndex > 0) {
                currentIndex--;
                updateHighlight();
                $("#medicineListTableBody tr").eq(currentIndex).focus();
            }
        }

    });

    $(".table-responsive").on("scroll", function () {

        let $this = $(this);

        if ($this.scrollTop() + $this.innerHeight() >= this.scrollHeight - 10) {

            offset += limit;

            loadProducts(query, offset, true);
        }
    });


    //========================================================


    // PRICE × QTY calculation
    $("#quantity").on("input", function () {
        let quantity = parseFloat($(this).val()) || 0;
        let cp = parseFloat($("#cp").val()) || 0;
        let total = quantity * cp;
        $("#total").val(total.toFixed(2));
    });

    $("#cp").on("input", function () {
        let cp = parseFloat($(this).val()) || 0;
        let quantity = parseFloat($("#quantity").val()) || 0;
        let total = quantity * cp;
        $("#total").val(total.toFixed(2));
    });

    // ADD to selected list
    function addToSelectedList(pname, cp, qty, total) {

        let row = `
            <tr>
                <td>${$("#selectedMedicineList tr").length + 1}</td>
                <td>${pname}</td>
                <td>${qty}</td>
                <td>${cp}</td>
                <td>${total}</td>
                <td>
                    <button type="button" class="btn btn-sm btn-danger remove-item">Remove</button>
                </td>
            </tr>
        `;

        $("#selectedMedicineList").append(row);

        // Clear input fields
        $("#productSearch").val("");
        $("#cp").val("");
        $("#quantity").val("");
        $("#total").val("");

        updateSelectedTotal();
        updateInvoiceSummary(); 
    }

    // Remove button functionality
    $(document).on("click", ".remove-item", function () {
        // let pname = $(this).closest("tr").find('td:eq(1)').text();

        if (confirm("Are you sure to remove:\n\n" + $(this).closest("tr").find('td:eq(1)').text() + " ?")) {
            $(this).closest("tr").remove();
        }
        // Update SL numbers
        $("#selectedMedicineList tr").each(function (index) {
            $(this).find("td:first").text(index + 1);
        });

        // Update total
        updateSelectedTotal();
    });

    // Function to calculate bottom total
    function updateSelectedTotal() {
        let total = 0;
        $("#selectedMedicineList tr").each(function () {
            let cp = parseFloat($(this).find("td:eq(3)").text()) || 0;
            let qty = parseFloat($(this).find("td:eq(2)").text()) || 0;
            total += cp * qty;
        });
        $("#bottomTotal").text(total.toFixed(2));
    }

    function updateInvoiceSummary() {
        let invoiceAmount = 0;

        // Sum row totals
        $("#selectedMedicineList tr").each(function () {
            let rowTotal = parseFloat($(this).find("td:eq(4)").text()) || 0;
            invoiceAmount += rowTotal;
        });

        let discountPercent = parseFloat($("#discount").val()) || 0;
        let advance = parseFloat($("#advanced").val()) || 0;

        // Calculate discount amount (percentage)
        let discountAmount = (invoiceAmount * discountPercent) / 100;

        // Net amount after discount
        let netAmount = invoiceAmount - discountAmount;
        if (netAmount < 0) netAmount = 0;

        // Balance after advance
        let balance = netAmount - advance;
        if (balance < 0) balance = 0;

        // Set values
        $("#invoiceAmount").val(invoiceAmount.toFixed(2));
        $("#netAmount").val(netAmount.toFixed(2));
        $("#balance").val(balance.toFixed(2));
    }

    function updateGrandTotal() {
        let total = 0;

        $("#selectedMedicineList tr").each(function () {
            let rowTotal = parseFloat($(this).find(".item-total").text()) || 0;
            total += rowTotal;
        });

        $("#grandTotal").text(total.toFixed(2));
    }

    // $(document).on("click", ".deleteRow", function () {
    //     alert("Are you sure to remove");
    //     $(this).closest("tr").remove();
    //     updateGrandTotal();
    //     updateSelectedTotal();
    //     updateInvoiceSummary();
    // });

    $("#discount, #advanced").on("input", function () {
        updateInvoiceSummary();
    });

    loadProducts();
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
        alert("No products selected!");
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
        products: purchaseList
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
            $('#productSearch').focus();
            console.log(response);
        },
        error: function(xhr){
            console.error(xhr.status, xhr.responseText);
            alert("Save failed! Check console for error.");
        }
    });
});
