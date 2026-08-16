$(document).ready(function () { // #codex
    function csrfToken() { // #codex
        return $("#global_csrf").val() || $("input[name='csrfmiddlewaretoken']").val(); // #codex
    } // #codex

    function selectedDoctorId() { // #codex
        return $("#referralDoctor").val(); // #codex
    } // #codex

    function selectedGroupId() { // #codex
        return $("#referralGroup").val(); // #codex
    } // #codex

    const referralTestsUrl = $("#referralTestsUrl").val() || "/diagnosis/referral/tests/"; // #codex
    const referralSavedGroupsUrl = $("#referralSavedGroupsUrl").val() || "/diagnosis/referral/saved-groups/"; // #codex
    const referralSaveUrl = $("#referralSaveUrl").val() || "/diagnosis/referral/save/"; // #codex
    const referralCopyUrl = $("#referralCopyUrl").val() || "/diagnosis/referral/copy/"; // #codex
    const referralSuccessMessage = $("#referralSuccessMessage").val() || "Referral setup updated successfully"; // #codex
    const referralCopySuccessMessage = $("#referralCopySuccessMessage").val() || "Referral setup copied successfully"; // #codex
    const referralProviderLabel = $("#referralProviderLabel").val() || "Doctor"; // #codex
    const referralProviderMetaLabel = $("#referralProviderMetaLabel").val() || "Specialization"; // #codex
    const referralProviderExtraLabel = $("#referralProviderExtraLabel").val() || "Chamber"; // #codex

    function notify(message, type) { // #codex
        let toastType = type || "info"; // #codex
        let toastClass = toastType === "success" ? "bg-success" : (toastType === "error" ? "bg-danger" : (toastType === "warning" ? "bg-warning text-dark" : "bg-primary")); // #codex
        let $toastWrap = $("#referralToastWrap"); // #codex
        if (!$toastWrap.length) { // #codex
            $("body").append('<div id="referralToastWrap" style="position:fixed;top:90px;right:24px;z-index:99999;min-width:280px;"></div>'); // #codex
            $toastWrap = $("#referralToastWrap"); // #codex
        } // #codex
        let $toast = $(`<div class="toast align-items-center text-white ${toastClass} border-0 show shadow mb-2" role="alert"><div class="d-flex"><div class="toast-body fw-semibold">${message}</div><button type="button" class="btn-close btn-close-white me-2 m-auto"></button></div></div>`); // #codex
        $toastWrap.append($toast); // #codex
        $toast.find(".btn-close").on("click", function () { $toast.remove(); }); // #codex
        setTimeout(function () { $toast.fadeOut(250, function () { $(this).remove(); }); }, 4500); // #codex
    } // #codex

    let savedToastMessage = sessionStorage.getItem("referralSetupToast"); // #codex
    if (savedToastMessage) { // #codex
        sessionStorage.removeItem("referralSetupToast"); // #codex
        notify(savedToastMessage, "success"); // #codex
    } // #codex

    let pendingConfirmAction = null; // #codex
    let referralGroupsLoaded = false; // #codex

    function openConfirmModal(title, message, action) { // #codex
        pendingConfirmAction = action; // #codex
        $("#referralConfirmTitle").text(title); // #codex
        $("#referralConfirmMessage").text(message); // #codex
        $("#referralConfirmModal").modal("show"); // #codex
    } // #codex

    $("#referralConfirmYesBtn").on("click", function () { // #codex
        $("#referralConfirmModal").modal("hide"); // #codex
        if (typeof pendingConfirmAction === "function") { pendingConfirmAction(); } // #codex
        pendingConfirmAction = null; // #codex
    }); // #codex

    $(".referral-doctor-select").select2({ width: "100%" }); // #codex

    function loadGroups() { // #codex
        $.get("/diagnosis/referral/groups/", function (res) { // #codex
            let options = '<option value="">-- Select Group --</option>'; // #codex
            (res.groups || []).forEach(function (group) { // #codex
                options += `<option value="${group.id}">${group.name}</option>`; // #codex
            }); // #codex
            $("#referralGroup").html(options); // #codex
            referralGroupsLoaded = true; // #codex
            $("#referralGroup").trigger("referral:groups-loaded"); // #codex
        }).fail(function () { // #codex
            notify("Failed to load diagnosis groups", "error"); // #codex
        }); // #codex
    } // #codex

    function renderEmpty(message) { // #codex
        $("#referralTestBody").html(`<tr><td colspan="5" class="text-center text-muted py-4">${message}</td></tr>`); // #codex
    } // #codex

    function clearReferralForm() { // #codex
        $("#referralDoctor").val("").trigger("change.select2"); // #codex
        $("#copySourceDoctor").val("").trigger("change.select2"); // #codex
        $("#referralGroup").val(""); // #codex
        $("#globalRateType").val("tk"); // #codex
        $("#globalRate").val(""); // #codex
        $("#selectAllTests").prop("checked", false); // #codex
        $("#selectedDoctorName").text(`No ${referralProviderLabel} selected`); // #codex
        $("#selectedDoctorMeta").text("-"); // #codex
        renderEmpty("Select doctor and group"); // #codex
    } // #codex

    function refreshReferralPage(message) { // #codex
        clearReferralForm(); // #codex
        sessionStorage.setItem("referralSetupToast", message); // #codex
        window.location.href = window.location.pathname; // #codex
    } // #codex

    function loadTests() { // #codex
        let docId = selectedDoctorId(); // #codex
        let groupId = selectedGroupId(); // #codex
        if (!docId || !groupId) { renderEmpty("Select doctor and group"); return; } // #codex

        $.get(referralTestsUrl, { doc_id: docId, group_id: groupId }, function (res) { // #codex
            let tests = res.tests || []; // #codex
            if (!tests.length) { renderEmpty("No test found under this group"); return; } // #codex
            let rows = ""; // #codex
            tests.forEach(function (test) { // #codex
                let checked = Number(test.selected || 0) === 1 ? "checked" : ""; // #codex
                let refType = test.ref_type || "tk"; // #codex
                rows += ` 
                    <tr data-head-id="${test.id}"> 
                        <td class="text-center"><input type="checkbox" class="form-check-input test-check" ${checked}></td>
                        <td>${test.name || "-"}</td>
                        <td class="text-end">${Number(test.mrp || 0).toFixed(2)}</td>
                        <td>
                            <select class="form-select form-select-sm row-ref-type">
                                <option value="tk" ${refType === "tk" ? "selected" : ""}>Tk</option>
                                <option value="percent" ${refType === "percent" ? "selected" : ""}>%</option>
                            </select>
                        </td>
                        <td><input type="number" step="0.01" min="0" class="form-control form-control-sm row-ref-rate" value="${Number(test.ref_rate || 0)}"></td>
                    </tr>`; // #codex
            }); // #codex
            $("#referralTestBody").html(rows); // #codex
            $("#selectAllTests").prop("checked", tests.every(function (test) { return Number(test.selected || 0) === 1; })); // #codex
            let firstSaved = tests.find(function (test) { return Number(test.selected || 0) === 1; }); // #codex
            if (firstSaved) { // #codex
                $("#globalRateType").val(firstSaved.ref_type || "tk"); // #codex
                $("#globalRate").val(Number(firstSaved.ref_rate || 0)); // #codex
            } // #codex
        }).fail(function (xhr) { // #codex
            let res = xhr.responseJSON || {}; // #codex
            notify(res.message || "Failed to load tests", "error"); // #codex
        }); // #codex
    } // #codex

    function loadSavedSetupForDoctor(docId) { // #codex
        if (!docId) { $("#referralGroup").val(""); renderEmpty(`Select ${referralProviderLabel} and group`); return; } // #codex
        $.get(referralSavedGroupsUrl, { doc_id: docId }, function (res) { // #codex
            let groups = res.groups || []; // #codex
            if (!groups.length) { $("#referralGroup").val(""); renderEmpty(`No saved referral setup found for this ${referralProviderLabel}`); return; } // #codex
            $("#referralGroup").val(groups[0].group_id); // #codex
            loadTests(); // #codex
        }).fail(function (xhr) { // #codex
            let res = xhr.responseJSON || {}; // #codex
            notify(res.message || "Failed to load saved referral setup", "error"); // #codex
        }); // #codex
    } // #codex

    $("#referralDoctor").on("change", function () { // #codex
        let option = $(this).find("option:selected"); // #codex
        let name = option.data("name") || `No ${referralProviderLabel} selected`; // #codex
        let specialization = option.data("specialization") || "-"; // #codex
        let chamber = option.data("chamber") || "-"; // #codex
        $("#selectedDoctorName").text(name); // #codex
        $("#selectedDoctorMeta").text(`${referralProviderMetaLabel}: ${specialization} | ${referralProviderExtraLabel}: ${chamber}`); // #codex
        if (referralGroupsLoaded) { loadSavedSetupForDoctor(selectedDoctorId()); return; } // #codex
        $("#referralGroup").one("referral:groups-loaded", function () { loadSavedSetupForDoctor(selectedDoctorId()); }); // #codex
    }); // #codex

    $("#referralGroup").on("change", loadTests); // #codex

    $("#selectAllTests").on("change", function () { // #codex
        $(".test-check").prop("checked", $(this).is(":checked")); // #codex
    }); // #codex

    $("#applyRateBtn").on("click", function () { // #codex
        let rateType = $("#globalRateType").val(); // #codex
        let rate = $("#globalRate").val() || 0; // #codex
        $(".test-check:checked").each(function () { // #codex
            let row = $(this).closest("tr"); // #codex
            row.find(".row-ref-type").val(rateType); // #codex
            row.find(".row-ref-rate").val(rate); // #codex
        }); // #codex
    }); // #codex

    function submitReferralSetup(docId, groupId, rows) { // #codex
        $.ajax({ // #codex
            url: referralSaveUrl, // #codex
            method: "POST", // #codex
            headers: { "X-CSRFToken": csrfToken() }, // #codex
            contentType: "application/json", // #codex
            data: JSON.stringify({ doc_id: docId, group_id: groupId, rows: rows }), // #codex
            success: function () { refreshReferralPage(referralSuccessMessage); }, // #codex
            error: function (xhr) { // #codex
                let res = xhr.responseJSON || {}; // #codex
                notify(res.message || "Failed to save referral setup", "error"); // #codex
            } // #codex
        }); // #codex
    } // #codex

    function submitReferralCopy(sourceDocId, targetDocId) { // #codex
        $.ajax({ // #codex
            url: referralCopyUrl, // #codex
            method: "POST", // #codex
            headers: { "X-CSRFToken": csrfToken() }, // #codex
            contentType: "application/json", // #codex
            data: JSON.stringify({ source_doc_id: sourceDocId, target_doc_id: targetDocId }), // #codex
            success: function () { refreshReferralPage(referralCopySuccessMessage); }, // #codex
            error: function (xhr) { // #codex
                let res = xhr.responseJSON || {}; // #codex
                notify(res.message || "Failed to copy referral setup", "error"); // #codex
            } // #codex
        }); // #codex
    } // #codex

    $("#saveReferralBtn").on("click", function () { // #codex
        let docId = selectedDoctorId(); // #codex
        let groupId = selectedGroupId(); // #codex
        if (!docId) { notify(`Please select ${referralProviderLabel}`, "warning"); return; } // #codex
        if (!groupId) { notify("Please select group", "warning"); return; } // #codex

        let rows = []; // #codex
        $("#referralTestBody tr[data-head-id]").each(function () { // #codex
            let row = $(this); // #codex
            rows.push({ // #codex
                tran_head_id: row.data("head-id"), // #codex
                ref_type: row.find(".row-ref-type").val(), // #codex
                ref_rate: row.find(".row-ref-rate").val() || 0, // #codex
                selected: row.find(".test-check").is(":checked") // #codex
            }); // #codex
        }); // #codex

        openConfirmModal("Confirm Referral Update", `Are you sure you want to update this ${referralProviderLabel} referral setup?`, function () { // #codex
            submitReferralSetup(docId, groupId, rows); // #codex
        }); // #codex
    }); // #codex

    $("#copyReferralBtn").on("click", function () { // #codex
        let sourceDocId = $("#copySourceDoctor").val(); // #codex
        let targetDocId = selectedDoctorId(); // #codex
        if (!targetDocId) { notify(`Please select target ${referralProviderLabel} first`, "warning"); return; } // #codex
        if (!sourceDocId) { notify(`Please select source ${referralProviderLabel}`, "warning"); return; } // #codex
        if (sourceDocId === targetDocId) { notify(`Source and target ${referralProviderLabel} cannot be same`, "warning"); return; } // #codex

        openConfirmModal("Confirm Referral Copy", `Are you sure you want to copy referral setup to selected ${referralProviderLabel}?`, function () { // #codex
            submitReferralCopy(sourceDocId, targetDocId); // #codex
        }); // #codex
    }); // #codex

    loadGroups(); // #codex
}); // #codex
