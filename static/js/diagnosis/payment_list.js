$(document).ready(function () {

    // =========================
    // STATE
    // =========================
    let selectedMainHead = "10"; // codex change
    let selectedDoctor = ""; // codex change
    let selectedSr = ""; // codex change
    let selectedPatient = ""; // codex change
    let selectedTranBy = ""; // codex change
    let paymentList = [];

    let offset = 0;
    let limit = 50;
    let hasMore = true;
    let isLoading = false;
    let currentRequest = null;
    let query = "";

    // =========================
    // INIT DATE
    // =========================
    function setTodayDate() {
        if ($("#start_date").val() || $("#end_date").val()) {
            return;
        }

        const today = new Date();

        const date =
            today.getFullYear() + "-" +
            String(today.getMonth() + 1).padStart(2, "0") + "-" +
            String(today.getDate()).padStart(2, "0");

        $("#start_date").val(date);
        $("#end_date").val(date);
    }

    // =========================
    // MONEY FORMAT
    // =========================
    function money(value) {
        let amount = parseFloat(value) || 0;
        return amount.toFixed(2);
    }

    function loadDiagnosisFilterCombo(selector, url, label) { // codex change
        $.ajax({ // codex change
            url: url, // codex change
            method: "GET", // codex change
            success: function (res) { // codex change
                let $select = $(selector); // codex change
                $select.empty(); // codex change
                $select.append(`<option value="">${label}</option>`); // codex change
                (res.results || []).forEach(function (item) { // codex change
                    $select.append(`<option value="${item.id}">${item.name}</option>`); // codex change
                }); // codex change
            }, // codex change
            error: function (xhr) { // codex change
                console.error(xhr.status, xhr.responseText); // codex change
            } // codex change
        }); // codex change
    } // codex change

    // =========================
    // LOAD TABLE
    // =========================
    function loadTable(newOffset = 0, append = false) {

        if (isLoading) return;

        if (currentRequest) {
            currentRequest.abort();
        }

        isLoading = true;

        let params = new URLSearchParams();
        selectedMainHead = $("#transactionmainheads").val() || "10"; // codex change
        selectedDoctor = $("#doctor_filter").val() || ""; // codex change
        selectedSr = $("#sr_filter").val() || ""; // codex change
        selectedPatient = $("#patient_filter").val() || ""; // codex change
        selectedTranBy = $("#tran_by_filter").val() || ""; // codex change

        // COMBO FILTERS
        if (selectedMainHead) {
            params.append("transactionmainheads", selectedMainHead);
        }

        if (selectedDoctor) { // codex change
            params.append("doctor_id", selectedDoctor); // codex change
        }

        if (selectedSr) { // codex change
            params.append("sr_id", selectedSr); // codex change
        }

        if (selectedPatient) { // codex change
            params.append("patient_id", selectedPatient); // codex change
        }

        if (selectedTranBy) { // codex change
            params.append("tran_by", selectedTranBy); // codex change
        }

        // OLD FILTERS
        query = ""; // codex change

        if (query) {
            params.append("q", query);
        }

        let status = $("#status").val();

        if (status) {
            params.append("status", status);
        }

        let start_date = $("#start_date").val();
        let end_date = $("#end_date").val();

        if (start_date) {
            params.append("start_date", start_date);
        }

        if (end_date) {
            params.append("end_date", end_date);
        }

        limit = parseInt($("#perPage").val()) || 50;

        params.append("offset", newOffset);
        params.append("limit", limit);

        currentRequest = $.ajax({
            url: window.APP_URLS.PAYMENT_LIST_URL,
            method: "GET",
            data: params.toString(),

            success: function (res) {

                const fetched = res.results || [];

                if (append) {
                    paymentList = paymentList.concat(fetched);
                } else {
                    paymentList = fetched;
                }

                offset = newOffset;
                hasMore = fetched.length === limit;

                renderTable();

                $("#total_due").val(
                    money(res.total_due || calculateTotalDue())
                );

                isLoading = false;
            },

            error: function (xhr) {
                console.error(xhr.status, xhr.responseText);
                isLoading = false;
            }
        });
    }

    // =========================
    // CALCULATE TOTAL DUE
    // =========================
    function calculateTotalDue() {
        let totalDue = 0;

        paymentList.forEach(function (item) {
            totalDue += parseFloat(item.due) || 0;
        });

        return totalDue;
    }

    // =========================
    // RENDER TABLE
    // =========================
    function renderTable() {

        let html = "";

        if (!paymentList.length) {
            html = `
                <tr>
                    <td colspan="17" class="text-center text-muted py-3"> <!-- codex change -->
                        No payment data found
                    </td>
                </tr>
            `;

            $("#paymentListTableBody").html(html);
            return;
        }

        paymentList.forEach(function (item, index) {

            html += `
                <tr>
                    <td>${index + 1}</td>

                    <td>${item.tran_id || ""}</td>

                    <td>${item.invoice_ref || item.invoice || "-"}</td>

                    <td>${item.tran_date || ""}</td>

                    <td>${item.supplier_name || item.tran_type_with || "-"}</td>

                    <td>${item.doctor_name || "-"}</td> <!-- codex change -->

                    <td>${item.sr_name || "-"}</td> <!-- codex change -->

                    <td>${item.patient_name || item.user_name || item.tran_user || "-"}</td> <!-- codex change -->

                    <td>${item.tran_by || "-"}</td> <!-- codex change -->

                    <td class="text-end">${money(item.bill_total)}</td>

                    <td class="text-end">${money(item.discount)}</td>

                    <td class="text-end">${money(item.net_total)}</td>

                    <td class="text-end">${money(item.advance)}</td>

                    <td class="text-end">${money(item.due_collection)}</td>

                    <td class="text-end">${money(item.due_discount)}</td>

                    <td class="text-end">${money(item.due)}</td>

                    <td class="text-center">
                        <button
                            type="button"
                            class="btn btn-sm btn-primary ${window.IS_PARTY_PAYMENT_LIST ? "payment-btn" : "edit-payment-btn"}"
                            data-id="${item.id || ""}"
                            data-tran-id="${item.tran_id || ""}">
                            ${window.IS_PARTY_PAYMENT_LIST ? "Payment" : "Edit"} <!-- codex change -->
                        </button>
                    </td>
                </tr>
            `;
        });

        $("#paymentListTableBody").html(html);
    }

    // =========================
    // RESET + LOAD
    // =========================
    function resetAndLoad() {
        offset = 0;
        hasMore = true;
        loadTable(0, false);
    }

    // =========================
    // INIT
    // =========================
    setTodayDate(); // codex change

    $("#transactionmainheads").val("10"); // codex change
    loadDiagnosisFilterCombo("#doctor_filter", window.APP_URLS.DIAGNOSIS_DOCTOR_FILTER_URL, "All Doctor"); // codex change
    loadDiagnosisFilterCombo("#sr_filter", window.APP_URLS.DIAGNOSIS_SR_FILTER_URL, "All SR"); // codex change
    loadDiagnosisFilterCombo("#patient_filter", window.APP_URLS.DIAGNOSIS_PATIENT_FILTER_URL, "All Patient"); // codex change
    loadDiagnosisFilterCombo("#tran_by_filter", window.APP_URLS.DIAGNOSIS_TRAN_BY_FILTER_URL, "All Transaction By"); // codex change

    loadTable(0, false);

    // =========================
    // COMBO EVENTS
    // =========================
    $("#transactionmainheads").on("change", function () {
        selectedMainHead = this.value || "10"; // codex change
    });

    $("#doctor_filter").on("change", function () { // codex change
        selectedDoctor = this.value; // codex change
    });

    $("#sr_filter").on("change", function () { // codex change
        selectedSr = this.value; // codex change
    }); // codex change

    $("#patient_filter").on("change", function () { // codex change
        selectedPatient = this.value; // codex change
    });

    $("#tran_by_filter").on("change", function () { // codex change
        selectedTranBy = this.value; // codex change
    }); // codex change

    // =========================
    // OLD FILTER EVENTS
    // =========================
    $("#start_date, #end_date, #status, #perPage, #supplierSearch, #tran_by_filter").off("change input"); // codex change

    if ($("#supplierSearch").length) { // codex change
        $("#supplierSearch").on("keyup", function () { // codex change
            const incomingQuery = $(this).val().toLowerCase().trim(); // codex change
            $("#paymentListTableBody tr").filter(function () { // codex change
                $(this).toggle($(this).text().toLowerCase().indexOf(incomingQuery) > -1); // codex change
            }); // codex change
        }); // codex change
    } // codex change

    $("form").on("submit", function (e) {
        e.preventDefault();
        resetAndLoad(); // codex change
    });

    // =========================
    // SCROLL PAGINATION
    // =========================
    $(".table-responsive").on("scroll", function () {

        if (
            $(this).scrollTop() + $(this).innerHeight() >=
            this.scrollHeight - 10
        ) {
            if (hasMore && !isLoading) {
                offset += limit;
                loadTable(offset, true);
            }
        }
    });

        // =========================
    // EDIT BUTTON // codex change
    // =========================
    $(document).on("click", ".edit-payment-btn", function () { // codex change

        const id = $(this).data("id");

        if (id) {
            window.location.href =
                "/diagnosis/payment/edit/" + id + "/"; // codex change
            return;
        }
    });

    // =========================
    // PAYMENT BUTTON
    // =========================
    $(document).on("click", ".payment-btn", function () {

        const id = $(this).data("id");
        const tranId = $(this).data("tran-id");

        if (id) {
            window.location.href =
                (window.APP_URLS.PAYMENT_FORM_BASE_URL || "/diagnosis/payment-form/") + id + "/"; // codex change
            return;
        }

        if (tranId) {
            window.location.href =
                (window.APP_URLS.PAYMENT_FORM_BASE_URL || "/diagnosis/payment-form/") + tranId + "/"; // codex change
        }
    });

    // =========================
    // FIFO PAYMENT
    // =========================
    $("#fifo_pay_btn").on("click", function () {

        let amount = parseFloat($("#fifo_payment").val()) || 0;

        if (amount <= 0) {
            alert("Enter payment amount");
            return;
        }

        let ids = paymentList
            .map(function (x) {
                return x.id;
            })
            .filter(Boolean);

        if (!ids.length) {
            alert("No payable rows found");
            return;
        }

        $.ajax({
            url: window.APP_URLS.FIFO_PAYMENT_URL || "/diagnosis/party-payment/process-fifo-payment/", // codex change
            type: "POST",
            data: {
                payment: amount,
                ids: JSON.stringify(ids)
            },

            success: function (res) {

                if (!res.success) {
                    alert(res.error || "Payment failed");
                    return;
                }

                alert("Paid: " + res.paid);

                $("#fifo_payment").val("");
                resetAndLoad();
            },

            error: function (xhr) {
                console.error(xhr.status, xhr.responseText);
                alert("Payment failed! Check console.");
            }
        });
    });

    // =========================
    // PRINT REPORT
    // =========================
    $("#printReportBtn").on("click", function () {

        let params = new URLSearchParams();

        let q = $("#supplierSearch").val().trim();
        let start_date = $("#start_date").val();
        let end_date = $("#end_date").val();
        let status = $("#status").val();
        selectedMainHead = $("#transactionmainheads").val() || "10"; // codex change
        selectedDoctor = $("#doctor_filter").val() || ""; // codex change
        selectedSr = $("#sr_filter").val() || ""; // codex change
        selectedPatient = $("#patient_filter").val() || ""; // codex change
        selectedTranBy = $("#tran_by_filter").val() || ""; // codex change

        if (q) params.append("q", q);
        if (start_date) params.append("start_date", start_date);
        if (end_date) params.append("end_date", end_date);
        if (status) params.append("status", status);

        if (selectedMainHead) {
            params.append("transactionmainheads", selectedMainHead);
        }

        if (selectedDoctor) { // codex change
            params.append("doctor_id", selectedDoctor); // codex change
        }

        if (selectedSr) { // codex change
            params.append("sr_id", selectedSr); // codex change
        }

        if (selectedPatient) { // codex change
            params.append("patient_id", selectedPatient); // codex change
        }

        if (selectedTranBy) { // codex change
            params.append("tran_by", selectedTranBy); // codex change
        }

        let url =
            window.APP_URLS.PAYMENT_REPORT_URL +
            "?" +
            params.toString();

        window.open(url, "_blank");
    });

});
