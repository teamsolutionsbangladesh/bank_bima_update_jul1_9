$(document).ready(function () {

    // =========================
    // VARIABLES
    // =========================
    let summaryList = [];
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

        const localDate =
            today.getFullYear() + "-" +
            String(today.getMonth() + 1).padStart(2, "0") + "-" +
            String(today.getDate()).padStart(2, "0");

        $("#start_date").val(localDate);
        $("#end_date").val(localDate);
    }

    // =========================
    // MONEY FORMAT
    // =========================
    function money(value) {
        const amount = parseFloat(value) || 0;
        return amount.toFixed(2);
    }

    // =========================
    // DATE FORMAT
    // =========================
    function displayDate(value) {

        if (!value) {
            return "";
        }

        return String(value)
            .split("T")[0]
            .split(" ")[0];
    }

    // =========================
    // LOAD FILTER COMBO
    // =========================
    function loadDiagnosisFilterCombo(selector, url, label) {

        if (!url) {
            console.error(
                "Filter URL not found for:",
                selector
            );
            return;
        }

        $.ajax({
            url: url,
            method: "GET",

            success: function (res) {

                const $select = $(selector);

                $select.empty();

                $select.append(
                    `<option value="">${label}</option>`
                );

                (res.results || []).forEach(function (item) {

                    $select.append(
                        `<option value="${item.id}">
                            ${item.name}
                        </option>`
                    );
                });
            },

            error: function (xhr) {

                console.error(
                    "Filter combo load failed:",
                    selector,
                    xhr.status,
                    xhr.responseText
                );
            }
        });
    }

    // =========================
    // CURRENT LIST LOCAL SEARCH
    // =========================
    function getFilteredSummaryList() {

        const searchText =
            (
                $("#supplierSearch").val() ||
                $("input[name='search']").val() ||
                ""
            )
                .toLowerCase()
                .trim();

        if (!searchText) {
            return summaryList;
        }

        return summaryList.filter(function (item) {

            const searchableText = [
                item.tran_id,
                item.invoice_ref,
                item.invoice,
                item.tran_date,

                item.supplier_name,
                item.tran_type_with,
                item.tran_with_name,

                item.doctor_name,
                item.doctor_id,

                item.sr_name,
                item.sr_id,

                item.patient_name,
                item.patient_id,

                item.tran_by,
                item.user_name,
                item.tran_user,

                item.bill_total,
                item.bill_amount,
                item.discount,
                item.net_total,
                item.net_amount,
                item.advance,
                item.payment,
                item.due_collection,
                item.due_col,
                item.due_discount,
                item.due_disc,
                item.due
            ]
                .map(function (value) {

                    if (
                        value === null ||
                        value === undefined
                    ) {
                        return "";
                    }

                    return String(value);
                })
                .join(" ")
                .toLowerCase();

            return searchableText.includes(searchText);
        });
    }

    // =========================
    // LOAD TRANSACTION SUMMARY
    // =========================
    function loadTransactionSummary(
        newOffset = 0,
        append = false
    ) {

        if (isLoading) {
            return;
        }

        if (
            currentRequest &&
            currentRequest.readyState !== 4
        ) {
            currentRequest.abort();
        }

        isLoading = true;

        const params = new URLSearchParams();

        const selectedMainHead =
            $("#transactionmainheads").val() || "10";

        const selectedDoctor =
            $("#doctor_filter").val() || "";

        const selectedSr =
            $("#sr_filter").val() || "";

        const selectedPatient =
            $("#patient_filter").val() || "";

        const selectedTranBy =
            $("#tran_by_filter").val() || "";

        const status =
            $("#status").val() || "";

        const startDate =
            $("#start_date").val() || "";

        const endDate =
            $("#end_date").val() || "";

        limit =
            parseInt($("#perPage").val(), 10) || 50;

        /*
         * Search query API-তে পাঠানো হচ্ছে না।
         * Search শুধু বর্তমানে loaded summaryList-এর মধ্যে হবে।
         */

        if (selectedMainHead) {
            params.append(
                "transactionmainheads",
                selectedMainHead
            );

            params.append(
                "tran_main_head",
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
        params.append("per_page", limit);

        currentRequest = $.ajax({
            url: window.APP_URLS.PAYMENT_LIST_URL,
            method: "GET",
            cache: false,
            data: params.toString(),

            success: function (res) {

                const fetched =
                    res.results || [];

                if (append) {
                    summaryList =
                        summaryList.concat(fetched);
                } else {
                    summaryList = fetched;
                }

                offset = newOffset;

                hasMore =
                    fetched.length === limit;

                renderSummaryTable();

                if ($("#total_due").length) {

                    const totalDue =
                        res.total_due !== undefined
                            ? res.total_due
                            : calculateTotalDue();

                    $("#total_due").val(
                        money(totalDue)
                    );
                    <td class="text-center">
                        -
                    </td>
                }

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
    // CALCULATE TOTAL DUE
    // =========================
    function calculateTotalDue() {

        let totalDue = 0;

        summaryList.forEach(function (item) {

            totalDue +=
                parseFloat(item.due) || 0;
        });

        return totalDue;
    }

    // =========================
    // RENDER SUMMARY TABLE
    // =========================
    function renderSummaryTable() {

        let html = "";

        const filteredList =
            getFilteredSummaryList();

        if (!filteredList.length) {

            html = `
                <tr>
                    <td
                        colspan="16"
                        class="text-center text-muted py-3"
                    >
                        No transaction summary found
                    </td>
                </tr>
            `;

            $("#paymentListTableBody").html(html);
            return;
        }

        filteredList.forEach(function (item, index) {

            const supplier =
                item.supplier_name ||
                item.tran_with_name ||
                item.tran_type_with ||
                "-";

            const doctor =
                item.doctor_name ||
                item.doctor_id ||
                "-";

            const sr =
                item.sr_name ||
                item.sr_id ||
                "-";

            const patient =
                item.patient_name ||
                item.user_name ||
                item.tran_user ||
                item.patient_id ||
                "-";

            const billAmount =
                item.bill_total ??
                item.bill_amount ??
                0;

            const netAmount =
                item.net_total ??
                item.net_amount ??
                0;

            const advance =
                item.advance ??
                item.payment ??
                0;

            const dueCollection =
                item.due_collection ??
                item.due_col ??
                0;

            const dueDiscount =
                item.due_discount ??
                item.due_disc ??
                0;

            html += `
                <tr>
                    <td>${index + 1}</td>

                    <td>
                        ${item.tran_id || "-"}
                    </td>

                    <td>
                        ${
                            item.invoice_ref ||
                            item.invoice ||
                            "-"
                        }
                    </td>

                    <td>
                        ${displayDate(item.tran_date)}
                    </td>

                    <td>
                        ${supplier}
                    </td>

                    <td>
                        ${doctor}
                    </td>

                    <td>
                        ${sr}
                    </td>

                    <td>
                        ${patient}
                    </td>

                    <td>
                        ${item.tran_by || "-"}
                    </td>

                    <td class="text-end">
                        ${money(billAmount)}
                    </td>

                    <td class="text-end">
                        ${money(item.discount)}
                    </td>

                    <td class="text-end">
                        ${money(netAmount)}
                    </td>

                    <td class="text-end">
                        ${money(advance)}
                    </td>

                    <td class="text-end">
                        ${money(dueCollection)}
                    </td>

                    <td class="text-end">
                        ${money(dueDiscount)}
                    </td>

                    <td class="text-end">
                        ${money(item.due)}
                    </td>
                </tr>
            `;
        });

        $("#paymentListTableBody").html(html);
    }

    // =========================
    // RESET AND LOAD
    // =========================
    function resetAndLoad() {

        if (
            currentRequest &&
            currentRequest.readyState !== 4
        ) {
            currentRequest.abort();
        }

        currentRequest = null;
        isLoading = false;

        offset = 0;
        hasMore = true;

        loadTransactionSummary(
            0,
            false
        );
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

    loadTransactionSummary(
        0,
        false
    );

    // =========================
    // FILTER FORM
    // =========================
    $("#paymentFilterForm, form")
        .off("submit.transactionSummary")
        .on(
            "submit.transactionSummary",
            function (e) {

                e.preventDefault();

                resetAndLoad();
            }
        );

    // =========================
    // COMBO FILTER CHANGE
    // =========================
    $(
        "#doctor_filter, " +
        "#sr_filter, " +
        "#patient_filter, " +
        "#tran_by_filter"
    )
        .off("change.transactionSummary")
        .on(
            "change.transactionSummary",
            function () {

                resetAndLoad();
            }
        );

    // =========================
    // STATUS / DATE / PER PAGE
    // =========================
    $(
        "#status, " +
        "#start_date, " +
        "#end_date, " +
        "#perPage"
    )
        .off("change.transactionSummary")
        .on(
            "change.transactionSummary",
            function () {

                resetAndLoad();
            }
        );

    // =========================
    // CURRENT LIST LOCAL SEARCH
    // =========================
    $("#supplierSearch, input[name='search']")
        .off("input.transactionSummary")
        .on(
            "input.transactionSummary",
            function () {

                /*
                 * এখানে AJAX request হবে না।
                 * বর্তমানে summaryList-এ থাকা data search হবে।
                 */
                renderSummaryTable();
            }
        );

    // =========================
    // SCROLL PAGINATION
    // =========================
    $(".table-responsive")
        .off("scroll.transactionSummary")
        .on(
            "scroll.transactionSummary",
            function () {

                const reachedBottom =
                    $(this).scrollTop() +
                    $(this).innerHeight() >=
                    this.scrollHeight - 10;

                if (
                    reachedBottom &&
                    hasMore &&
                    !isLoading
                ) {
                    const nextOffset =
                        offset + limit;

                    loadTransactionSummary(
                        nextOffset,
                        true
                    );
                }
            }
        );

});