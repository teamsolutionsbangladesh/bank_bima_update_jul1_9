$(document).ready(function () {    
    $("#quantity").val(1).prop("readonly", true);
    $("#cp").val(0).prop("readonly", true);
    $("#mrp").val(0).prop("readonly", true);

    // default CP & MRP
    // $("#cp").val(0);
    // $("#mrp").val(0);
    function setTodayDate() {
        const today = new Date();
        const localDate =
            today.getFullYear() + "-" +
            String(today.getMonth() + 1).padStart(2, "0") + "-" +
            String(today.getDate()).padStart(2, "0");

        document.getElementById("tranDate").value = localDate;
        document.getElementById("expiryDate").value = localDate;
    }

    setTodayDate();    

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
            url: "/general/product-search/",
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
                $('#productSearch').focus();
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
        $("#receiveListTableBody").html(html);
        scrollToActiveRow();
    }

    
    function scrollToActiveRow() {
        let $activeRow = $("#receiveListTableBody tr.table-active");

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
                $("#addProductBtn").focus();
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
$("#addProductBtn").off("click").on("click", function () {

    let productId = $('#productid').val().trim();
    let name = $('#productSearch').val().trim();
    let qty = Number($('#quantity').val().trim());
    let cp = Number($('#cp').val().trim());
    let mrp = Number($('#mrp').val().trim());
    let expiry = $('#expiryDate').val().trim();

    let total = qty * cp;

    let existingRow = $(this).data("editRow");

    // ✅ VALIDATION (same as your old)
    if (!name) {
        alert("⚠️ Please enter product name!");
        $('#productSearch').focus();
        return;
    }

    // if (isNaN(qty) || qty <= 0) {
    //     alert("⚠️ Please enter a valid quantity!");
    //     $('#quantity').focus().select();
    //     return;
    // }

    // if (isNaN(cp) || cp <= 0) {
    //     alert("⚠️ Please enter a valid cost price!");
    //     $('#cp').focus().select();
    //     return;
    // }

    // if (isNaN(mrp) || mrp <= 0) {
    //     alert("⚠️ Please enter a valid MRP!");
    //     $('#mrp').focus().select();
    //     return;
    // }

    // if (mrp <= cp) {
    //     alert("⚠️ MRP must be greater than CP!");
    //     $('#mrp').focus().select();
    //     return;
    // }

    // ✅ DUPLICATE CHECK (only for ADD, not edit)
    if (!existingRow) {
        let duplicate = false;

        $("#selectedReceiveListReceive tr").each(function () {
            if ($(this).data("product-id") == productId) {
                duplicate = true;
                return false;
            }
        });

        if (duplicate) {
            alert("❌ This product is already selected!");
            $('#productSearch').focus().select();
            return;
        }
    }

    // ✏️ UPDATE MODE
    if (existingRow) {

        existingRow.find("td:eq(2)").text(name);
        existingRow.find("td:eq(3)").text(qty);
        existingRow.find("td:eq(4)").text(cp);
        existingRow.find("td:eq(5)").text(mrp);
        existingRow.find("td:eq(6)").text(expiry);
        existingRow.find("td:eq(7)").text(total);

        $(this).removeData("editRow");

        // optional UX
        $("#addProductBtn").text("Add");

    } else {
        // ➕ ADD MODE
        addToSelectedList(productId, name, qty, cp, mrp, expiry, total);
    }

    clearInputs();
    updateInvoiceSummary();

    setTimeout(function () {
        $('#productSearch').focus().select();
    }, 100);

});

    function updateHighlight() {

        let rows = $("#receiveListTableBody tr");

        rows.removeClass("table-active");

        if (currentIndex >= 0 && currentIndex < rows.length) {

            let $row = rows.eq(currentIndex);

            $row.addClass("table-active");

            $row[0].scrollIntoView({
                block: "nearest"
            });
        }
    }

    $(document).on("click", "#receiveListTableBody tr", function () {

        // Remove previous highlight
        $("#receiveListTableBody tr").removeClass("table-active");

        // Highlight clicked row
        $(this).addClass("table-active");

        // Optional: update currentIndex
        currentIndex = $(this).data("index");

    });


    $(document).on("keydown", "#receiveListTableBody tr", function (e) {

        if (e.key === "ArrowDown") {
            e.preventDefault();

            // Move highlight down
            if (currentIndex < products.length - 1) {
                currentIndex++;
                updateHighlight();
                $("#receiveListTableBody tr").eq(currentIndex).focus();
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
                $("#receiveListTableBody tr").eq(currentIndex).focus();
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
    function addToSelectedList(productId, pname, qty, cp, mrp, expiry, total) {

        let row = `
            <tr data-product-id="${productId}">
            
                <td>${$("#selectedReceiveListReceive tr").length + 1}</td>
                <td style="display:none;">${productId}</td>
                <td>${pname}</td>
                <td>${qty}</td>
                <td>${cp}</td>
                <td style="display:none;">${mrp}</td>
                <td style="display:none;">${expiry}</td>
                <td>${total}</td>
                <td>
                    <button type="button" class="btn btn-sm btn-primary edit-item">Edit</button>
                    <button type="button" class="btn btn-sm btn-danger remove-item">Remove</button>
                </td>
            </tr>
        `;

        $("#selectedReceiveListReceive").append(row);

        // Clear input fields
        $("#productid").val("");
        $("#productSearch").val("");
        $("#cp").val("");
        $("#mrp").val("");
        $("#quantity").val("");
        $("#total").val("");

        // updateSelectedTotal();
        updateInvoiceSummary(); 
    }

    $(document).on("click", ".edit-item", function () {

    let row = $(this).closest("tr");

    let productId = row.find("td:eq(1)").text();
    let name = row.find("td:eq(2)").text();
    let qty = row.find("td:eq(3)").text();
    let cp = row.find("td:eq(4)").text();
    let mrp = row.find("td:eq(5)").text();
    let expiry = row.find("td:eq(6)").text();

    // form এ বসাও
    $("#productid").val(productId);
    $("#productSearch").val(name);
    $("#quantity").val(qty);
    $("#cp").val(cp);
    $("#mrp").val(mrp);
    $("#expiryDate").val(expiry);

    // এই row টা save করে রাখো (important)
    $("#addProductBtn").data("editRow", row);
});



function clearInputs() {
    $("#productid").val("");
    $("#productSearch").val("");
    $("#cp").val("0");
    $("#mrp").val("0");
    $("#quantity").val("1");
    $("#total").val("");
    $("#expiryDate").val("");
}

function updateSerial() {
    $("#selectedReceiveListReceive tr").each(function(index) {
        $(this).find("td:eq(0)").text(index + 1);
    });
}

    // Remove button functionality
    $(document).on("click", ".remove-item", function () {
        // let pname = $(this).closest("tr").find('td:eq(1)').text();

        if (confirm("Are you sure to remove:\n\n" + $(this).closest("tr").find('td:eq(1)').text() + " ?")) {
            $(this).closest("tr").remove();
        }
        // Update SL numbers
        $("#selectedReceiveListReceive tr").each(function (index) {
            $(this).find("td:first").text(index + 1);
        });

        $('#productSearch').focus();
        updateSerial();
        updateInvoiceSummary();
        // Update total
        // updateSelectedTotal();
    });

    // Function to calculate bottom total
    // function updateSelectedTotal() {
    //     let total = 0;
    //     $("#selectedMedicineListPurchase tr").each(function () {
    //         let cp = parseFloat($(this).find("td:eq(3)").text()) || 0;
    //         let qty = parseFloat($(this).find("td:eq(2)").text()) || 0;
    //         total += cp * qty;
    //     });
    //     $("#bottomTotal").text(total.toFixed(2));
    // }

    function updateInvoiceSummary() {
        let invoiceAmount = 0;

        // Sum row totals
        $("#selectedReceiveListReceive tr").each(function () {
            let rowTotal = parseFloat($(this).find("td:eq(7)").text()) || 0;
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

        $("#selectedReceiveListReceive tr").each(function () {
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
function loadTransactionWith() {
    $.ajax({
        url: window.APP_URLS.TRANSACTION_WITH_URL,
        type: "GET",
        success: function (data) {

            console.log("TRANSACTION WITH DATA:", data);

            let html = `<option value="">Select</option>`;

            data.forEach(item => {
                html += `<option value="${item.id}">
                            ${item.tran_with_name || item.name}
                         </option>`;
            });

            $("#transaction_with").html(html);
        },
        error: function (err) {
            console.log("ERROR loading transaction_with:", err);
        }
    });
}

$("#transaction_with").on("change", function () {

    let id = $(this).val();

    if (!id) {
        $("#supplier").html(`<option value="">Select Supplier</option>`);
        return;
    }

    $("#supplier").html(`<option>Loading...</option>`);

    $.ajax({
        url: "/general/get-supplier-by-tran-with-g/",
        data: { tran_with_id: id },
        success: function (res) {

            let html = `<option value="">Select Supplier</option>`;

            if (!res || res.length === 0) {
                html = `<option>No Supplier Found</option>`;
            }

            res.forEach(item => {
                html += `<option value="${item.id}">
                            ${item.user_name}
                         </option>`;
            });

            $("#supplier").html(html);
        },
        error: function () {
            $("#supplier").html(`<option>Failed</option>`);
        }
    });
});
    loadTransactionWith();
    loadProducts();

    // $('#productSearch').focus();
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

    let receiveList = [];

    // selected medicines table
    $('#selectedReceiveListReceive tr').each(function () {
        let row = $(this);
        // array style for Python index-access
        // purchaseList.push([
        //     parseFloat(row.find('td:eq(1)').text()) || 0,    // 0. productid / tran_head_id
        //     parseFloat(row.find('td:eq(3)').text()) || 0,    // 1. quantity
        //     parseFloat(row.find('td:eq(4)').text()) || 0,    // 2. cp
        //     parseFloat(row.find('td:eq(5)').text()) || 0,    // 3. mrp
        //     row.find('td:eq(6) input').val(),   // 4. expiry
        //     parseFloat(row.find('td:eq(7)').text()) || 0,    // 5. tot_amount
        // ]);
        receiveList.push([
        row.data('product-id'),                         // product id
        parseFloat(row.find('td:eq(3)').text()) || 0,   // qty
        parseFloat(row.find('td:eq(4)').text()) || 0,   // cp
        parseFloat(row.find('td:eq(5)').text()) || 0,   // mrp
        row.find('td:eq(6)').text() || null,            // expiry
        parseFloat(row.find('td:eq(7)').text()) || 0    // total
    ]);
    });

    if (!receiveList.length) {
        alert("No products selected!");
        return;
    }

    let receive = parseFloat($('#advanced').val()) || 0;
    let net_amount = parseFloat($('#netAmount').val()) || 0;

    console.log("Receive:", receive, "Net:", net_amount); // check values

    if (receive > net_amount) {
        alert("⚠️ Invalid Receive/Advance Amount! It cannot exceed Net Amount.");
        $('#advanced').focus().select();
        return;
    }    

    let payload = {
        store: parseInt($('.store-select').val()) || null,
        location: parseInt($('.location-select').val()) || null,
        supplier: parseInt($('#supplier').val()) || null,

        tran_type_with: parseInt($('#transaction_with').val()) || null,
        tran_type: 1,          // Pharmacy
        tran_method: "receive",
        invoice: $('#receiveinvoice').val(),
        payment_method: $('#payment_method').val(),
        bill_amount: parseFloat($('#invoiceAmount').val()) || 0,
        discount: parseFloat($('#discount').val()) || 0,
        net_amount: parseFloat($('#netAmount').val()) || 0,
        payment: 0,
        receive: parseFloat($('#advanced').val()) || 0,
        due: parseFloat($('#balance').val()) || 0,
        tran_date: $('#tranDate').val(),
        products: receiveList        
    };
    
    $.ajax({
        url: "/general/receive/save-receive/",
        type: "POST",
        headers: { "X-CSRFToken": csrftoken },
        contentType: "application/json",
        data: JSON.stringify(payload),
        success: function (response) {
            alert("Saved Successfully!");
            $("#selectedReceiveListReceive").empty();   // clear table
            $("#invoiceAmount").val("0");
            $("#discount").val("0");
            $("#netAmount").val("0");
            $("#advanced").val("0");
            $("#balance").val("0");
            $('#productSearch').focus();
            console.log(response);
        },
        error: function(xhr){
            console.error(xhr.status, xhr.responseText);
            alert("Save failed! Check console for error.");
        }
    });
});
