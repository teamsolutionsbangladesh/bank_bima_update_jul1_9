let currentRequest = null;
let offset = 0;
let query = "";
let isLoading = false;
let limit = 50;

function setTodayDate() {
    const today = new Date();

    const localDate =
        today.getFullYear() + "-" +
        String(today.getMonth() + 1).padStart(2, "0") + "-" +
        String(today.getDate()).padStart(2, "0");

    if (document.getElementById("tranDate")) {
        document.getElementById("tranDate").value = localDate;
    }

    if (document.getElementById("expiryDate")) {
        document.getElementById("expiryDate").value = localDate;
    }
}

function updateProductTotal() {
    let quantity = parseFloat($("#quantity").val()) || 0;
    let mrp = parseFloat($("#mrp").val()) || 0;

    let total = quantity * mrp;

    $("#total").val(total.toFixed(2));
}

$(document).ready(function () {

    $("#quantity").val(1).prop("readonly", true);
    $("#cp").val(0).prop("readonly", true);
    $("#mrp").val(0).prop("readonly", true);

    setTodayDate();

    function openProductSearch() {
    if (!$("#productSearch").data("select2")) {
        return;
    }

    $("#productSearch").select2("open");

    setTimeout(function () {
        let searchField = document.querySelector(
            ".select2-container--open .select2-search__field"
        );

        if (searchField) {
            searchField.focus();
            searchField.select();
        }
    }, 150);
}

    function focusProductBoxOnly() {
        let productBox = $("#productSearch")
            .next(".select2-container")
            .find(".select2-selection");

        if (productBox.length) {
            productBox.focus();
        }
    }

    function openSelect2Search(selector) {
        $(selector).select2("open");

        setTimeout(function () {
            let searchField = document.querySelector(
                ".select2-container--open .select2-search__field"
            );

            if (searchField) {
                searchField.focus();
                searchField.select();
            }
        }, 100);
    }

    // =========================
    // PAGE LOAD FOCUS
    // =========================
    // Product dropdown auto-open korbo na.
    // Auto-open korle Transaction Group dropdown blink kore close hoy.
    // =========================
// PAGE LOAD FOCUS
// =========================
setTimeout(function () {
    $("#pat_name").focus().select();
}, 300);

// =========================
// KEYBOARD FLOW
// Patient → Doctor → SR → Product
// =========================

$("#pat_name")
    .off("keydown.keyboardFlow")
    .on("keydown.keyboardFlow", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            $("#pat_age_y").focus().select();
        }
    });

$("#pat_age_y")
    .off("keydown.keyboardFlow")
    .on("keydown.keyboardFlow", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            $("#pat_age_m").focus().select();
        }
    });

$("#pat_age_m")
    .off("keydown.keyboardFlow")
    .on("keydown.keyboardFlow", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            $("#pat_age_d").focus().select();
        }
    });

$("#pat_age_d")
    .off("keydown.keyboardFlow")
    .on("keydown.keyboardFlow", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            $("#pat_gender").focus();
        }
    });

$("#pat_gender")
    .off("keydown.keyboardFlow")
    .on("keydown.keyboardFlow", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            $("#pat_phone").focus().select();
        }
    });

$("#pat_phone")
    .off("keydown.keyboardFlow")
    .on("keydown.keyboardFlow", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            $("#pat_address").focus().select();
        }
    });

$("#pat_address")
    .off("keydown.keyboardFlow")
    .on("keydown.keyboardFlow", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            openSelect2Search("#doc_lookup");
        }
    });

// Doctor select → SR
$("#doc_lookup")
    .off("select2:select.keyboardFlow")
    .on("select2:select.keyboardFlow", function () {
        setTimeout(function () {
            openSelect2Search("#sr_lookup");
        }, 100);
    });

// SR select → Product Search
$("#sr_lookup")
    .off("select2:select.keyboardFlow")
    .on("select2:select.keyboardFlow", function () {
        setTimeout(function () {
            openProductSearch();
        }, 100);
    });
    });

    // =========================
    // PRODUCT FILTER DEPENDENCY
    // =========================
    // Main head / group change hole product clear hobe.
    // But product search auto-open/focus hobe na.
    $("#transactionmainheads")
        .off("change.productFilter")
        .on("change.productFilter", function () {
            $("#productSearch").val(null).trigger("change");
        });

    $("#tran_group")
        .off("change.productFilter")
        .on("change.productFilter", function () {
            $("#productSearch").val(null).trigger("change");
        });

    // =========================
    // QTY / ADD BUTTON KEYBOARD
    // =========================
    $("#quantity").on("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();

            setTimeout(function () {
                $("#addProductBtn").focus();
            }, 0);
        }
    });

    $("#addProductBtn").on("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            $(this).click();
        }
    });

    // =========================
    // ADD PRODUCT
    // =========================
    $("#addProductBtn").off("click").on("click", function () {

        let productId = ($("#productid").val() || "").toString().trim();
        let name = ($("#productSearch option:selected").text() || "").toString().trim();

        if (
            !name ||
            name === "-- Start Typing Product ID / Name --"
        ) {
            name = "";
        }

        let qty = Number(($("#quantity").val() || "1").toString().trim());
        let cp = Number(($("#cp").val() || "0").toString().trim());
        let mrp = Number(($("#mrp").val() || "0").toString().trim());

        let expiry = ($("#expiryDate").val() || "").toString().trim();

        let total = qty * mrp;

        // ✅ DOCTOR + PATIENT VALIDATION BEFORE ADD
        let doctorId = ($("#doc_id").val() || "").trim();
        let patientName = ($("#pat_name").val() || "").trim();

        // Doctor must be selected
        if (!doctorId) {
            alert("⚠️ Please select a doctor first!");

            setTimeout(function () {
                $("#doc_lookup").select2("open");

                setTimeout(function () {
                    let doctorSearchInput = document.querySelector(
                        ".select2-container--open .select2-search__field"
                    );

                    if (doctorSearchInput) {
                        doctorSearchInput.focus();
                        doctorSearchInput.select();
                    }
                }, 100);
            }, 100);

            return;
        }

        // Only Patient Name required
        if (!patientName) {
            alert("⚠️ Please enter patient name!");

            setTimeout(function () {
                $("#pat_name").focus().select();
            }, 100);

            return;
        }

        // ✅ PRODUCT VALIDATION
        if (!name) {
            alert("⚠️ Please enter product name!");
            openProductSearch();
            return;
        }

        if (!productId) {
            alert("⚠️ Please select a product from the list!");
            openProductSearch();
            return;
        }

        // ✅ DUPLICATE CHECK
        let duplicate = false;

        $("#selectedPaymentListPayment tr").each(function () {
            if ($(this).data("product-id") == productId) {
                duplicate = true;
                return false;
            }
        });

        if (duplicate) {
            alert("❌ This product is already selected!");
            openProductSearch();
            return;
        }

        // ✅ ADD TO SELECTED TABLE
        addToSelectedList(
            productId,
            name,
            qty,
            cp,
            mrp,
            expiry,
            total
        );

        
        clearInputs();
        updateInvoiceSummary();

        setTimeout(function () {
            showAddMoreProductModal();
        }, 100);
    });

    // ==========================================
    // ADD MORE PRODUCT MODAL
    // ==========================================
    function showAddMoreProductModal() {

        const modalElement =
            document.getElementById("addMoreProductModal");

        if (!modalElement) {
            console.error(
                "addMoreProductModal element was not found."
            );

            // Modal না পাওয়া গেলে fallback হিসেবে
            // Product Search open হবে।
            openProductSearch();
            return;
        }

        if (
            typeof bootstrap === "undefined" ||
            !bootstrap.Modal
        ) {
            console.error(
                "Bootstrap Modal JavaScript is not loaded."
            );

            openProductSearch();
            return;
        }

        let addMoreModal =
            bootstrap.Modal.getInstance(modalElement);

        if (!addMoreModal) {
            addMoreModal = new bootstrap.Modal(
                modalElement,
                {
                    backdrop: "static",
                    keyboard: false
                }
            );
        }

        addMoreModal.show();

        /*
        * Modal সম্পূর্ণ show হওয়ার পর
        * Yes button-এ focus থাকবে।
        */
        $(modalElement)
            .off("shown.bs.modal.addMoreProduct")
            .on(
                "shown.bs.modal.addMoreProduct",
                function () {
                    $("#addMoreYesBtn").focus();
                }
            );
    }

    // ==========================================
// ADD MORE MODAL BUTTON EVENTS
// ==========================================

// YES → Product Search open
// YES → Modal close হওয়ার পর Product Search open
$("#addMoreYesBtn")
    .off("click.addMoreProduct")
    .on("click.addMoreProduct", function () {

        const modalElement =
            document.getElementById("addMoreProductModal");

        if (!modalElement) {
            return;
        }

        const addMoreModal =
            bootstrap.Modal.getInstance(modalElement);

        /*
         * Event আগে register করতে হবে,
         * তারপর modal hide করতে হবে।
         */
        $(modalElement)
            .off("hidden.bs.modal.addMoreYes")
            .one(
                "hidden.bs.modal.addMoreYes",
                function () {

                    /*
                     * Bootstrap যেন Add button-এ focus
                     * ফেরত নিতে না পারে।
                     */
                    if (document.activeElement) {
                        document.activeElement.blur();
                    }

                    /*
                     * Modal transition এবং focus restore
                     * সম্পূর্ণ শেষ হওয়ার পরে Select2 open।
                     */
                    setTimeout(function () {

                        if (!$("#productSearch").data("select2")) {
                            console.error(
                                "Product Select2 is not initialized."
                            );
                            return;
                        }

                        $("#productSearch").select2("open");

                        setTimeout(function () {

                            const searchField =
                                document.querySelector(
                                    ".select2-container--open " +
                                    ".select2-search__field"
                                );

                            if (searchField) {
                                searchField.focus();
                                searchField.select();
                            }

                        }, 150);

                    }, 250);
                }
            );

        if (addMoreModal) {
            addMoreModal.hide();
        }
    });


// NO → Advance field focus
$("#addMoreNoBtn")
    .off("click.addMoreProduct")
    .on("click.addMoreProduct", function () {

        const modalElement =
            document.getElementById(
                "addMoreProductModal"
            );

        const addMoreModal =
            bootstrap.Modal.getInstance(
                modalElement
            );

        if (addMoreModal) {
            addMoreModal.hide();
        }

        /*
         * Modal পুরোপুরি close হওয়ার পর
         * Advance field-এ focus যাবে।
         */
        $(modalElement)
            .off("hidden.bs.modal.addMoreNo")
            .one(
                "hidden.bs.modal.addMoreNo",
                function () {

                    $("#advanced")
                        .focus()
                        .select();
                }
            );
    });

    $("#addMoreYesBtn, #addMoreNoBtn")
    .off("keydown.addMoreNavigation")
    .on("keydown.addMoreNavigation", function (e) {

        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") {
            return;
        }

        e.preventDefault();

        const currentId = $(this).attr("id");

        if (currentId === "addMoreYesBtn") {
            $("#addMoreNoBtn").focus();
        } else {
            $("#addMoreYesBtn").focus();
        }
    });

// =========================
// ADVANCE → SAVE BUTTON FOCUS
// =========================
$("#advanced")
    .off("keydown.advanceToSave")
    .on("keydown.advanceToSave", function (e) {

        if (e.key !== "Enter") {
            return;
        }

        e.preventDefault();

        $("#saveAllBtn").focus();
    });


// =========================
// SHOW SAVE CONFIRM MODAL
// =========================
function showSaveTransactionConfirmModal() {

    const modalElement =
        document.getElementById("saveTransactionConfirmModal");

    if (!modalElement) {
        console.error("saveTransactionConfirmModal not found.");
        return;
    }

    let confirmModal =
        bootstrap.Modal.getInstance(modalElement);

    if (!confirmModal) {
        confirmModal = new bootstrap.Modal(
            modalElement,
            {
                backdrop: "static",
                keyboard: false,
                focus: true
            }
        );
    }

    $(modalElement)
        .off("shown.bs.modal.saveConfirm")
        .one("shown.bs.modal.saveConfirm", function () {
            $("#saveConfirmYesBtn").focus();
        });

    confirmModal.show();
}


// =========================
// SAVE BUTTON → CONFIRM MODAL
// =========================
$("#saveAllBtn")
    .off("click.saveConfirm")
    .on("click.saveConfirm", function (e) {

        e.preventDefault();

        showSaveTransactionConfirmModal();
    });


// =========================
// ACTUAL SAVE TRANSACTION
// =========================
function saveTransaction() {

    let paymentList = [];

    $("#selectedPaymentListPayment tr").each(function () {

        let row = $(this);

        let expiryDate =
            (row.find("td:eq(6)").text() || "").trim();

        if (!expiryDate) {
            expiryDate = null;
        }

        paymentList.push([
            row.data("product-id"),
            parseFloat(row.find("td:eq(3)").text()) || 0,
            parseFloat(row.find("td:eq(4)").text()) || 0,
            parseFloat(row.find("td:eq(5)").text()) || 0,
            expiryDate,
            parseFloat(row.find("td:eq(7)").text()) || 0
        ]);
    });

    if (!paymentList.length) {
        alert("No products selected!");
        return;
    }

    let receive =
        parseFloat($("#advanced").val()) || 0;

    let net_amount =
        parseFloat($("#netAmount").val()) || 0;

    let selectedUserText =
        $("#transaction_with_user option:selected").text();

    let selectedUserId =
        $("#transaction_with_user").val();

    if (receive > net_amount) {

        alert(
            "⚠️ Invalid Receive/Advance Amount! " +
            "It cannot exceed Net Amount."
        );

        $("#advanced").focus().select();
        return;
    }

    let tranTypeWith =
        $("#transaction_with").val() ||
        $("#self_transaction_with").val();

    if (!tranTypeWith) {
        alert(
            "⚠️ Please select Transaction With or Self Transaction!"
        );
        return;
    }

    let payload = {

        edit_id: window.EDIT_PAYMENT_DATA?.is_edit ? window.EDIT_PAYMENT_DATA.transaction?.id : null, // codex change

        store:
            parseInt($(".store-select").val()) || null,

        location:
            parseInt($(".location-select").val()) || null,

        supplier: selectedUserId,
        user_name: selectedUserText,

        tran_type_with:
            parseInt($("#transaction_with").val()) || null,

        tran_type: 10,
        tran_method: "receive",

        invoice:
            $("#paymentinvoice").val(),

        payment_method:
            $("#payment_method").val(),

        bill_amount:
            parseFloat($("#invoiceAmount").val()) || 0,

        discount:
            parseFloat($("#discount").val()) || 0,

        net_amount:
            parseFloat($("#netAmount").val()) || 0,

        receive: 0,

        payment:
            parseFloat($("#advanced").val()) || 0,

        due:
            parseFloat($("#balance").val()) || 0,

        tran_date:
            $("#tranDate").val(),

        products:
            paymentList,

        patient_title:
            $("#pat_title").val(),

        patient_name:
            $("#pat_name").val().trim(),

        patient_age_y:
            parseInt($("#pat_age_y").val()) || 0,

        patient_age_m:
            parseInt($("#pat_age_m").val()) || 0,

        patient_age_d:
            parseInt($("#pat_age_d").val()) || 0,

        patient_gender:
            $("#pat_gender").val(),

        patient_phone:
            $("#pat_phone").val().trim(),

        patient_address:
            $("#pat_address").val().trim(),

        patient_id:
            (
                $("#patient_lookup").val() ||
                $("#patient_id").val() ||
                window.EDIT_PAYMENT_DATA?.transaction?.patient_id || // codex change
                ""
            ).toString().trim() || null,

        referred_doctor_id:
            (
                $("#doc_id").val() ||
                $("#doc_lookup").val() ||
                ""
            ).toString().trim() || null,

        referred_sr_id:
            (
                $("#sr_id").val() ||
                $("#sr_lookup").val() ||
                ""
            ).toString().trim() || null
    };

    $("#saveAllBtn").prop("disabled", true);
    $("#saveConfirmYesBtn").prop("disabled", true);

    $.ajax({
        url: "/diagnosis/payment/save-payment/",
        type: "POST",

        headers: {
            "X-CSRFToken": csrftoken
        },

        contentType: "application/json",
        data: JSON.stringify(payload),

        success: function (response) {

            console.log("SAVE RESPONSE:", response);

            $("#saveAllBtn").prop("disabled", false);
            $("#saveConfirmYesBtn").prop("disabled", false);

            if (!response.success) {

                alert(
                    response.message ||
                    response.error ||
                    "Save failed!"
                );

                return;
            }

            showTransactionPreview(
                response,
                payload,
                paymentList
            );

            $("#selectedPaymentListPayment").empty();

            $("#invoiceAmount").val("0");
            $("#discount").val("0");
            $("#netAmount").val("0");
            $("#advanced").val("0");
            $("#balance").val("0");

            $("#productid").val("");

            $("#productSearch")
                .val(null)
                .trigger("change");

            $("#quantity").val("1");
            $("#cp").val("0");
            $("#mrp").val("0");
            $("#total").val("");
        },

        error: function (xhr) {

    $("#saveAllBtn").prop("disabled", false);
    $("#saveConfirmYesBtn").prop("disabled", false);

    console.error(
        xhr.status,
        xhr.responseText
    );

    let errorMessage = "Save failed! Please try again.";

    /*
     * Backend JSON response থেকে message নেওয়া
     */
    if (xhr.responseJSON) {
        errorMessage =
            xhr.responseJSON.message ||
            xhr.responseJSON.error ||
            errorMessage;
    } else if (xhr.responseText) {
        try {
            const response = JSON.parse(xhr.responseText);

            errorMessage =
                response.message ||
                response.error ||
                errorMessage;
        } catch (error) {
            console.error(
                "Invalid error response:",
                error
            );
        }
    }

    alert(errorMessage);

    /*
     * Doctor validation error হলে
     * doctor search আবার open হবে
     */
    if (
        errorMessage
            .toLowerCase()
            .includes("doctor")
    ) {
        $("#doc_id").val("");

        $("#doc_lookup")
            .val(null)
            .trigger("change");

        setTimeout(function () {

            $("#doc_lookup").select2("open");

            setTimeout(function () {

                $(".select2-container--open .select2-search__field")
                    .focus()
                    .select();

            }, 100);

        }, 150);

        return;
    }

    /*
     * অন্য validation error হলে
     * Save button-এ focus থাকবে
     */
    $("#saveAllBtn").focus();
}
    });
}


// =========================
// SAVE CONFIRM YES
// =========================
$("#saveConfirmYesBtn")
    .off("click.saveTransaction")
    .on("click.saveTransaction", function () {

        const modalElement =
            document.getElementById(
                "saveTransactionConfirmModal"
            );

        const confirmModal =
            bootstrap.Modal.getInstance(modalElement);

        $(modalElement)
            .off("hidden.bs.modal.saveYes")
            .one("hidden.bs.modal.saveYes", function () {

                saveTransaction();
            });

        if (confirmModal) {
            confirmModal.hide();
        }
    });


// =========================
// SAVE CONFIRM NO
// =========================
$("#saveConfirmNoBtn")
    .off("click.saveTransaction")
    .on("click.saveTransaction", function () {

        const modalElement =
            document.getElementById(
                "saveTransactionConfirmModal"
            );

        const confirmModal =
            bootstrap.Modal.getInstance(modalElement);

        $(modalElement)
            .off("hidden.bs.modal.saveNo")
            .one("hidden.bs.modal.saveNo", function () {

                // Page-এই থাকবে এবং Save button focus হবে
                $("#saveAllBtn").focus();
            });

        if (confirmModal) {
            confirmModal.hide();
        }
    });


// =========================
// SAVE MODAL ARROW NAVIGATION
// =========================
$("#saveConfirmYesBtn, #saveConfirmNoBtn")
    .off("keydown.saveConfirmNavigation")
    .on("keydown.saveConfirmNavigation", function (e) {

        if (
            e.key !== "ArrowRight" &&
            e.key !== "ArrowLeft"
        ) {
            return;
        }

        e.preventDefault();

        if ($(this).attr("id") === "saveConfirmYesBtn") {
            $("#saveConfirmNoBtn").focus();
        } else {
            $("#saveConfirmYesBtn").focus();
        }
    });
    

    // =========================
    // PRICE × QTY CALCULATION
    // =========================
    $("#quantity, #mrp").on("input", function () {
        updateProductTotal();
    });

    // =========================
    // ADD TO SELECTED LIST
    // =========================
    function addToSelectedList(productId, pname, qty, cp, mrp, expiry, total) {

        let row = `
            <tr data-product-id="${productId}">

                <td>${$("#selectedPaymentListPayment tr").length + 1}</td>

                <td style="display:none;">
                    ${productId}
                </td>

                <td>${pname}</td>

                <td>${qty}</td>

                <td>${cp}</td>

                <td style="display:none;">
                    ${mrp}
                </td>

                <td style="display:none;">
                    ${expiry}
                </td>

                <td>${total}</td>

                <td>
                    <button type="button" class="btn btn-sm btn-primary edit-item">
                        Edit
                    </button>

                    <button type="button" class="btn btn-sm btn-danger remove-item">
                        Remove
                    </button>
                </td>

            </tr>
        `;

        $("#selectedPaymentListPayment").append(row);

        $("#productid").val("");
        $("#productSearch").val(null).trigger("change");
        $("#cp").val("");
        $("#mrp").val("");
        $("#quantity").val("");
        $("#total").val("");

        updateInvoiceSummary();
    }

    function appendEditProductRow(item) { // codex change
        let productId = item.product_id || ""; // codex change
        let name = item.product_name || productId; // codex change
        let qty = parseFloat(item.quantity) || 0; // codex change
        let cp = parseFloat(item.cp) || 0; // codex change
        let mrp = parseFloat(item.mrp) || 0; // codex change
        let expiry = item.expiry_date || ""; // codex change
        let total = parseFloat(item.total) || 0; // codex change

        let row = ` // codex change
            <tr data-product-id="${productId}"> <!-- codex change -->
                <td>${$("#selectedPaymentListPayment tr").length + 1}</td> <!-- codex change -->
                <td style="display:none;">${productId}</td> <!-- codex change -->
                <td>${name}</td> <!-- codex change -->
                <td>${qty}</td> <!-- codex change -->
                <td>${cp}</td> <!-- codex change -->
                <td style="display:none;">${mrp}</td> <!-- codex change -->
                <td style="display:none;">${expiry}</td> <!-- codex change -->
                <td>${total}</td> <!-- codex change -->
                <td> <!-- codex change -->
                    <button type="button" class="btn btn-sm btn-primary edit-item">Edit</button> <!-- codex change -->
                    <button type="button" class="btn btn-sm btn-danger remove-item">Remove</button> <!-- codex change -->
                </td> <!-- codex change -->
            </tr> <!-- codex change -->
        `; // codex change

        $("#selectedPaymentListPayment").append(row); // codex change
    } // codex change

    // =========================
    // EDIT ITEM
    // =========================
    $(document).on("click", ".edit-item", function () {

        let row = $(this).closest("tr");

        let productId = row.find("td:eq(1)").text().trim();
        let name = row.find("td:eq(2)").text().trim();
        let qty = row.find("td:eq(3)").text().trim();
        let cp = row.find("td:eq(4)").text().trim();
        let mrp = row.find("td:eq(5)").text().trim();
        let expiry = row.find("td:eq(6)").text().trim();

        $("#productid").val(productId);

        let productOption = new Option(
            name,
            productId,
            true,
            true
        );

        $("#productSearch")
            .append(productOption)
            .trigger("change");

        $("#quantity").val(qty);
        $("#cp").val(cp);
        $("#mrp").val(mrp);
        $("#expiryDate").val(expiry);
        $("#total").val(
            (
                (parseFloat(qty) || 0) *
                (parseFloat(mrp) || 0)
            ).toFixed(2)
        );

        $("#addProductBtn").data("editRow", row);
    });

    function clearInputs() {
        $("#productid").val("");
        $("#productSearch").val(null).trigger("change");
        $("#cp").val("0");
        $("#mrp").val("0");
        $("#quantity").val("1");
        $("#total").val("");

        if ($("#expiryDate").length) {
            $("#expiryDate").val("");
        }
    }

    function updateSerial() {
        $("#selectedPaymentListPayment tr").each(function (index) {
            $(this).find("td:eq(0)").text(index + 1);
        });
    }

    // =========================
    // REMOVE ITEM
    // =========================
    $(document).on("click", ".remove-item", function () {

        if (
            confirm(
                "Are you sure to remove:\n\n" +
                $(this).closest("tr").find("td:eq(2)").text() +
                " ?"
            )
        ) {
            $(this).closest("tr").remove();
        }

        $("#selectedPaymentListPayment tr").each(function (index) {
            $(this).find("td:first").text(index + 1);
        });

        focusProductBoxOnly();
        updateSerial();
        updateInvoiceSummary();
    });

    // =========================
    // INVOICE SUMMARY
    // =========================
    function updateInvoiceSummary() {
        let invoiceAmount = 0;

        $("#selectedPaymentListPayment tr").each(function () {
            let rowTotal =
                parseFloat($(this).find("td:eq(7)").text()) || 0;

            invoiceAmount += rowTotal;
        });

        let discountPercent = parseFloat($("#discount").val()) || 0;
        let advance = parseFloat($("#advanced").val()) || 0;

        let discountAmount =
            (invoiceAmount * discountPercent) / 100;

        let netAmount = invoiceAmount - discountAmount;

        if (netAmount < 0) {
            netAmount = 0;
        }

        let balance = netAmount - advance;

        if (balance < 0) {
            balance = 0;
        }

        $("#invoiceAmount").val(invoiceAmount.toFixed(2));
        $("#netAmount").val(netAmount.toFixed(2));
        $("#balance").val(balance.toFixed(2));
    }

    function updateGrandTotal() {
        let total = 0;

        $("#selectedPaymentListPayment tr").each(function () {
            let rowTotal =
                parseFloat($(this).find(".item-total").text()) || 0;

            total += rowTotal;
        });

        $("#grandTotal").text(total.toFixed(2));
    }

    $("#discount, #advanced").on("input", function () {
        updateInvoiceSummary();
    });

    function setSelect2Option(selector, value, text) { // codex change
        if (!value) { // codex change
            return; // codex change
        } // codex change

        let label = text || value; // codex change
        let option = new Option(label, value, true, true); // codex change
        $(selector).append(option).trigger("change"); // codex change
    } // codex change

    function initEditPaymentForm() { // codex change
        let editData = window.EDIT_PAYMENT_DATA || {}; // codex change

        if (!editData.is_edit || !editData.transaction) { // codex change
            return; // codex change
        } // codex change

        let transaction = editData.transaction; // codex change
        let details = editData.details || []; // codex change

        $(".card-header h5").text("Edit Payment"); // codex change
        $("#saveAllBtn").text("Update"); // codex change

        $("#tranDate").val(transaction.tran_date || ""); // codex change
        $("#paymentinvoice").val(transaction.invoice_ref || transaction.tran_id || ""); // codex change
        $("#payment_method").val(transaction.tran_method || "cash"); // codex change
        $(".location-select").val(transaction.loc_id || "").trigger("change"); // codex change
        $(".store-select").val(transaction.store_id || ""); // codex change

        $("#pat_title").val(transaction.patient_title || $("#pat_title").val()); // codex change
        $("#pat_name").val(transaction.patient_name || ""); // codex change
        $("#pat_age_y").val(transaction.patient_age_y || 0); // codex change
        $("#pat_age_m").val(transaction.patient_age_m || 0); // codex change
        $("#pat_age_d").val(transaction.patient_age_d || 0); // codex change
        $("#pat_gender").val(transaction.patient_gender || "Male"); // codex change
        $("#pat_phone").val(transaction.patient_phone || ""); // codex change
        $("#pat_address").val(transaction.patient_address || ""); // codex change
        $("#patient_id").val(transaction.patient_id || ""); // codex change

        $("#doc_id").val(transaction.doctor_id || ""); // codex change
        $("#doc_speciality").val(transaction.doctor_speciality || ""); // codex change
        $("#doc_chamber").val(transaction.doctor_chamber || ""); // codex change
        setSelect2Option("#doc_lookup", transaction.doctor_id, transaction.doctor_name); // codex change

        $("#sr_id").val(transaction.sr_id || ""); // codex change
        $("#sr_name_display").val(transaction.sr_name || ""); // codex change
        setSelect2Option("#sr_lookup", transaction.sr_id, transaction.sr_name); // codex change

        $("#invoiceAmount").val(parseFloat(transaction.bill_amount || 0).toFixed(2)); // codex change
        $("#discount").val(transaction.discount || 0); // codex change
        $("#netAmount").val(parseFloat(transaction.net_amount || 0).toFixed(2)); // codex change
        $("#advanced").val(transaction.payment || 0); // codex change
        $("#balance").val(parseFloat(transaction.due || 0).toFixed(2)); // codex change

        $("#selectedPaymentListPayment").empty(); // codex change
        details.forEach(function (item) { // codex change
            appendEditProductRow(item); // codex change
        }); // codex change

        if (typeof loadTransactionMainHeadsCombo === "function") { // codex change
            loadTransactionMainHeadsCombo(transaction.tran_type || 0, function () { // codex change
                $("#transactionmainheads").val(transaction.tran_type || ""); // codex change

                if (typeof loadTransactionMethodsCombo === "function") { // codex change
                    loadTransactionMethodsCombo(transaction.tran_group_method || 0, function () { // codex change
                        if (typeof loadTransactionGroupCombo === "function") { // codex change
                            loadTransactionGroupCombo(transaction.tran_group_id || 0, function () { // codex change
                                $("#tran_group").val(transaction.tran_group_id || ""); // codex change
                            }); // codex change
                        } // codex change
                    }); // codex change
                } // codex change

                if (typeof loadTransactionWithMethodsCombo === "function") { // codex change
                    loadTransactionWithMethodsCombo(transaction.tran_with_method || 0, function () { // codex change
                        if (typeof loadTransactionWithCombo === "function") { // codex change
                            loadTransactionWithCombo(transaction.tran_type_with || 0, function () { // codex change
                                if (typeof loadTransactionWithUserCombo === "function") { // codex change
                                    loadTransactionWithUserCombo(transaction.tran_user || 0); // codex change
                                } // codex change
                            }); // codex change
                        } // codex change
                    }); // codex change
                } // codex change
            }); // codex change
        } // codex change

        updateInvoiceSummary(); // codex change
    } // codex change

    setTimeout(initEditPaymentForm, 500); // codex change

$(document)
    .off("keydown.optionalSr", ".select2-search__field")
    .on("keydown.optionalSr", ".select2-search__field", function (e) {

        if (e.key !== "Enter") {
            return;
        }

        const $srLookup = $("#sr_lookup");

        if (!$srLookup.length || !$srLookup.data("select2")) {
            return;
        }

        const srSelect2 = $srLookup.data("select2");

        if (!srSelect2.isOpen()) {
            return;
        }

        if ($srLookup.val()) {
            return;
        }

        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();

        $srLookup.select2("close");

        setTimeout(function () {
            $("#productSearch").select2("open");

            setTimeout(function () {
                $(".select2-container--open .select2-search__field")
                    .focus()
                    .select();
            }, 100);
        }, 100);
    });

// =========================
// CSRF TOKEN
// =========================
function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (
                cookie.substring(0, name.length + 1) ===
                (name + "=")
            ) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }

    return cookieValue;
}

const csrftoken = getCookie("csrftoken");

// =========================
// TRANSACTION PREVIEW
// =========================
function showTransactionPreview(response, payload, paymentList) {

    lastSavedTransactionId = response.tran_id || null;

    function selectedText(selector) {
        const $element = $(selector);

        if (!$element.length) {
            return "-";
        }

        const text = $element.find("option:selected").text();

        if (!text || !text.trim()) {
            return "-";
        }

        return text.trim();
    }

    function safeText(value) {
        if (
            value === null ||
            value === undefined ||
            value === ""
        ) {
            return "-";
        }

        return value;
    }

    function money(value) {
        const amount = parseFloat(value) || 0;
        return amount.toFixed(2);
    }

    $("#previewTranId").text(
        safeText(response.tran_id)
    );

    $("#previewTranIdText").text(
        "Transaction ID: " + safeText(response.tran_id)
    );

    $("#previewTranDate").text(
        safeText(payload.tran_date)
    );

    $("#previewMainHead").text(
        selectedText("#transactionmainheads")
    );

    $("#previewTransactionMethod").text(
        selectedText("#transaction_method")
    );

    $("#previewTransactionGroup").text(
        selectedText("#tran_group")
    );

    $("#previewTransactionWithMethod").text(
        selectedText("#transaction_with_method")
    );

    $("#previewTransactionWith").text(
        selectedText("#transaction_with")
    );

    $("#previewTransactionUser").text(
        selectedText("#transaction_with_user")
    );

    $("#previewPaymentMethod").text(
        selectedText("#payment_method")
    );

    $("#previewInvoiceNo").text(
        safeText(payload.invoice)
    );

    $("#previewLocation").text(
        selectedText(".location-select")
    );

    $("#previewPatientId").text(
        safeText(response.patient_id)
    );

    $("#previewPatientName").text(
        safeText(payload.patient_name)
    );

    const ageY = parseInt(payload.patient_age_y) || 0;
    const ageM = parseInt(payload.patient_age_m) || 0;
    const ageD = parseInt(payload.patient_age_d) || 0;

    $("#previewPatientAge").text(
        ageY + "Y - " +
        ageM + "M - " +
        ageD + "D"
    );

    $("#previewPatientGender").text(
        safeText(payload.patient_gender)
    );

    $("#previewPatientPhone").text(
        safeText(payload.patient_phone)
    );

    $("#previewPatientAddress").text(
        safeText(payload.patient_address)
    );

    $("#previewDoctorId").text(
        safeText(response.doctor_id)
    );

    $("#previewDoctorName").text(
        selectedText("#doc_lookup")
    );

    $("#previewDoctorSpeciality").text(
        safeText($("#doc_speciality").val())
    );

    $("#previewDoctorChamber").text(
        safeText($("#doc_chamber").val())
    );

    $("#previewSrId").text(
        safeText(response.sr_id)
    );

    let srName = $("#sr_name_display").val();

    if (!srName || !srName.trim()) {
        srName = selectedText("#sr_lookup");
    }

    $("#previewSrName").text(
        safeText(srName)
    );

    let rowsHtml = "";

    $("#selectedPaymentListPayment tr").each(function (index) {

        const $row = $(this);

        const productId =
            $row.data("product-id") || "-";

        const productName =
            ($row.find("td:eq(2)").text() || "-").trim();

        const qty =
            parseFloat($row.find("td:eq(3)").text()) || 0;

        const mrp =
            parseFloat($row.find("td:eq(5)").text()) || 0;

        const total =
            parseFloat($row.find("td:eq(7)").text()) || 0;

        rowsHtml += `
            <tr>
                <td>${index + 1}</td>
                <td>${productId}</td>
                <td>${productName}</td>
                <td class="text-center">${qty}</td>
                <td class="text-end">${mrp.toFixed(2)}</td>
                <td class="text-end fw-semibold">${total.toFixed(2)}</td>
            </tr>
        `;
    });

    if (!rowsHtml) {
        rowsHtml = `
            <tr>
                <td colspan="6" class="text-center text-muted py-3">
                    No transaction details found
                </td>
            </tr>
        `;
    }

    $("#previewTransactionRows").html(rowsHtml);

    $("#previewBottomTranId").text(
        safeText(response.tran_id)
    );

    $("#previewBottomPatientName").text(
        safeText(payload.patient_name)
    );

    $("#previewBottomDoctorName").text(
        selectedText("#doc_lookup")
    );

    $("#previewInvoiceAmount").text(
        money(payload.bill_amount)
    );

    $("#previewDiscount").text(
        money(payload.discount)
    );

    $("#previewNetAmount").text(
        money(payload.net_amount)
    );

    $("#previewAdvance").text(
        money(payload.payment)
    );

    $("#previewBalance").text(
        money(payload.due)
    );

    const modalElement =
        document.getElementById("transactionPreviewModal");

    if (!modalElement) {
        console.error("❌ transactionPreviewModal not found");
        return;
    }

    if (
        typeof bootstrap === "undefined" ||
        !bootstrap.Modal
    ) {
        console.error("❌ Bootstrap Modal JS is not loaded");
        return;
    }

    let previewModal =
        bootstrap.Modal.getInstance(modalElement);

    if (!previewModal) {
        previewModal =
            new bootstrap.Modal(modalElement);
    }

    previewModal.show();
}
