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

        if ($("#start_date").val() || $("#end_date").val()) return;

        const today = new Date();
        const localDate =
            today.getFullYear() + "-" +
            String(today.getMonth() + 1).padStart(2, "0") + "-" +
            String(today.getDate()).padStart(2, "0");

        $("#start_date").val(localDate);
        $("#end_date").val(localDate);
    }

    // =========================
    // LOAD DATA
    // =========================
    function loadReportList(q = "", newOffset = 0, append = false) {

        if (isLoading) return;

        if (currentRequest && currentRequest.readyState !== 4) {
            currentRequest.abort();
        }

        isLoading = true;

        const start_date = $("#start_date").val();
        const end_date = $("#end_date").val();

        currentRequest = $.ajax({
            url: "/reports/party-payment/load/",
            method: "GET",
            data: {
                q: q,
                offset: newOffset,

                start_date: start_date,
                end_date: end_date,

                main_head: $("#transactionmainheads").val() || "",
                tran_with: $("#transaction_with").val() || "",
                supplier: $("#transaction_with_user").val() || ""
            },

            success: function (res) {

                const fetched = res.results || [];

                if (append) {
                    reportList = reportList.concat(fetched);
                } else {
                    reportList = fetched;
                    currentIndex = 0;
                }

                offset = newOffset;

                renderTable();

                hasMore = fetched.length === limit;
                isLoading = false;
            },

            error: function () {
                isLoading = false;
            }
        });
    }

    // =========================
    // RENDER TABLE
    // =========================
    function renderTable() {

        let html = "";

        reportList.forEach((p, i) => {

            html += `
                <tr class="${i === currentIndex ? 'table-active' : ''}">
                    <td>${i + 1}</td>
                    <td>${p.tran_id || '-'}</td>
                    <td>${p.tran_date ? new Date(p.tran_date).toISOString().split("T")[0] : ""}</td>
                    <td>${p.tran_type_with || '-'}</td>
                    <td>${p.tran_user || '-'}</td>

                    <td style="text-align:right;">${p.bill_amount || 0}</td>
                    <td style="text-align:right;">${p.discount || 0}</td>
                    <td style="text-align:right;">${p.net_amount || 0}</td>

                    <td style="text-align:right;">${p.payment || 0}</td>
                    <td style="text-align:right;">${p.due_col || 0}</td>
                    <td style="text-align:right;">${p.due || 0}</td>
                </tr>
            `;
        });

        $("#reportTableBody").html(html);
    }

    // =========================
    // INIT
    // =========================
    setTodayDate();

    query = "";
    loadReportList(query, 0, false);

    // =========================
    // DATE FILTER
    // =========================
    $("#start_date, #end_date").on("change", function () {

        query = ($("#searchInput").val() || "").trim();

        offset = 0;
        currentIndex = 0;
        hasMore = true;

        loadReportList(query, 0, false);
    });

    // =========================
    // SEARCH (SAFE)
    // =========================
    let typingTimer;

    $("#searchInput").on("input", function () {

        clearTimeout(typingTimer);

        typingTimer = setTimeout(() => {

            query = ($(this).val() || "").trim();

            offset = 0;
            currentIndex = 0;
            hasMore = true;

            loadReportList(query, 0, false);

        }, 300);
    });

    // =========================
    // SCROLL PAGINATION
    // =========================
    $(".table-responsive").on("scroll", function () {

        if ($(this).scrollTop() + $(this).innerHeight() >= this.scrollHeight - 10) {

            if (hasMore && !isLoading) {
                offset += limit;
                loadReportList(query, offset, true);
            }
        }
    });

    // =========================
    // PRINT PDF (SAFE FIX)
    // =========================
    $("#printReportBtn").on("click", function () {

    let start_date = $("#start_date").val() || "";
    let end_date = $("#end_date").val() || "";

    let main_head = $("#transactionmainheads").val();
    let tran_with = $("#transaction_with").val();
    let supplier = $("#transaction_with_user").val();

    // FIX NULL VALUES
    if (!main_head || main_head === "null") {
        main_head = "";
    }

    if (!tran_with || tran_with === "null") {
        tran_with = "";
    }

    if (!supplier || supplier === "null") {
        supplier = "";
    }

    let q = ($("#searchInput").val() || "").trim();

    let url =
        "/general/reports/party-payment/?" +

        "q=" + encodeURIComponent(q) +

        "&main_head=" + encodeURIComponent(main_head) +

        "&tran_with=" + encodeURIComponent(tran_with) +

        "&supplier=" + encodeURIComponent(supplier) +

        "&start_date=" + encodeURIComponent(start_date) +

        "&end_date=" + encodeURIComponent(end_date);

    console.log(url);

    window.open(url, "_blank");
});

});