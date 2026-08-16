$(document).on("click", ".verify-btn", function() {
    let tranId = $(this).data("tran-id");

    // Store tranId in modal hidden input
    $("#verifyModal #tran_id").remove();
    $("#verifyModal .modal-body").append('<input type="hidden" id="tran_id" value="'+tranId+'">');

    // AJAX request to fetch transaction details
    $.ajax({
        url: "/transaction/temp/get/" + tranId + "/",  // Django view URL
        method: "GET",
        success: function(res) {
            if(res.success) {
                // Populate modal fields
                $("#verifyModal #location").val(res.data.location);
                $("#verifyModal #store").val(res.data.store_id);
                $("#verifyModal #date").val(res.data.date);
                $("#verifyModal #supplier").val(res.data.supplier_name);
                $("#verifyModal #payment_method").val(res.data.payment_method);
                $("#verifyModal #invoiceAmount").val(res.data.bill_amount);
                $("#verifyModal #discount").val(res.data.discount);
                $("#verifyModal #netAmount").val(res.data.net_amount);
                $("#verifyModal #advanced").val(res.data.payment);
                $("#verifyModal #balance").val(res.data.due);

                // Populate selected medicines table
                let tbody = $("#verifyModal #selectedMedicineList");
                tbody.empty();
                res.data.medicines.forEach(function(med, index){
                    tbody.append('<tr>'+
                        '<td>'+ (index+1) +'</td>'+
                        '<td>'+ med.name +'</td>'+
                        '<td>'+ med.quantity +'</td>'+
                        '<td>'+ med.unit_price +'</td>'+
                        '<td>'+ med.total +'</td>'+
                        '<td></td>'+
                    '</tr>');
                });

                // Populate product list table (optional)
                let productBody = $("#verifyModal #medicineListTableBody");
                productBody.empty();
                res.data.products.forEach(function(prod){
                    productBody.append('<tr>'+
                        '<td>'+ prod.name +'</td>'+
                        '<td>'+ prod.generic_name +'</td>'+
                        '<td>'+ prod.manufacture +'</td>'+
                        '<td>'+ prod.form +'</td>'+
                        '<td>'+ prod.qty +'</td>'+
                        '<td>'+ prod.cp +'</td>'+
                        '<td>'+ prod.mrp +'</td>'+
                        '<td></td>'+
                    '</tr>');
                });
            }
        }
    });
});
