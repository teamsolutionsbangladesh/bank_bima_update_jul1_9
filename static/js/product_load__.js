$(document).ready(function () {

    // $('#addMedicineModal').on('shown.bs.modal', function () {
    //     $("#productSearch").focus();
    // });

    let products = [];
    let currentIndex = 0;
    let offset = 0;
    let query = "";
    let isLoading = false;
    let limit = 50;

    function loadProducts(q = "", newOffset = 0, append = false) {
        if (isLoading) return;
        isLoading = true;
        let currentIndex = 0;
        $.ajax({
            url: "/product-search/",
            method: "GET",
            data: { q: q, offset: newOffset },
            success: function (response) {
                let fetched = response.results || [];

                if (append) products = products.concat(fetched);
                else {
                    products = fetched;
                    offset = newOffset;
                    currentIndex = 0;
                }

                renderTable();              
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
  

    $("#productSearch").on("keydown", function (e) {

        // let rows = $("#medicineListTableBody tr");
        
        // if (products.length > 0) {
        //     if (e.key === "Enter") {
        //         e.preventDefault();
        //         query = $(this).val().trim();
        //         offset = 0;
        //         loadProducts(query, offset);
                
        //         // Wait for AJAX render
        //         setTimeout(function () {

        //             if (products.length > 0) {

        //                 currentIndex = 0;

        //                 updateHighlight();

        //                 // 🔥 Move focus to first row
        //                 $("#medicineListTableBody tr")
        //                     .eq(0)
        //                     .focus();
        //             }

        //         }, 200);                
        //         return;
        //     }
        // }

        if (e.key === "ArrowDown") {
            e.preventDefault();

            if (currentIndex < products.length - 1) {
                currentIndex++;
                updateHighlight();   // ✅ Only highlight
            }
        }

        if (e.key === "ArrowUp") {
            e.preventDefault();

            if (currentIndex > 0) {
                currentIndex--;
                updateHighlight();   // ✅ Only highlight
            }
        }

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

        if (e.key === "Enter") {

            e.preventDefault();

            let index = $(this).data("index");

            if (index === undefined) return;

            let selectedProduct = products[index];

            if (!selectedProduct) return;

            // 🔥 Fill fields
            $("#productSearch").val(selectedProduct.name);
            $("#cp").val(selectedProduct.cp);
            $("#mrp").val(selectedProduct.mrp);

            // 🔥 Focus quantity
            $("#quantity").focus().select();
        }

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






    // PRICE × QTY calculation
    $("#quantity").on("input", function () {
        let quantity = parseFloat($(this).val()) || 0;
        let price = parseFloat($("#price").val()) || 0;
        let total = quantity * price;
        $("#total").val(total.toFixed(2));
    });

    // ADD to selected list
    function addToSelectedList(pname, price, qty, total) {

        let row = `
            <tr>
                <td>${$("#selectedMedicineList tr").length + 1}</td>
                <td>${pname}</td>
                <td>${qty}</td>
                <td>${price}</td>
                <td>${total}</td>
                <td>
                    <button type="button" class="btn btn-sm btn-danger remove-item">Remove</button>
                </td>
            </tr>
        `;

        $("#selectedMedicineList").append(row);

        // Clear input fields
        $("#productSearch").val("");
        $("#price").val("");
        $("#quantity").val("");
        $("#total").val("");

        updateSelectedTotal();
        updateInvoiceSummary(); 
    }

    // Remove button functionality
    $(document).on("click", ".remove-item", function () {
        $(this).closest("tr").remove();

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
            let price = parseFloat($(this).find("td:eq(3)").text()) || 0;
            let qty = parseFloat($(this).find("td:eq(2)").text()) || 0;
            total += price * qty;
        });
        $("#bottomTotal").text(total.toFixed(2));
    }


    function updateGrandTotal() {
        let total = 0;

        $("#selectedMedicineList tr").each(function () {
            let rowTotal = parseFloat($(this).find(".item-total").text()) || 0;
            total += rowTotal;
        });

        $("#grandTotal").text(total.toFixed(2));
    }

    $(document).on("click", ".deleteRow", function () {
        $(this).closest("tr").remove();
        updateGrandTotal();
        updateSelectedTotal();
        updateInvoiceSummary();
    });
    $("#discount, #advanced").on("input", function () {
        updateInvoiceSummary();
    });

    loadProducts();
});





