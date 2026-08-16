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
            openProductSearch();
        }, 100);
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

// =========================
// SAVE ALL
// =========================
$("#saveAllBtn").on("click", function (e) {
    e.preventDefault();

    let paymentList = [];

    $("#selectedPaymentListPayment tr").each(function () {
        let row = $(this);

        let expiryDate = (row.find("td:eq(6)").text() || "").trim();

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

    let receive = parseFloat($("#advanced").val()) || 0;
    let net_amount = parseFloat($("#netAmount").val()) || 0;

    let selectedUserText =
        $("#transaction_with_user option:selected").text();

    let selectedUserId =
        $("#transaction_with_user").val();

    if (receive > net_amount) {
        alert("⚠️ Invalid Receive/Advance Amount! It cannot exceed Net Amount.");
        $("#advanced").focus().select();
        return;
    }

    let tranTypeWith =
        $("#transaction_with").val() ||
        $("#self_transaction_with").val();

    if (!tranTypeWith) {
        alert("⚠️ Please select Transaction With or Self Transaction!");
        return;
    }

    let payload = {
        store: parseInt($(".store-select").val()) || null,
        location: parseInt($(".location-select").val()) || null,

        supplier: selectedUserId,
        user_name: selectedUserText,

        tran_type_with: parseInt($("#transaction_with").val()) || null,
        tran_type: 10,
        tran_method: "receive",

        invoice: $("#paymentinvoice").val(),
        payment_method: $("#payment_method").val(),

        bill_amount: parseFloat($("#invoiceAmount").val()) || 0,
        discount: parseFloat($("#discount").val()) || 0,
        net_amount: parseFloat($("#netAmount").val()) || 0,

        receive: 0,
        payment: parseFloat($("#advanced").val()) || 0,
        due: parseFloat($("#balance").val()) || 0,

        tran_date: $("#tranDate").val(),

        products: paymentList,

        patient_title: $("#pat_title").val(),
        patient_name: $("#pat_name").val().trim(),

        patient_age_y: parseInt($("#pat_age_y").val()) || 0,
        patient_age_m: parseInt($("#pat_age_m").val()) || 0,
        patient_age_d: parseInt($("#pat_age_d").val()) || 0,

        patient_gender: $("#pat_gender").val(),
        patient_phone: $("#pat_phone").val().trim(),
        patient_address: $("#pat_address").val().trim(),

        patient_id:
            (
                $("#patient_lookup").val() ||
                $("#patient_id").val() ||
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
            $("#productSearch").val(null).trigger("change");
            $("#quantity").val("1");
            $("#cp").val("0");
            $("#mrp").val("0");
            $("#total").val("");

            setTimeout(function () {
                openProductSearch();
            }, 500);
        },

        error: function (xhr) {
            console.error(xhr.status, xhr.responseText);
            alert("Save failed! Check console for error.");
        }
    });
});


