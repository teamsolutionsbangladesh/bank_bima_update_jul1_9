function money(value) {
    const number = parseFloat(value) || 0;
    return number.toFixed(2);
}

function safePreviewText(value) {
    if (value === undefined || value === null || value === "") return "-";
    return value;
}

function setInvoiceBarcode($target, invoiceValue, barcodeSvg) {
    if (!barcodeSvg) {
        $target.text(safePreviewText(invoiceValue));
        return;
    }
    $target.html(barcodeSvg);
}

function openPartyPaymentPreview(transactionId, redirectAfterClose = null) {
    $.ajax({
        url: window.APP_URLS.PAYMENT_PREVIEW_URL + transactionId + "/",
        method: "GET",

        success: function (res) {
            if (!res.success) {
                alert(res.error || "Unable to load transaction preview.");
                return;
            }

            const transaction = res.transaction || {};
            const details = res.details || [];

            $("#previewTranId").text(safePreviewText(transaction.tran_id));
            setInvoiceBarcode(
                $("#previewInvoiceNoBarcode"),
                transaction.invoice_ref,
                res.invoice_barcode_svg
            );
            setInvoiceBarcode(
                $("#previewPatientIdBarcode"),
                transaction.patient_id,
                res.patient_barcode_svg
            );
            $("#previewTranDate").text(safePreviewText(transaction.tran_date));

            $("#previewPatientId").text(safePreviewText(transaction.patient_id));
            $("#previewPatientName").text(safePreviewText(transaction.patient_name));
            $("#previewPatientAge").text(safePreviewText(transaction.patient_age));
            $("#previewPatientGender").text(safePreviewText(transaction.patient_gender));

            $("#previewPatientPhone").text(
                safePreviewText(
                    transaction.patient_phone ||
                    transaction.patient_mobile
                )
            );

            $("#previewPatientAddress").text(
                safePreviewText(transaction.patient_address)
            );

            $("#previewDoctorName").text(
                safePreviewText(transaction.doctor_name)
            );

            $("#previewSrName").text(
                safePreviewText(transaction.sr_name)
            );

            let rowsHtml = "";

            details.forEach(function (item, index) {
                rowsHtml += `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${safePreviewText(item.product_id)}</td>
                        <td>${safePreviewText(item.product_name)}</td>
                        <td class="text-center">${parseFloat(item.quantity) || 0}</td>
                        <td class="text-end">${money(item.mrp)}</td>
                        <td class="text-end fw-semibold">${money(item.total)}</td>
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

            $("#previewInvoiceAmount").text(money(transaction.bill_amount));
            $("#previewDiscount").text(money(transaction.discount));
            $("#previewNetAmount").text(money(transaction.net_amount));
            $("#previewAdvance").text(money(transaction.payment));
            $("#previewDueCollection").text(money(transaction.due_col));
            $("#previewDueDiscount").text(money(transaction.due_disc));
            $("#previewBalance").text(money(transaction.due));
            (()=>{ const isPaid = (parseFloat(transaction.due) || 0) <= 0; const $box = $("#previewPaymentStatusBox"); $box.text(isPaid ? "PAID" : "DUE").removeClass("status-paid status-due").addClass(isPaid ? "status-paid" : "status-due"); })();

            const modalElement =
                document.getElementById("transactionPreviewModal");

            let previewModal =
                bootstrap.Modal.getInstance(modalElement);

            if (!previewModal) {
                previewModal =
                    new bootstrap.Modal(modalElement);
            }

            if (redirectAfterClose) {
                $(modalElement)
                    .off("hidden.bs.modal.paymentPreviewRedirect")
                    .one(
                        "hidden.bs.modal.paymentPreviewRedirect",
                        function () {
                            window.location.href = redirectAfterClose;
                        }
                    );
            } else {
                $(modalElement)
                    .off("hidden.bs.modal.paymentPreviewRedirect");
            }

            previewModal.show();
        },

        error: function (xhr) {
            console.error(xhr.responseText);

            alert(
                xhr.responseJSON?.error ||
                "Unable to load transaction preview."
            );
        }
    });
}
