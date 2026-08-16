$(document).ready(function () {
    console.log("🚀 Diagnosis Select2 Engine Active.");

    function focusOpenedSelect2Search() {
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

    // ==========================================
    // DOCTOR SEARCH AUTO-COMPLETE
    // ==========================================
    $(".select2-doc").select2({
        ajax: {
            url: window.APP_URLS.DOCTOR_AUTOCOMPLETE_URL,
            dataType: "json",
            delay: 250,

            data: function (params) {
                return {
                    q: params.term
                };
            },

            processResults: function (data) {
                return {
                    results: data.results
                };
            },

            cache: true
        },
        placeholder: "-- Start Typing Doctor ID / Name --",
        minimumInputLength: 1,
        allowClear: true,
        width: "100%"
    });

    $("#doc_lookup")
        .off("select2:select")
        .on("select2:select", function (e) {
            let data = e.params.data;

            $("#doc_id").val(data.id);
            $("#doc_speciality").val(data.speciality || "General");
            $("#doc_chamber").val(data.chamber || "N/A");

            $("#doc_lookup").select2("close");

            setTimeout(function () {
                $("#sr_lookup").select2("open");
                focusOpenedSelect2Search();
            }, 300);
        });

    $("#doc_lookup")
        .off("select2:clear")
        .on("select2:clear", function () {
            $("#doc_id").val("");
            $("#doc_speciality").val("");
            $("#doc_chamber").val("");
        });

    // ==========================================
    // SR AGENT SEARCH AUTO-COMPLETE
    // ==========================================
    $(".select2-sr").select2({
        ajax: {
            url: window.APP_URLS.SR_AUTOCOMPLETE_URL,
            dataType: "json",
            delay: 250,

            data: function (params) {
                return {
                    q: params.term
                };
            },

            processResults: function (data) {
                return {
                    results: data.results
                };
            },

            cache: true
        },
        placeholder: "-- Start Typing SR ID / Name --",
        minimumInputLength: 1,
        allowClear: true,
        width: "100%"
    });

    $("#sr_lookup")
        .off("select2:select")
        .on("select2:select", function (e) {
            let data = e.params.data;

            $("#sr_id").val(data.id);
            $("#sr_name_display").val(
                data.name_display || data.text || ""
            );

            $("#sr_lookup").select2("close");

            setTimeout(function () {
                $("#product_search").focus();
            }, 300);
        });

    $("#sr_lookup")
        .off("select2:clear")
        .on("select2:clear", function () {
            $("#sr_id").val("");
            $("#sr_name_display").val("");
        });

    // ==========================================
    // PRODUCT SEARCH AUTO-COMPLETE
    // ==========================================
    $(".select2-product").select2({ 
        ajax: {
            url: window.APP_URLS.PRODUCT_SEARCH_URL,
            dataType: "json",
            delay: 250,

            data: function (params) {
                return {
                    q: params.term,
                    tran_main_head_id: $("#transactionmainheads").val(),
                    tran_group_id: $("#tran_group").val()
                };
            },

            processResults: function (data) {
                return {
                    results: $.map(data.results || [], function (item) {
                        return {
                            id: item.id,
                            text: item.name,
                            name: item.name,
                            cp: item.cp,
                            mrp: item.mrp,
                            category_name: item.category_name,
                            manufacturer: item.manufacturer,
                            form: item.form
                        };
                    })
                };
            },

            cache: true
        },
        placeholder: "-- Start Typing Product ID / Name --",
        minimumInputLength: 1,
        allowClear: true,
        width: "100%"
    });

    $("#productSearch")
        .off("select2:select")
        .on("select2:select", function (e) {
            let data = e.params.data;

            let qty = parseFloat($("#quantity").val()) || 1;
            let cp = parseFloat(data.cp) || 0;
            let mrp = parseFloat(data.mrp) || 0;
            let total = qty * mrp;

            $("#productid").val(data.id);
            $("#cp").val(cp);
            $("#mrp").val(mrp);
            $("#quantity").val(qty);
            $("#total").val(total.toFixed(2));

            $("#productSearch").select2("close");

            setTimeout(function () {
            let addButton = document.getElementById("addProductBtn");

            if (addButton) {
                addButton.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });

                addButton.focus();
            }
        }, 300);
        });

    $("#productSearch")
        .off("select2:clear")
        .on("select2:clear", function () {
            $("#productid").val("");
            $("#cp").val("0");
            $("#mrp").val("0");
            $("#total").val("");
        });

    // ==========================================
    // SELECT2 OPEN HOLE SEARCH INPUT FOCUS
    // ==========================================
    $(document)
        .off("select2:open.diagnosisSelect2")
        .on("select2:open.diagnosisSelect2", function () {
            focusOpenedSelect2Search();
        });
});