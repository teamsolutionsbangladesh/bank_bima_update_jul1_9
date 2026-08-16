$(document).ready(function () {

    // =========================
    // STATE
    // =========================
    let selectedMainHead = "";
    let selectedWith = "";
    let selectedSupplier = "";
    let isLoading = false;
    let currentRequest = null;
    let paymentList = [];

    // INIT DATE
    function setTodayDate() {
        if ($("#start_date").val() || $("#end_date").val()) return;

        const today = new Date();
        const date =
            today.getFullYear() + "-" +
            String(today.getMonth() + 1).padStart(2, "0") + "-" +
            String(today.getDate()).padStart(2, "0");

        $("#start_date").val(date);
        $("#end_date").val(date);
    }

    // INIT EVERYTHING HERE
    setTodayDate();
    loadTransactionMainHeadsCombo(0);
    loadTable();

    // =========================
    // LOAD TABLE (MAIN LOGIC)
    // =========================
    function loadTable() {

        if (isLoading) return;
        if (currentRequest) currentRequest.abort?.();

        isLoading = true;

        let params = new URLSearchParams();

        // ===== COMBOS (ONLY SEND VALUES) =====
        if (selectedMainHead) {
            params.append("transactionmainheads", selectedMainHead);
        }

        if (selectedWith) {
            params.append("tran_with", selectedWith);
        }

        if (selectedSupplier) {
            params.append("supplier", selectedSupplier);
        }

        // ===== DATE FILTER =====
        let start_date = $("#start_date").val();
        let end_date = $("#end_date").val();

        if (start_date) params.append("start_date", start_date);
        if (end_date) params.append("end_date", end_date);

        currentRequest = $.ajax({
            url: window.APP_URLS.PARTY_PAYMENT_LIST_URL,
            method: "GET",
            data: params.toString(),

            success: function (res) {

                paymentList = res.results || [];

                renderTable();

                $("#total_due").val(res.total_due || 0);

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

        paymentList.forEach((item, index) => {

            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${item.tran_id}</td>
                    <td>${item.invoice_ref ?? '-'}</td>
                    <td>${item.tran_date}</td>

                    <td>${item.supplier_name ?? '-'}</td>
                    <td>${item.user_name ?? '-'}</td>

                    <td class="text-end">${item.bill_total}</td>
                    <td class="text-end">${item.discount}</td>
                    <td class="text-end">${item.net_total}</td>

                    <td class="text-end">${item.advance ?? 0}</td>
                    <td class="text-end">${item.due_collection}</td>
                    <td class="text-end">${item.due_discount}</td>
                    <td class="text-end">${item.due}</td>

                    <td class="text-center">
                        <button class="btn btn-sm btn-primary payment-btn"
                            data-id="${item.id}">
                            Payment
                        </button>
                    </td>
                </tr>
            `;
        });

        $("#paymentListTableBody").html(html);
    }

    // =========================
    // EVENTS (ONLY UPDATE STATE)
    // =========================

    $("#transactionmainheads").on("change", function () {
        selectedMainHead = this.value;
        loadTable();
    });

    $("#transaction_with").on("change", function () {
        selectedWith = this.value;
        loadTable();
    });

    $("#transaction_with_user").on("change", function () {
        selectedSupplier = this.value;  // THIS MUST BE user_infos.id
        loadTable();
    });

    // =========================
    // DATE FILTER
    // =========================
    $("#start_date, #end_date").on("change", function () {
        loadTable();
    });

    // =========================
    // PAYMENT BUTTON
    // =========================
    $(document).on("click", ".payment-btn", function () {

        const id = $(this).data("id");

        window.location.href =
            "/general/party-payment/payment-form/" + id + "/";
    });

    // =========================
    // FIFO PAYMENT
    // =========================
    $("#fifo_pay_btn").on("click", function () {

        let amount = $("#fifo_payment").val();

        if (!amount || amount <= 0) {
            alert("Enter payment amount");
            return;
        }

        let ids = paymentList.map(x => x.id);

        $.ajax({
            url: "/general/process-fifo-payment/",
            type: "POST",
            data: {
                payment: amount,
                ids: JSON.stringify(ids)
            },
            success: function (res) {

                if (!res.success) {
                    alert(res.error);
                    return;
                }

                alert("Paid: " + res.paid);

                loadTable();
            }
        });
    });

    // =========================
    // INIT
    // =========================
    setTodayDate();
    loadTable();

});