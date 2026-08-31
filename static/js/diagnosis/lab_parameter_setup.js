let labParameterPage = 1; // #codex
let labParameterLoading = false; // #codex
let labParameterHasMore = true; // #codex
let labParameterMode = "save"; // #codex

function labParameterCsrfToken() { // #codex
    return $("#global_csrf").val() || $("input[name='csrfmiddlewaretoken']").val() || window.csrftoken; // #codex
} // #codex

function labParameterEscape(value) { // #codex
    return $("<div>").text(value || "").html(); // #codex
} // #codex

function notifyLabParameter(message, type) { // #codex
    let toastType = type || "info"; // #codex
    let toastClass = toastType === "success" ? "bg-success" : (toastType === "error" ? "bg-danger" : (toastType === "warning" ? "bg-warning text-dark" : "bg-primary")); // #codex
    let $wrap = $("#labParameterToastWrap"); // #codex
    if (!$wrap.length) { // #codex
        $("body").append('<div id="labParameterToastWrap" style="position:fixed;top:90px;right:24px;z-index:99999;min-width:280px;"></div>'); // #codex
        $wrap = $("#labParameterToastWrap"); // #codex
    } // #codex
    let $toast = $(`<div class="toast align-items-center text-white ${toastClass} border-0 show shadow mb-2" role="alert"><div class="d-flex"><div class="toast-body fw-semibold">${labParameterEscape(message)}</div><button type="button" class="btn-close btn-close-white me-2 m-auto"></button></div></div>`); // #codex
    $wrap.append($toast); // #codex
    $toast.find(".btn-close").on("click", function () { $toast.remove(); }); // #codex
    setTimeout(function () { $toast.fadeOut(250, function () { $(this).remove(); }); }, 3500); // #codex
} // #codex

function resetLabParameterForm() { // #codex
    $("#lab_parameter_id").val(""); // #codex
    $("#serial").val("0"); // #codex
    $("#title").val(""); // #codex
    $("#title_code").val(""); // #codex
    $("#investigation").val(""); // #codex
    $("#investigation_code").val(""); // #codex
    $("#unit").val(""); // #codex
    $("#reff_range").val(""); // #codex
    $("#head_id").val(""); // #codex
    labParameterMode = "save"; // #codex
    $("#saveLabParameterBtn").text("Save").removeClass("btn-primary").addClass("btn-success"); // #codex
} // #codex

function resetLabParameterList() { // #codex
    labParameterPage = 1; // #codex
    labParameterHasMore = true; // #codex
    $("#labParameterTableBody").html(""); // #codex
    loadLabParameters(); // #codex
} // #codex

function loadLabParameterHeads(targetSelector, groupId, categoryId, selectedId, allLabel) { // #codex
    let $target = $(targetSelector); // #codex
    let defaultLabel = allLabel || "-- Optional --"; // #codex
    $target.html(`<option value="">${defaultLabel}</option>`); // #codex
    if (!groupId) { return $.Deferred().resolve().promise(); } // #codex
    return $.ajax({ // #codex
        url: "/diagnosis/lab-report/heads/", // #codex
        method: "GET", // #codex
        data: { group_id: groupId, category_id: categoryId || "" }, // #codex
        success: function (response) { // #codex
            let options = `<option value="">${defaultLabel}</option>`; // #codex
            (response.heads || []).forEach(function (head) { // #codex
                options += `<option value="${head.id}">${labParameterEscape(head.name)}</option>`; // #codex
            }); // #codex
            $target.html(options); // #codex
            if (selectedId) { $target.val(String(selectedId)); } // #codex
        }, // #codex
        error: function () { // #codex
            notifyLabParameter("Failed to load transaction heads", "error"); // #codex
        } // #codex
    }); // #codex
} // #codex

function loadLabParameterCategories(targetSelector, groupId, selectedId, allLabel) { // #codex
    let $target = $(targetSelector); // #codex
    let defaultLabel = allLabel || "-- Select Category --"; // #codex
    let emptyLabel = groupId ? defaultLabel : (targetSelector.indexOf("filter") >= 0 ? defaultLabel : "-- Select Group First --"); // #codex
    $target.html(`<option value="">${emptyLabel}</option>`); // #codex
    if (!groupId) { return $.Deferred().resolve().promise(); } // #codex
    return $.ajax({ // #codex
        url: "/diagnosis/lab-report/categories/", // #codex
        method: "GET", // #codex
        data: { group_id: groupId }, // #codex
        success: function (response) { // #codex
            let options = `<option value="">${defaultLabel}</option>`; // #codex
            (response.categories || []).forEach(function (category) { // #codex
                options += `<option value="${category.id}">${labParameterEscape(category.name)}</option>`; // #codex
            }); // #codex
            $target.html(options); // #codex
            if (selectedId) { $target.val(String(selectedId)); } // #codex
        }, // #codex
        error: function () { // #codex
            notifyLabParameter("Failed to load lab categories", "error"); // #codex
        } // #codex
    }); // #codex
} // #codex

function loadLabParameters() { // #codex
    if (labParameterLoading || !labParameterHasMore) { return; } // #codex
    labParameterLoading = true; // #codex
    $.ajax({ // #codex
        url: "/diagnosis/lab-report/parameters/load/", // #codex
        method: "GET", // #codex
        data: { // #codex
            page: labParameterPage, // #codex
            limit: 20, // #codex
            group_id: $("#filter_group_id").val(), // #codex
            category_id: $("#filter_category_id").val(), // #codex
            head_id: $("#filter_head_id").val(), // #codex
            search: $("#search_lab_parameter").val() // #codex
        }, // #codex
        success: function (response) { // #codex
            let rows = response.lab_parameters || []; // #codex
            if (!rows.length && labParameterPage === 1) { // #codex
                $("#labParameterTableBody").html('<tr><td colspan="12" class="text-center text-muted py-4">No lab parameter found</td></tr>'); // #codex
                labParameterHasMore = false; // #codex
                labParameterLoading = false; // #codex
                return; // #codex
            } // #codex
            if (!rows.length) { // #codex
                labParameterHasMore = false; // #codex
                labParameterLoading = false; // #codex
                return; // #codex
            } // #codex
            let html = ""; // #codex
            rows.forEach(function (row, index) { // #codex
                html += ` 
                    <tr>
                        <td>${((labParameterPage - 1) * 20) + index + 1}</td>
                        <td>${labParameterEscape(row.group_name)}</td>
                        <td>${labParameterEscape(row.category_name)}</td>
                        <td>${labParameterEscape(row.tran_head_name || "-")}</td>
                        <td>${labParameterEscape(row.serial)}</td>
                        <td>${labParameterEscape(row.title)}</td>
                        <td>${labParameterEscape(row.title_code || "-")}</td>
                        <td>${labParameterEscape(row.investigation)}</td>
                        <td>${labParameterEscape(row.investigation_code || "-")}</td>
                        <td>${labParameterEscape(row.unit || "-")}</td>
                        <td>${labParameterEscape(row.reff_range || "-")}</td>
                        <td>
                            <button type="button" class="btn btn-sm btn-warning labParameterEditBtn"
                                data-id="${row.id}"
                                data-group_id="${row.group_id}"
                                data-category_id="${row.category_id}"
                                data-head_id="${row.head_id || ""}"
                                data-serial="${labParameterEscape(row.serial)}"
                                data-title="${labParameterEscape(row.title)}"
                                data-title_code="${labParameterEscape(row.title_code || "")}"
                                data-investigation="${labParameterEscape(row.investigation)}"
                                data-investigation_code="${labParameterEscape(row.investigation_code || "")}"
                                data-unit="${labParameterEscape(row.unit || "")}"
                                data-reff_range="${labParameterEscape(row.reff_range || "")}">Edit</button>
                            <button type="button" class="btn btn-sm btn-danger labParameterDeleteBtn" data-id="${row.id}">Delete</button>
                        </td>
                    </tr>
                `; // #codex
            }); // #codex
            if (labParameterPage === 1) { $("#labParameterTableBody").html(html); } else { $("#labParameterTableBody").append(html); } // #codex
            labParameterPage++; // #codex
            labParameterLoading = false; // #codex
        }, // #codex
        error: function (xhr) { // #codex
            labParameterLoading = false; // #codex
            let response = xhr.responseJSON || {}; // #codex
            notifyLabParameter(response.message || "Failed to load lab parameters", "error"); // #codex
        } // #codex
    }); // #codex
} // #codex

$(document).ready(function () { // #codex
    loadLabParameters(); // #codex

    $("#group_id").on("change", function () { // #codex
        loadLabParameterCategories("#category_id", $("#group_id").val(), null, "-- Select Category --"); // #codex
        loadLabParameterHeads("#head_id", $("#group_id").val(), "", null, "-- Optional --"); // #codex
    }); // #codex

    $("#category_id").on("change", function () { // #codex
        loadLabParameterHeads("#head_id", $("#group_id").val(), $("#category_id").val(), null, "-- Optional --"); // #codex
    }); // #codex

    $("#filter_group_id").on("change", function () { // #codex
        loadLabParameterCategories("#filter_category_id", $("#filter_group_id").val(), null, "All Category").always(function () { // #codex
            loadLabParameterHeads("#filter_head_id", $("#filter_group_id").val(), $("#filter_category_id").val(), null, "All Head"); // #codex
            resetLabParameterList(); // #codex
        }); // #codex
    }); // #codex

    $("#filter_category_id").on("change", function () { // #codex
        loadLabParameterHeads("#filter_head_id", $("#filter_group_id").val(), $("#filter_category_id").val(), null, "All Head"); // #codex
        resetLabParameterList(); // #codex
    }); // #codex

    $("#filter_head_id").on("change", resetLabParameterList); // #codex

    $("#search_lab_parameter").on("input", function () { // #codex
        resetLabParameterList(); // #codex
    }); // #codex

    $("#resetLabParameterBtn").on("click", function () { // #codex
        resetLabParameterForm(); // #codex
    }); // #codex

    $("#labParameterForm").on("submit", function (event) { // #codex
        event.preventDefault(); // #codex
        let url = labParameterMode === "update" ? "/diagnosis/lab-report/parameters/update/" : "/diagnosis/lab-report/parameters/save/"; // #codex
        $.ajax({ // #codex
            url: url, // #codex
            method: "POST", // #codex
            headers: { "X-CSRFToken": labParameterCsrfToken() }, // #codex
            data: $(this).serialize(), // #codex
            success: function (response) { // #codex
                notifyLabParameter(response.message || "Saved successfully", "success"); // #codex
                resetLabParameterForm(); // #codex
                resetLabParameterList(); // #codex
            }, // #codex
            error: function (xhr) { // #codex
                let response = xhr.responseJSON || {}; // #codex
                notifyLabParameter(response.message || "Failed to save lab parameter", "error"); // #codex
            } // #codex
        }); // #codex
    }); // #codex

    $(document).on("click", ".labParameterEditBtn", function () { // #codex
        let data = $(this).data(); // #codex
        $("#lab_parameter_id").val(data.id); // #codex
        $("#group_id").val(data.group_id); // #codex
        $("#serial").val(data.serial); // #codex
        $("#title").val(data.title); // #codex
        $("#title_code").val(data.title_code); // #codex
        $("#investigation").val(data.investigation); // #codex
        $("#investigation_code").val(data.investigation_code); // #codex
        $("#unit").val(data.unit); // #codex
        $("#reff_range").val(data.reff_range); // #codex
        loadLabParameterCategories("#category_id", data.group_id, data.category_id, "-- Select Category --").always(function () { // #codex
            loadLabParameterHeads("#head_id", data.group_id, data.category_id, data.head_id, "-- Optional --"); // #codex
        }); // #codex
        labParameterMode = "update"; // #codex
        $("#saveLabParameterBtn").text("Update").removeClass("btn-success").addClass("btn-primary"); // #codex
        window.scrollTo({ top: 0, behavior: "smooth" }); // #codex
    }); // #codex

    $(document).on("click", ".labParameterDeleteBtn", function () { // #codex
        if (!confirm("Are you sure you want to delete this lab parameter?")) { return; } // #codex
        $.ajax({ // #codex
            url: "/diagnosis/lab-report/parameters/delete/", // #codex
            method: "POST", // #codex
            headers: { "X-CSRFToken": labParameterCsrfToken() }, // #codex
            data: { id: $(this).data("id") }, // #codex
            success: function (response) { // #codex
                notifyLabParameter(response.message || "Deleted successfully", "success"); // #codex
                resetLabParameterList(); // #codex
            }, // #codex
            error: function (xhr) { // #codex
                let response = xhr.responseJSON || {}; // #codex
                notifyLabParameter(response.message || "Failed to delete lab parameter", "error"); // #codex
            } // #codex
        }); // #codex
    }); // #codex

    $(window).on("scroll", function () { // #codex
        if ($(window).scrollTop() + $(window).height() >= $(document).height() - 150) { // #codex
            loadLabParameters(); // #codex
        } // #codex
    }); // #codex
}); // #codex
