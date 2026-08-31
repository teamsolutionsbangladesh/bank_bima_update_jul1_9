let biochemistryRows = []; // #codex
let biochemistryTests = []; // #codex
let selectedBiochemistryTestId = ""; // #codex
let selectedBiochemistryTestIds = []; // #codex
let biochemistryRowsByTest = {}; // #codex
let activeResultTestId = ""; // #codex
let selectedBiochemistryTestNames = {}; // #codex
let invoiceSearchTimer = null; // #codex
let invoiceActiveIndex = -1; // #codex
let biochemistryEditMode = false; // #codex

function bioCsrfToken() { // #codex
    return $("#global_csrf").val() || $("input[name='csrfmiddlewaretoken']").val() || window.csrftoken; // #codex
} // #codex

function bioEscape(value) { // #codex
    return $("<div>").text(value || "").html(); // #codex
} // #codex

function bioResetForm() { // #codex
    $("#invoiceSearch").val(""); // #codex
    $("#invoiceId").val(""); // #codex
    $("#patientName,#doctorName,#labNo,#reportDate,#patientSex,#patientAgeY,#patientAgeM,#patientAgeD,#patientPhone,#patientAddress").val(""); // #codex
    $("#patientNameText,#doctorNameText,#patientSexText,#patientPhoneText,#patientAddressText").text("-"); // #codex
    $("#receiptNo,#patientAge").text("-"); // #codex
    $("#selectedTestName").text("Select test"); // #codex
    $("#invoiceTestBody").html('<tr><td colspan="3" class="text-center text-muted">Search transaction</td></tr>'); // #codex
    $("#resultEntryBody").html('<tr><td colspan="5" class="text-center text-muted">No result rows loaded</td></tr>'); // #codex
    biochemistryRows = []; // #codex
    biochemistryTests = []; // #codex
    selectedBiochemistryTestId = ""; // #codex
    selectedBiochemistryTestIds = []; // #codex
    biochemistryRowsByTest = {}; // #codex
    activeResultTestId = ""; // #codex
    selectedBiochemistryTestNames = {}; // #codex
} // #codex

function hideInvoiceDropdown() { // #codex
    $("#invoiceSearchDropdown").addClass("d-none").empty(); // #codex
} // #codex

function renderInvoiceDropdown(rows) { // #codex
    let html = ""; // #codex
    (rows || []).forEach(function (row) { // #codex
        let receipt = row.invoice_ref || row.tran_id || ""; // #codex
        html += `<div class="bio-invoice-option" data-invoice-id="${bioEscape(row.id)}" data-receipt="${bioEscape(receipt)}">
                    <b>${bioEscape(receipt)}</b>
                    <span class="bio-invoice-meta">${bioEscape(row.patient_name || "-")} | ${bioEscape(row.tran_id || "")}</span>
                </div>`; // #codex
    }); // #codex
    $("#invoiceSearchDropdown").html(html).toggleClass("d-none", !html); // #codex
    invoiceActiveIndex = rows && rows.length ? 0 : -1; // #codex
    $("#invoiceSearchDropdown .bio-invoice-option").first().addClass("active"); // #codex
} // #codex

function searchInvoiceSuggestions() { // #codex
    let term = ($("#invoiceSearch").val() || "").trim(); // #codex
    if (!term) { hideInvoiceDropdown(); return; } // #codex
    $.get("/diagnosis/lab-report/biochemistry/invoice-search/", { q: term }, function (response) { // #codex
        renderInvoiceDropdown(response.results || []); // #codex
    }); // #codex
} // #codex

function saveActiveResultInputs() { // #codex
    if (!biochemistryRowsByTest.template) { return; } // #codex
    $("#resultEntryBody tr[data-index]").each(function () { // #codex
        let index = Number($(this).data("index")); // #codex
        if (biochemistryRowsByTest.template[index]) { // #codex
            biochemistryRowsByTest.template[index].result = $(this).find(".bio-result-input").val(); // #codex
        } // #codex
    }); // #codex
} // #codex

function renderResultButtons() { // #codex
    let names = selectedBiochemistryTestIds.map(function (testId) { return selectedBiochemistryTestNames[testId] || testId; }); // #codex
    $("#selectedTestName").html(names.length ? `<span class="badge bg-primary">${bioEscape(names.join(", "))}</span>` : '<span class="badge bg-light text-dark border">Select test</span>'); // #codex
} // #codex

function renderSelectedResultRows() { // #codex
    biochemistryRows = biochemistryRowsByTest.template || []; // #codex
    let rowHtml = ""; // #codex
    biochemistryRows.forEach(function (row, index) { // #codex
        rowHtml += ` 
            <tr data-index="${index}">
                <td>${bioEscape(row.title)}</td>
                <td>${bioEscape(row.investigation)}</td>
                <td><input type="text" class="form-control form-control-sm bio-result-input" value="${bioEscape(row.result || "")}"></td>
                <td>${bioEscape(row.unit || "")}</td>
                <td>${bioEscape(row.reff_range || "")}</td>
            </tr>`; // #codex
    }); // #codex
    $("#resultEntryBody").html(rowHtml || '<tr><td colspan="5" class="text-center text-muted">Select investigation first</td></tr>'); // #codex
    renderResultButtons(); // #codex
} // #codex

function renderInvoiceData(response, renderRows) { // #codex
    let invoice = response.invoice || {}; // #codex
    $("#invoiceId").val(invoice.id || ""); // #codex
    $("#patientName").val(invoice.patient_name || ""); // #codex
    $("#doctorName").val(invoice.doctor_name || ""); // #codex
    $("#patientPhone").val(invoice.phone || ""); // #codex
    $("#patientAddress").val(invoice.address || ""); // #codex
    $("#patientNameText").text(invoice.patient_name || "-"); // #codex
    $("#doctorNameText").text(invoice.doctor_name || "-"); // #codex
    $("#patientPhoneText").text(invoice.phone || "-"); // #codex
    $("#patientAddressText").text(invoice.address || "-"); // #codex
    $("#labNo").val(invoice.id || ""); // #codex
    $("#reportDate").val((invoice.tran_date || "").slice(0, 10)); // #codex
    $("#receiptNo").text(invoice.invoice_ref || invoice.tran_id || "-"); // #codex
    $("#patientAge").text(`${invoice.age_y || 0}Y ${invoice.age_m || 0}M ${invoice.age_d || 0}D`); // #codex
    $("#patientAgeY").val(invoice.age_y || 0); // #codex
    $("#patientAgeM").val(invoice.age_m || 0); // #codex
    $("#patientAgeD").val(invoice.age_d || 0); // #codex
    $("#patientSex").val(invoice.gender || ""); // #codex
    $("#patientSexText").text(invoice.gender || "-"); // #codex

    let testHtml = ""; // #codex
    biochemistryTests = response.tests || []; // #codex
    if (response.selected_test_ids && response.selected_test_ids.length) { // #codex
        selectedBiochemistryTestIds = response.selected_test_ids.map(String); // #codex
        (response.selected_test_names || []).forEach(function (name, index) { selectedBiochemistryTestNames[selectedBiochemistryTestIds[index]] = name; }); // #codex
        if (!selectedBiochemistryTestId && selectedBiochemistryTestIds.length) { selectedBiochemistryTestId = selectedBiochemistryTestIds[0]; } // #codex
    } // #codex
    biochemistryTests.forEach(function (test) { // #codex
        selectedBiochemistryTestNames[String(test.id)] = selectedBiochemistryTestNames[String(test.id)] || test.name; // #codex
        let checked = selectedBiochemistryTestIds.includes(String(test.id)) ? "checked" : ""; // #codex
        let activeClass = checked ? " active" : ""; // #codex
        testHtml += `<tr class="bio-test-row${activeClass}" data-test-id="${bioEscape(test.id)}" data-test-name="${bioEscape(test.name)}"><td>${bioEscape(test.id)}</td><td>${bioEscape(test.name)}</td><td class="text-center"><input type="checkbox" class="bio-test-select" ${checked}></td></tr>`; // #codex
    }); // #codex
    let emptyMessage = response.already_added ? "Already added. Please edit from report list." : "No matching Biochemistry test found"; // #codex
    $("#invoiceTestBody").html(testHtml || `<tr><td colspan="3" class="text-center text-muted">${emptyMessage}</td></tr>`); // #codex
    let selectedTest = biochemistryTests.find(function (test) { return String(test.id) === String(selectedBiochemistryTestId); }); // #codex
    renderResultButtons(); // #codex

    if (renderRows && selectedBiochemistryTestId) { // #codex
        let selectedTestName = selectedTest ? selectedTest.name : ""; // #codex
        biochemistryRowsByTest.template = (response.rows || []).map(function (row) { // #codex
            row.head_id = ""; // #codex
            row.selected_test_name = selectedTestName; // #codex
            return row; // #codex
        }); // #codex
    } // #codex
    renderSelectedResultRows(); // #codex
} // #codex

function loadInvoiceBySearch(invoiceId, testId, editMode) { // #codex
    let data = invoiceId ? { invoice_id: invoiceId } : { invoice: $("#invoiceSearch").val() }; // #codex
    if (testId) { data.test_id = testId; } // #codex
    if (editMode || biochemistryEditMode) { data.edit = "1"; } // #codex
    $.get("/diagnosis/lab-report/biochemistry/load-invoice/", data, function (response) { // #codex
        renderInvoiceData(response, !!testId || biochemistryEditMode); // #codex
    }).fail(function (xhr) { // #codex
        let response = xhr.responseJSON || {}; // #codex
        alert(response.message || "Failed to load transaction"); // #codex
    }); // #codex
} // #codex

function collectResultRows() { // #codex
    saveActiveResultInputs(); // #codex
    let allRows = biochemistryRowsByTest.template || []; // #codex
    return allRows.map(function (row) { // #codex
        return { // #codex
            group_id: row.group_id, category_id: row.category_id, head_id: row.head_id || "", serial: row.serial || 0, // #codex
            title: row.title || "", title_code: row.title_code || "", investigation: row.investigation || "", investigation_code: row.investigation_code || "", // #codex
            unit: row.unit || "", reff_range: row.reff_range || "", result: row.result || "", selected_test_name: row.selected_test_name || "" // #codex
        }; // #codex
    }); // #codex
} // #codex

function openPreview(url) { // #codex
    $("#previewFrame").html('<div class="p-4 text-center text-muted">Loading preview...</div>'); // #codex
    $("#biochemistryPreviewModal").modal("show"); // #codex
    $.get(url, function (response) { // #codex
        $("#previewFrame").html(response.html || '<div class="p-4 text-center text-muted">No preview data found</div>'); // #codex
        $("#downloadPreviewBtn").attr("href", response.download_url || url.replace("/preview/", "/pdf/") + "?download=1"); // #codex
    }).fail(function (xhr) { // #codex
        let response = xhr.responseJSON || {}; // #codex
        $("#previewFrame").html(`<div class="p-4 text-center text-danger">${bioEscape(response.message || "Preview failed")}</div>`); // #codex
    }); // #codex
} // #codex

function bioLoadCategoryFilter() { // #codex
    let groupId = $("#resultFilterGroup").val(); // #codex
    let $category = $("#resultFilterCategory"); // #codex
    if (!$category.length) { return; } // #codex
    $category.html('<option value="">All Category</option>'); // #codex
    if (!groupId) { return; } // #codex
    $.get("/diagnosis/lab-report/categories/", { group_id: groupId }, function (response) { // #codex
        let options = '<option value="">All Category</option>'; // #codex
        (response.categories || []).forEach(function (category) { // #codex
            options += `<option value="${category.id}">${bioEscape(category.name)}</option>`; // #codex
        }); // #codex
        $category.html(options); // #codex
    }); // #codex
} // #codex

function loadResultList() { // #codex
    if (!$("#resultListBody").length) { return; } // #codex
    $.get("/diagnosis/lab-report/biochemistry/list/", {  // #codex
        search: $("#resultListSearch").val(),  // #codex
        group_id: $("#resultFilterGroup").val(),  // #codex
        category_id: $("#resultFilterCategory").val()  // #codex
    }, function (response) { // #codex
        let rows = response.results || []; // #codex
        let html = ""; // #codex
        rows.forEach(function (row, index) { // #codex
            html += ` 
                <tr>
                    <td>${index + 1}</td>
                    <td>${bioEscape(row.tran_id)}</td>
                    <td>${bioEscape(row.invoice_ref || "-")}</td>
                    <td>${bioEscape(row.patient_name || "-")}</td>
                    <td>${bioEscape(row.total_rows)}</td>
                    <td>${bioEscape(row.updated_at || "-")}</td>
                    <td>
                        <button type="button" class="btn btn-sm btn-warning bio-edit-btn" data-invoice-id="${row.invoice_id}">Edit</button>
                        <button type="button" class="btn btn-sm btn-primary bio-preview-btn" data-invoice-id="${row.invoice_id}">Preview</button>
                    </td>
                </tr>`; // #codex
        }); // #codex
        $("#resultListBody").html(html || '<tr><td colspan="7" class="text-center text-muted">No Biochemistry report found</td></tr>'); // #codex
    }); // #codex
} // #codex

function bioQueryParam(name) { // #codex
    return new URLSearchParams(window.location.search).get(name); // #codex
} // #codex

$(document).ready(function () { // #codex
    loadResultList(); // #codex
    let queryInvoiceId = bioQueryParam("invoice_id"); // #codex
    biochemistryEditMode = bioQueryParam("edit") === "1"; // #codex
    if (queryInvoiceId && $("#invoiceId").length) { loadInvoiceBySearch(queryInvoiceId, "", biochemistryEditMode); } // #codex

    $("#loadInvoiceBtn").on("click", function () { selectedBiochemistryTestId = ""; loadInvoiceBySearch(); }); // #codex
    $("#invoiceSearch").on("keydown", function (event) { // #codex
        let $options = $("#invoiceSearchDropdown .bio-invoice-option"); // #codex
        if ((!$options.length || $("#invoiceSearchDropdown").hasClass("d-none")) && event.key === "Enter") { event.preventDefault(); selectedBiochemistryTestId = ""; loadInvoiceBySearch(); return; } // #codex
        if (!$options.length || $("#invoiceSearchDropdown").hasClass("d-none")) { return; } // #codex
        if (event.key === "ArrowDown") { // #codex
            event.preventDefault(); // #codex
            invoiceActiveIndex = Math.min(invoiceActiveIndex + 1, $options.length - 1); // #codex
        } else if (event.key === "ArrowUp") { // #codex
            event.preventDefault(); // #codex
            invoiceActiveIndex = Math.max(invoiceActiveIndex - 1, 0); // #codex
        } else if (event.key === "Enter") { // #codex
            event.preventDefault(); // #codex
            $options.eq(Math.max(invoiceActiveIndex, 0)).trigger("click"); // #codex
            return; // #codex
        } else { return; } // #codex
        $options.removeClass("active").eq(invoiceActiveIndex).addClass("active"); // #codex
    }); // #codex
    $("#invoiceSearch").on("input", function () { // #codex
        clearTimeout(invoiceSearchTimer); // #codex
        invoiceSearchTimer = setTimeout(searchInvoiceSuggestions, 180); // #codex
    }); // #codex
    $(document).on("click", ".bio-invoice-option", function () { // #codex
        $("#invoiceSearch").val($(this).data("receipt")); // #codex
        selectedBiochemistryTestId = ""; // #codex
        hideInvoiceDropdown(); // #codex
        loadInvoiceBySearch($(this).data("invoice-id")); // #codex
    }); // #codex
    $(document).on("click", function (event) { // #codex
        if (!$(event.target).closest("#invoiceSearch,#invoiceSearchDropdown").length) { hideInvoiceDropdown(); } // #codex
    }); // #codex
    $("#resetBiochemistryBtn").on("click", bioResetForm); // #codex
    $("#resultListSearch").on("input", loadResultList); // #codex
    $("#resultListFilterBtn,#resultFilterCategory").on("click change", loadResultList); // #codex
    $("#resultFilterGroup").on("change", function () { bioLoadCategoryFilter(); loadResultList(); }); // #codex

    $("#saveBiochemistryBtn").on("click", function () { // #codex
        let invoiceId = $("#invoiceId").val(); // #codex
        if (!invoiceId) { alert("Please search transaction first"); return; } // #codex
        if (!selectedBiochemistryTestIds.length) { alert("Please select investigation first"); return; } // #codex
        let rows = collectResultRows().filter(function (row) { return String(row.result || "").trim(); }); // #codex
        if (!rows.length) { alert("No result rows found"); return; } // #codex
        $.ajax({ // #codex
            url: "/diagnosis/lab-report/biochemistry/save/", // #codex
            method: "POST", // #codex
            headers: { "X-CSRFToken": bioCsrfToken() }, // #codex
            contentType: "application/json", // #codex
            data: JSON.stringify({ invoice_id: invoiceId, selected_test_ids: selectedBiochemistryTestIds, selected_test_names: selectedBiochemistryTestIds.map(function (id) { return selectedBiochemistryTestNames[id] || id; }), rows: rows }), // #codex
            success: function (response) { // #codex
                loadResultList(); // #codex
                openPreview(response.preview_url); // #codex
            }, // #codex
            error: function (xhr) { // #codex
                let response = xhr.responseJSON || {}; // #codex
                alert(response.message || "Failed to save result"); // #codex
            } // #codex
        }); // #codex
    }); // #codex

    $(document).on("click", ".bio-test-row", function (event) { // #codex
        saveActiveResultInputs(); // #codex
        selectedBiochemistryTestId = $(this).data("test-id"); // #codex
        let testId = String(selectedBiochemistryTestId); // #codex
        let $checkbox = $(this).find(".bio-test-select"); // #codex
        if (!$(event.target).is(".bio-test-select")) { $checkbox.prop("checked", !$checkbox.prop("checked")); } // #codex
        if ($checkbox.prop("checked")) { // #codex
            if (!selectedBiochemistryTestIds.includes(testId)) { selectedBiochemistryTestIds.push(testId); } // #codex
            selectedBiochemistryTestNames[testId] = $(this).data("test-name") || selectedBiochemistryTestNames[testId] || testId; // #codex
            if (!biochemistryRowsByTest.template) { loadInvoiceBySearch($("#invoiceId").val(), selectedBiochemistryTestId, biochemistryEditMode); } else { renderSelectedResultRows(); } // #codex
        } else { // #codex
            selectedBiochemistryTestIds = selectedBiochemistryTestIds.filter(function (id) { return id !== testId; }); // #codex
            renderSelectedResultRows(); // #codex
        } // #codex
    }); // #codex

    $(document).on("click", ".bio-edit-btn", function () { // #codex
        window.location.href = `/diagnosis/lab-report/biochemistry/add/?invoice_id=${$(this).data("invoice-id")}&edit=1`; // #codex
    }); // #codex

    $(document).on("click", ".bio-preview-btn", function () { // #codex
        openPreview(`/diagnosis/lab-report/biochemistry/preview/${$(this).data("invoice-id")}/`); // #codex
    }); // #codex
}); // #codex
