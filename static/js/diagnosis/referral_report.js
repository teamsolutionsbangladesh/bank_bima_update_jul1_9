$(document).ready(function () { // #codex
    function money(value) { // #codex
        return Number(value || 0).toFixed(2); // #codex
    } // #codex

    function today() { // #codex
        return new Date().toISOString().slice(0, 10); // #codex
    } // #codex

    function renderEmpty(message) { // #codex
        $("#refReportBody").html(`<tr><td colspan="10" class="text-center text-muted py-4">${message}</td></tr>`); // #codex
        $("#totalTestTk, #totalDiscount, #totalReferral").text("0.00"); // #codex
    } // #codex

    function loadProviders() { // #codex
        let reportType = $("#refReportType").val(); // #codex
        $.get("/diagnosis/referral/report/providers/", { report_type: reportType }, function (res) { // #codex
            let label = reportType === "sr" ? "SR" : "Doctor"; // #codex
            let options = `<option value="">-- Select ${label} --</option>`; // #codex
            (res.providers || []).forEach(function (provider) { // #codex
                options += `<option value="${provider.code}">${provider.code} - ${provider.name}</option>`; // #codex
            }); // #codex
            $("#refProvider").html(options); // #codex
            renderEmpty("Filter report"); // #codex
        }).fail(function () { // #codex
            renderEmpty("Failed to load provider list"); // #codex
        }); // #codex
    } // #codex

    function loadReport() { // #codex
        let params = { // #codex
            report_type: $("#refReportType").val(), // #codex
            provider_id: $("#refProvider").val(), // #codex
            start_date: $("#refStartDate").val(), // #codex
            end_date: $("#refEndDate").val() // #codex
        }; // #codex
        if (!params.provider_id || !params.start_date || !params.end_date) { // #codex
            renderEmpty("Select provider and date range"); // #codex
            return; // #codex
        } // #codex
        $.get("/diagnosis/referral/report/data/", params, function (res) { // #codex
            let rows = res.rows || []; // #codex
            if (!rows.length) { renderEmpty("No referral transaction found"); return; } // #codex
            let html = ""; // #codex
            rows.forEach(function (row, index) { // #codex
                html += `<tr>
                    <td>${index + 1}</td>
                    <td>${row.tran_id || "-"}</td>
                    <td>${row.tran_date || "-"}</td>
                    <td>${row.group_name || "-"}</td>
                    <td>${row.tran_head_name || "-"}</td>
                    <td class="text-end">${money(row.test_tk)}</td>
                    <td class="text-end">${money(row.discount)}</td>
                    <td>${row.ref_type || "-"}</td>
                    <td class="text-end">${money(row.ref_rate)}</td>
                    <td class="text-end">${money(row.referral_amount)}</td>
                </tr>`; // #codex
            }); // #codex
            $("#refReportBody").html(html); // #codex
            $("#totalTestTk").text(money(res.total_test_tk)); // #codex
            $("#totalDiscount").text(money(res.total_discount)); // #codex
            $("#totalReferral").text(money(res.total_referral)); // #codex
        }).fail(function (xhr) { // #codex
            let res = xhr.responseJSON || {}; // #codex
            renderEmpty(res.message || "Failed to load referral report"); // #codex
        }); // #codex
    } // #codex

    function downloadReportPdf() { // #codex
        let params = { // #codex
            report_type: $("#refReportType").val(), // #codex
            provider_id: $("#refProvider").val(), // #codex
            start_date: $("#refStartDate").val(), // #codex
            end_date: $("#refEndDate").val() // #codex
        }; // #codex
        if (!params.provider_id || !params.start_date || !params.end_date) { // #codex
            renderEmpty("Select provider and date range before downloading PDF"); // #codex
            return; // #codex
        } // #codex
        let query = $.param(params); // #codex
        window.location.href = `/diagnosis/referral/report/pdf/?${query}`; // #codex
    } // #codex

    $("#refStartDate").val(today()); // #codex
    $("#refEndDate").val(today()); // #codex
    $("#refReportType").on("change", loadProviders); // #codex
    $("#refFilterBtn").on("click", loadReport); // #codex
    $("#refPdfBtn").on("click", downloadReportPdf); // #codex
    loadProviders(); // #codex
}); // #codex
