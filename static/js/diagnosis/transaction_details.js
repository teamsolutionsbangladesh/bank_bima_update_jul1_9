$(document).ready(function () {

    // =========================
    // VARIABLES
    // =========================
    let detailsList = [];
    let offset = 0;
    let limit = 50;
    let hasMore = true;
    let isLoading = false;
    let currentRequest = null;

    // =========================
    // SET TODAY DATE
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

    // =========================
    // LOAD FILTER COMBO
    // =========================
    function loadDiagnosisFilterCombo(selector, url, label) {

        $.ajax({
            url: url,
            method: "GET",

            success: function (res) {

                let $select = $(selector);

                $select.empty();
                $select.append(`<option value="">${label}</option>`);

                (res.results || []).forEach(function (item) {
                    $select.append(
                        `<option value="${item.id}">${item.name}</option>`
                    );
                });
            },

            error: function (xhr) {
                console.error(xhr.status, xhr.responseText);
            }
        });
    }

    // =========================
    // GET LOCAL SEARCH RESULT
    // =========================
    function getFilteredDetailsList() {

        const searchText = (
            $("#productSearch").val() || ""
        ).toLowerCase().trim();

        if (!searchText) {
            return detailsList;
        }

        return detailsList.filter(function (item) {

            const searchableText = [
                item.tran_id,
                item.invoice_ref,
                item.tran_date,
                item.tran_head_id,
                item.tran_head_name,
                item.tran_type_with,
                item.doctor_name,
                item.doctor_id,
                item.sr_name,
                item.sr_id,
                item.patient_name,
                item.patient_id,
                item.tran_by,
                item.tot_amount,
                item.discount,
                item.amount,
                item.payment,
                item.due_col,
                item.due_disc,
                item.due
            ]
                .map(function (value) {
                    return value === null || value === undefined
                        ? ""
                        : String(value);
                })
                .join(" ")
                .toLowerCase();

            return searchableText.includes(searchText);
        });
    }

    // =========================
    // LOAD TRANSACTION DETAILS
    // =========================
    function loadTransactionDetails(
        newOffset = 0,
        append = false
    ) {

        if (isLoading) {
            return;
        }

        if (currentRequest) {
            currentRequest.abort();
        }

        isLoading = true;

        let params = new URLSearchParams();

        let selectedMainHead =
            $("#transactionmainheads").val() || "10";

        let selectedDoctor =
            $("#doctor_filter").val() || "";

        let selectedSr =
            $("#sr_filter").val() || "";

        let selectedPatient =
            $("#patient_filter").val() || "";

        let selectedTranBy =
            $("#tran_by_filter").val() || "";

        let status =
            $("#status").val() || "";

        let startDate =
            $("#start_date").val() || "";

        let endDate =
            $("#end_date").val() || "";

        limit =
            parseInt($("#perPage").val(), 10) || 50;

        /*
         * এখানে productSearch-এর q পাঠানো হচ্ছে না।
         * Search শুধু currently loaded detailsList-এর মধ্যে হবে।
         */

        if (selectedMainHead) {
            params.append(
                "transactionmainheads",
                selectedMainHead
            );
        }

        if (selectedDoctor) {
            params.append(
                "doctor_id",
                selectedDoctor
            );
        }

        if (selectedSr) {
            params.append(
                "sr_id",
                selectedSr
            );
        }

        if (selectedPatient) {
            params.append(
                "patient_id",
                selectedPatient
            );
        }

        if (selectedTranBy) {
            params.append(
                "tran_by",
                selectedTranBy
            );
        }

        if (status) {
            params.append(
                "status",
                status
            );
        }

        if (startDate) {
            params.append(
                "start_date",
                startDate
            );
        }

        if (endDate) {
            params.append(
                "end_date",
                endDate
            );
        }

        params.append("offset", newOffset);
        params.append("limit", limit);

        currentRequest = $.ajax({
            url: window.APP_URLS.TRANSACTION_DETAILS_LOAD_URL,
            method: "GET",
            data: params.toString(),

            success: function (res) {

                const fetched = res.results || [];

                if (append) {
                    detailsList = detailsList.concat(fetched);
                } else {
                    detailsList = fetched;
                }

                offset = newOffset;
                hasMore = fetched.length === limit;

                /*
                 * নতুন data load হওয়ার পরেও current search text
                 * অনুযায়ী table render হবে।
                 */
                renderTable();

                isLoading = false;
                currentRequest = null;
            },

            error: function (xhr, statusText) {

                if (statusText !== "abort") {
                    console.error(
                        xhr.status,
                        xhr.responseText
                    );
                }

                isLoading = false;
                currentRequest = null;
            }
        });
    }

    // =========================
    // RENDER TABLE
    // =========================
    function renderTable() {

        let html = "";

        /*
         * detailsList সরাসরি render না করে
         * locally searched list render করা হচ্ছে।
         */
        const filteredList = getFilteredDetailsList();

        if (!filteredList.length) {

            html = `
                <tr>
                    <td colspan="18"
                        class="text-center text-muted py-3">
                        No transaction details found
                    </td>
                </tr>
            `;

            $("#transactionDetailsTableBody").html(html);
            return;
        }

        filteredList.forEach(function (item, index) {

            html += `
                <tr>
                    <td>${index + 1}</td>

                    <td>${item.tran_id || ""}</td>

                    <td>${item.invoice_ref || ""}</td>

                    <td>${item.tran_date || ""}</td>

                    <td>${item.tran_head_id || ""}</td>

                    <td>${item.tran_head_name || "-"}</td>

                    <td>${item.tran_type_with || ""}</td>

                    <td>
                        ${
                            item.doctor_name ||
                            item.doctor_id ||
                            ""
                        }
                    </td>

                    <td>
                        ${
                            item.sr_name ||
                            item.sr_id ||
                            ""
                        }
                    </td>

                    <td>
                        ${
                            item.patient_name ||
                            item.patient_id ||
                            ""
                        }
                    </td>

                    <td>${item.tran_by || ""}</td>

                    <td class="text-end">
                        ${money(item.tot_amount)}
                    </td>

                    <td class="text-end">
                        ${money(item.discount)}
                    </td>

                    <td class="text-end">
                        ${money(item.amount)}
                    </td>

                    <td class="text-end">
                        ${money(item.payment)}
                    </td>

                    <td class="text-end">
                        ${money(item.due_col)}
                    </td>

                    <td class="text-end">
                        ${money(item.due_disc)}
                    </td>

                    <td class="text-end">
                        ${money(item.due)}
                    </td>
                </tr>
            `;
        });

        $("#transactionDetailsTableBody").html(html);
    }

    // =========================
    // RESET AND LOAD
    // =========================
    function resetAndLoad() {

        if (currentRequest) {
            currentRequest.abort();
            currentRequest = null;
        }

        offset = 0;
        hasMore = true;
        isLoading = false;

        loadTransactionDetails(0, false);
    }

    // =========================
    // INIT
    // =========================
    setTodayDate();

    $("#transactionmainheads").val("10");

    loadDiagnosisFilterCombo(
        "#doctor_filter",
        window.APP_URLS.DIAGNOSIS_DOCTOR_FILTER_URL,
        "All Doctor"
    );

    loadDiagnosisFilterCombo(
        "#sr_filter",
        window.APP_URLS.DIAGNOSIS_SR_FILTER_URL,
        "All SR"
    );

    loadDiagnosisFilterCombo(
        "#patient_filter",
        window.APP_URLS.DIAGNOSIS_PATIENT_FILTER_URL,
        "All Patient"
    );

    loadDiagnosisFilterCombo(
        "#tran_by_filter",
        window.APP_URLS.DIAGNOSIS_TRAN_BY_FILTER_URL,
        "All Transaction By"
    );

    loadTransactionDetails(0, false);

    // =========================
    // FILTER FORM
    // =========================
    $("form").on("submit", function (e) {

        e.preventDefault();

        resetAndLoad();
    });

    // =========================
    // LOCAL SEARCH
    // =========================
    $("#productSearch").on("input", function () {

        /*
         * এখানে কোনো AJAX/API call হবে না।
         * শুধু current detailsList আবার render হবে।
         */
        renderTable();
    });

    // =========================
    // SCROLL PAGINATION
    // =========================
    $(".table-responsive").on("scroll", function () {

        const reachedBottom =
            $(this).scrollTop() +
            $(this).innerHeight() >=
            this.scrollHeight - 10;

        if (
            reachedBottom &&
            hasMore &&
            !isLoading
        ) {
            const nextOffset = offset + limit;

            loadTransactionDetails(
                nextOffset,
                true
            );
        }
    });

});