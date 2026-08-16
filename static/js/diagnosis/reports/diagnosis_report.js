$(document).ready(function () {

    // =========================
    // VARIABLES
    // =========================
    let reportList = [];
    let currentIndex = 0;
    let offset = 0;
    let limit = 50;
    let query = "";
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
        return (parseFloat(value) || 0).toFixed(2);
    }

    // =========================
    // GET LIMIT
    // =========================
    function getLimit() {
        return parseInt($("#perPage").val(), 10) || 50;
    }

    // =========================
    // GET SEARCH QUERY
    // =========================
    function getSearchQuery() {
        return (
            $("#searchInput").val() ||
            $("#supplierSearch").val() ||
            ""
        ).trim();
    }

    // =========================
    // RESET AND LOAD
    // =========================
    function resetAndLoad() {

        query = getSearchQuery();

        offset = 0;
        currentIndex = 0;
        hasMore = true;

        loadReportList(query, 0, false);
    }

    // =========================
    // LOAD REPORT DATA
    // =========================
    function loadReportList(
        q = "",
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
        limit = getLimit();

        const startDate =
            $("#start_date").val() || "";

        const endDate =
            $("#end_date").val() || "";

        const status =
            $("#status").val() || "";

        const mainHead =
            $("#transactionmainheads").val() || "10";

        const doctorId =
            $("#doctor_filter").val() || "";

        const srId =
            $("#sr_filter").val() || "";

        const patientId =
            $("#patient_filter").val() || "";

        const tranBy =
            $("#tran_by_filter").val() || "";

        currentRequest = $.ajax({
            url:
                window.APP_URLS
                    .DIAGNOSIS_PAYMENT_REPORT_LOAD_URL,

            method: "GET",

            data: {
                q: q,
                search: q,

                offset: newOffset,
                limit: limit,

                start_date: startDate,
                end_date: endDate,

                status: status,

                transactionmainheads: mainHead,
                main_head: mainHead,

                doctor_id: doctorId,
                sr_id: srId,
                patient_id: patientId,
                tran_by: tranBy
            },

            success: function (res) {

                const fetched =
                    res.results || [];

                if (append) {
                    reportList =
                        reportList.concat(fetched);
                } else {
                    reportList = fetched;
                    currentIndex = 0;
                }

                offset = newOffset;

                hasMore =
                    fetched.length === limit;

                renderTable();

                if ($("#total_due").length) {
                    $("#total_due").val(
                        money(
                            res.total_due ||
                            calculateTotalDue()
                        )
                    );
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

        reportList.forEach(function (item) {
            totalDue +=
                parseFloat(item.due) || 0;
        });

        return totalDue;
    }

    // =========================
    // DISPLAY DATE
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
    // RENDER TABLE
    // =========================
    function renderTable() {

        let html = "";

        if (!reportList.length) {

            html = `
                <tr>
                    <td
                        colspan="16"
                        class="text-center text-muted py-3"
                    >
                        No diagnosis payment report found
                    </td>
                </tr>
            `;

            $("#reportTableBody").html(html);
            return;
        }

        reportList.forEach(function (item, index) {

            html += `
                <tr class="${
                    index === currentIndex
                        ? "table-active"
                        : ""
                }">

                    <td>${index + 1}</td>

                    <td>
                        ${item.tran_id || "-"}
                    </td>

                    <td>
                        ${item.invoice_ref || "-"}
                    </td>

                    <td>
                        ${displayDate(item.tran_date)}
                    </td>

                    <td>
                        ${
                            item.tran_with_name ||
                            item.tran_type_with ||
                            "-"
                        }
                    </td>

                    <td>
                        ${
                            item.doctor_name ||
                            item.doctor_id ||
                            "-"
                        }
                    </td>

                    <td>
                        ${
                            item.sr_name ||
                            item.sr_id ||
                            "-"
                        }
                    </td>

                    <td>
                        ${
                            item.patient_name ||
                            item.patient_id ||
                            "-"
                        }
                    </td>

                    <td>
                        ${item.tran_by || "-"}
                    </td>

                    <td class="text-end">
                        ${money(item.bill_amount)}
                    </td>

                    <td class="text-end">
                        ${money(item.discount)}
                    </td>

                    <td class="text-end">
                        ${money(item.net_amount)}
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

        $("#reportTableBody").html(html);
    }

    // =========================
    // INIT
    // =========================
    setTodayDate();

    $("#transactionmainheads").val("10");

    query = getSearchQuery();

    loadReportList(
        query,
        0,
        false
    );

    // =========================
    // FORM FILTER
    // =========================
    $("form").on("submit", function (e) {

        e.preventDefault();

        resetAndLoad();
    });

    // =========================
    // FILTER CHANGE
    // =========================
    $(
        "#start_date, " +
        "#end_date, " +
        "#status, " +
        "#perPage, " +
        "#doctor_filter, " +
        "#sr_filter, " +
        "#patient_filter, " +
        "#tran_by_filter"
    ).on("change", function () {

        resetAndLoad();
    });

    // =========================
    // SEARCH
    // =========================
    let typingTimer = null;

    $("#searchInput, #supplierSearch")
        .on("input", function () {

            clearTimeout(typingTimer);

            typingTimer = setTimeout(
                function () {
                    resetAndLoad();
                },
                300
            );
        });

    // =========================
    // SCROLL PAGINATION
    // =========================
    $(".table-responsive")
        .on("scroll", function () {

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

                loadReportList(
                    query,
                    nextOffset,
                    true
                );
            }
        });

    // =========================
    // PRINT PDF
    // =========================
    $("#printReportBtn")
    .off("click.diagnosisReport")
    .on("click.diagnosisReport", function (e) {

        e.preventDefault();

        const params = new URLSearchParams();

        const q = getSearchQuery();
        const startDate = $("#start_date").val() || "";
        const endDate = $("#end_date").val() || "";
        const status = $("#status").val() || "";
        const mainHead = $("#transactionmainheads").val() || "10";
        const doctorId = $("#doctor_filter").val() || "";
        const srId = $("#sr_filter").val() || "";
        const patientId = $("#patient_filter").val() || "";
        const tranBy = $("#tran_by_filter").val() || "";

        if (q) params.append("q", q);
        if (startDate) params.append("start_date", startDate);
        if (endDate) params.append("end_date", endDate);
        if (status) params.append("status", status);
        if (mainHead) params.append("transactionmainheads", mainHead);
        if (doctorId) params.append("doctor_id", doctorId);
        if (srId) params.append("sr_id", srId);
        if (patientId) params.append("patient_id", patientId);
        if (tranBy) params.append("tran_by", tranBy);

        const reportUrl =
            window.APP_URLS.DIAGNOSIS_PAYMENT_REPORT_URL ||
            window.APP_URLS.PAYMENT_REPORT_URL;

        if (!reportUrl) {
            console.error("Diagnosis report URL is undefined.");
            return;
        }

        window.open(
            reportUrl + "?" + params.toString(),
            "_blank"
        );
    });

});