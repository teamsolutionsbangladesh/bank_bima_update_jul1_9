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
	                    q: params.term || "" // codex change
	                };
            },

            processResults: function (data) {
                return {
                    results: data.results // codex change
                };
            },

            cache: true
        },
	        placeholder: "-- Start Typing Doctor ID / Name --",
		        minimumInputLength: 0, // codex change
	        allowClear: true,
	        width: "100%",
	        dropdownParent: $("#doc_lookup").closest(".card"), // codex change
	        dropdownCssClass: "diagnosis-reference-dropdown" // codex change
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
	                    q: params.term || "" // codex change
	                };
            },

            processResults: function (data) {
                let results = data.results || []; // codex change
                results.unshift({ id: "__blank_sr__", text: "-- No SR --", is_blank_sr: true }); // codex change
                return {
                    results: results // codex change
                };
            },

            cache: true
        },
	        placeholder: "-- Start Typing SR ID / Name --",
		        minimumInputLength: 0, // codex change
	        allowClear: true,
	        width: "100%",
	        dropdownParent: $("#sr_lookup").closest(".card"), // codex change
	        dropdownCssClass: "diagnosis-reference-dropdown" // codex change
	    });

	    $("#sr_lookup")
	        .off("select2:select")
	        .on("select2:select", function (e) {
	            let data = e.params.data;

                if (data.is_blank_sr || data.id === "__blank_sr__") { // codex change
                    $("#sr_lookup").val(null).trigger("change"); // codex change
                    $("#sr_id").val(""); // codex change
                    $("#sr_name_display").val(""); // codex change
                    $("#sr_lookup").select2("close"); // codex change
                    setTimeout(function () { $("#productSearch").select2("open"); focusOpenedSelect2Search(); }, 100); // codex change
                    return; // codex change
                } // codex change

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

    $("#doc_lookup, #sr_lookup") // codex change
        .off("focus.diagnosisOpenList click.diagnosisOpenList") // codex change
        .on("focus.diagnosisOpenList click.diagnosisOpenList", function () { // codex change
            const $field = $(this); // codex change
            if ($field.data("select2") && !$field.data("select2").isOpen()) { $field.select2("open"); } // codex change
        }); // codex change

    // ==========================================
    // PRODUCT SEARCH AUTO-COMPLETE
    // ==========================================
    // ==========================================
// PRODUCT SEARCH AUTO-COMPLETE
// ==========================================

function formatProductResult(product) {

    // Select2 loading message
    if (product.loading) {
        return product.text;
    }

    let productName =
        product.name ||
        product.text ||
        "-";

    let categoryName =
        product.category_name ||
        "";

    let quantity =
        product.quantity ??
        product.qty ??
        product.stock_quantity ??
        0;

    let mrp =
        parseFloat(product.mrp) || 0;

    return $(`
        <div class="product-search-row">

            <div class="product-search-name">
                ${productName}
            </div>

            <div class="product-search-generic">
                ${categoryName}
            </div>

            <div class="product-search-qty">
                ${quantity}
            </div>

            <div class="product-search-mrp">
                ${mrp.toFixed(2)}
            </div>

        </div>
    `);
}

function formatSelectedProduct(product) {

    if (!product.id) {
        return product.text;
    }

    return product.name || product.text || "";
}

$(".select2-product").select2({
    ajax: {
        url: window.APP_URLS.PRODUCT_SEARCH_URL,
        dataType: "json",
        delay: 250,

	        data: function (params) {
	            return {
	                q: params.term || "", // codex change
	                tran_main_head_id: $("#transactionmainheads").val(),
	                tran_group_id: $("#tran_group").val()
            };
        },

        processResults: function (data) {
            return {
                results: $.map(
                    data.results || [],
                    function (item) {

                        return {
                            id: item.id,

                            text:
                                item.name ||
                                item.text ||
                                "",

                            name:
                                item.name ||
                                item.text ||
                                "",

                            generic_name:
                                item.generic_name ||
                                item.generic ||
                                item.genericName ||
                                "",

                            quantity:
                                item.quantity ??
                                item.qty ??
                                item.stock_quantity ??
                                0,

                            cp:
                                item.cp || 0,

                            mrp:
                                item.mrp || 0,

                            category_name:
                                item.category_name || "",

                            manufacturer:
                                item.manufacturer || "",

                            form:
                                item.form || ""
                        };
                    }
                )
            };
        },

        cache: true
    },

	    placeholder: "-- Start Typing Product ID / Name --",
		    minimumInputLength: 0, // codex change
	    allowClear: true,
	    width: "100%",
	    dropdownParent: $("#productSearch").closest(".card-body"), // codex change
	    dropdownCssClass: "diagnosis-product-dropdown", // codex change

	    templateResult: formatProductResult,
    templateSelection: formatSelectedProduct,

    escapeMarkup: function (markup) {
        return markup;
    },

    language: {
        searching: function () {
            return "Searching products...";
        },

        noResults: function () {
            return "No product found";
        }
    }
});

$("#productSearch")
    .off("select2:select")
    .on("select2:select", function (e) {

        let data = e.params.data;

        let qty =
            parseFloat($("#quantity").val()) || 1;

        let cp =
            parseFloat(data.cp) || 0;

        let mrp =
            parseFloat(data.mrp) || 0;

        let total =
            qty * mrp;

        $("#productid").val(data.id);
        $("#cp").val(cp);
        $("#mrp").val(mrp);
        $("#quantity").val(qty);
        $("#total").val(total.toFixed(2));

        $("#productSearch").select2("close");

	        window.diagnosisProductAddFocusTimer = setTimeout(function () { // codex change

	            let addButton =
	                document.getElementById("addProductBtn");

	            if (addButton) {
                    if (window.diagnosisProductFocusLockUntil && Date.now() <= window.diagnosisProductFocusLockUntil) { return; } // codex change

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

$("#productSearch") // codex change
    .off("focus.diagnosisOpenList click.diagnosisOpenList") // codex change
    .on("focus.diagnosisOpenList click.diagnosisOpenList", function () { // codex change
        const $field = $(this); // codex change
        if ($field.data("select2") && !$field.data("select2").isOpen()) { $field.select2("open"); } // codex change
    }); // codex change

function addProductDropdownHeader() {

    const productSelect2 =
        $("#productSearch").data("select2");

    if (
        !productSelect2 ||
        !productSelect2.$dropdown
    ) {
        return;
    }

    /*
     * শুধু Product Select2-এর নিজের dropdown ধরবে।
     * Doctor বা SR dropdown ধরবে না।
     */
    const $productDropdown =
        productSelect2.$dropdown;

    const $results =
        $productDropdown.find(".select2-results");

    if (!$results.length) {
        return;
    }

    if (
        $results.find(".product-search-header").length
    ) {
        return;
    }

    const header = `
        <div class="product-search-header">
            <div>Product Name</div>
            <div>Category</div>
            <div>Qty</div>
            <div>MRP</div>
        </div>
    `;

	    $results.prepend(header);
	}

	function resizeProductDropdown() { // codex change
	    const productSelect2 = $("#productSearch").data("select2"); // codex change
	    const productPanel = $("#productSearch").closest(".diagnosis-product-entry-panel"); // codex change
	    const productWidth = productPanel.find(".card").outerWidth(); // codex change
	    if (!productSelect2 || !productSelect2.$dropdown || !productWidth) { return; } // codex change
	    productSelect2.$dropdown.parent().css({ // codex change
	        left: "0px", // codex change
	        width: productWidth + "px", // codex change
	        minWidth: "0", // codex change
	        maxWidth: productWidth + "px" // codex change
	    }); // codex change
	    productSelect2.$dropdown.css({ // codex change
	        width: productWidth + "px", // codex change
	        minWidth: "0", // codex change
	        maxWidth: productWidth + "px" // codex change
	    }); // codex change
	} // codex change

	function resizeReferenceDropdown(selector) { // codex change
	    const referenceSelect2 = $(selector).data("select2"); // codex change
	    const referenceCard = $(selector).closest(".card"); // codex change
	    const referenceWidth = referenceCard.outerWidth(); // codex change
	    if (!referenceSelect2 || !referenceSelect2.$dropdown || !referenceWidth) { return; } // codex change
	    referenceSelect2.$dropdown.closest(".select2-container").css({ // codex change
	        left: "0px", // codex change
	        width: referenceWidth + "px", // codex change
	        minWidth: "0", // codex change
	        maxWidth: referenceWidth + "px" // codex change
	    }); // codex change
	    referenceSelect2.$dropdown.parent().css({ // codex change
	        left: "0px", // codex change
	        width: referenceWidth + "px", // codex change
	        minWidth: "0", // codex change
	        maxWidth: referenceWidth + "px" // codex change
	    }); // codex change
	    referenceSelect2.$dropdown.css({ // codex change
	        width: referenceWidth + "px", // codex change
	        minWidth: "0", // codex change
	        maxWidth: referenceWidth + "px" // codex change
	    }); // codex change
	} // codex change

	$(document)
	    .off("select2:open.productHeader")
    .on("select2:open.productHeader", function (e) {

        if ($(e.target).attr("id") !== "productSearch") {
            return;
	        }

		        setTimeout(function () {
		            resizeProductDropdown(); // codex change
		            addProductDropdownHeader();
		        }, 50);
		    });

	    $(document) // codex change
	        .off("select2:open.referenceDropdownWidth") // codex change
	        .on("select2:open.referenceDropdownWidth", function (e) { // codex change
	            const openedId = $(e.target).attr("id"); // codex change
	            if (openedId !== "doc_lookup" && openedId !== "sr_lookup") { return; } // codex change
	            setTimeout(function () { // codex change
	                resizeReferenceDropdown("#" + openedId); // codex change
	            }, 50); // codex change
	        }); // codex change

    // ==========================================
    // SELECT2 OPEN HOLE SEARCH INPUT FOCUS
    // ==========================================
    $(document)
        .off("select2:open.diagnosisSelect2")
        .on("select2:open.diagnosisSelect2", function () {
            focusOpenedSelect2Search();
        });
});
