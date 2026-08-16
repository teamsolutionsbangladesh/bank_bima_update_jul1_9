/**
 * 📦 ERP Core System: Sales Representative Core Registry Master Pipeline Script
 */
$(document).ready(function() {

    // 📋 1. LIVE REPOSITORY SEARCH CONTROLLER
    if ($("#srSearchInput").length) {
        $("#srSearchInput").on("keyup", function() {
            const incomingQuery = $(this).val().toLowerCase().trim();
            $("#srTableBody tr").filter(function() {
                $(this).toggle($(this).text().toLowerCase().indexOf(incomingQuery) > -1);
            });
        });
    }

    // 💾 2. FORM EXECUTION MANAGER (SAVE / UPDATE PIPELINEMULTIPLEXER)
    $("#addForm").on("submit", function(e) {
        e.preventDefault(); 
        $(".name_error").text("");
        $("#saveBtn").prop("disabled", true).text("⏳ Processing Operations...");

        const currentCapturedId = $("#sr_id").val();
        let targetExecutionUrl = "/representatives/sr/add/"; 
        
        if (currentCapturedId) {
            targetExecutionUrl = `/representatives/sr/edit/${currentCapturedId}/`; 
        }

        const compiledFormData = $(this).serialize();

        $.ajax({
            url: targetExecutionUrl,
            type: "POST",
            data: compiledFormData,
            success: function(response) {
                $("#saveBtn").prop("disabled", false);
                if (response.success) {
                    toastr.success(currentCapturedId ? "🎉 Representative profiles updated successfully!" : "🌟 SR profile registered successfully!");
                    $("#addForm")[0].reset();
                    $("#sr_id").val("");
                    $("#formHeaderTitle").text("New SR Registration....");
                    $("#saveBtn").text("💾 Save SR Agent").removeClass("btn-warning").addClass("btn-primary");
                    
                    setTimeout(function() { window.location.reload(); }, 1000);
                } else {
                    toastr.error(response.error || "❌ Backend processing rejected query.");
                    $("#saveBtn").text(currentCapturedId ? "💾 Update SR Record" : "💾 Save SR Agent");
                }
            },
            error: function(xhr) {
                const currentCapturedId = $("#sr_id").val();
                $("#saveBtn").prop("disabled", false).text(currentCapturedId ? "💾 Update SR Record" : "💾 Save SR Agent");
                const errorPayload = xhr.responseJSON;
                if (errorPayload && errorPayload.error) {
                    toastr.error(errorPayload.error);
                    if (errorPayload.error.toLowerCase().includes("name")) {
                        $(".name_error").text(errorPayload.error);
                    }
                } else {
                    toastr.error(`⚠️ Network pipeline interface fault. Code: ${xhr.status}`);
                }
            }
        });
    });

    // 🔍 3. DYNAMIC INLINE FETCH MANAGER
    $(document).on("click", ".inlineEditBtn, .editBtn", function(e) {
        if ($(this).is('a') && !$(this).hasClass('inlineEditBtn')) { return; }
        e.preventDefault();

        const targetedFetchId = $(this).attr('data-id') || $(this).data('id');
        $("#formHeaderTitle").html('<span class="text-muted">⏳ Injecting remote agent profile registry logs...</span>');
        
        $.ajax({
            url: "/representatives/api/fetch-sr-profile/", 
            type: "GET",
            data: { "id": targetedFetchId },
            success: function(data) {
                $("#sr_id").val(data.id);
                $("#name").val(data.name);
                $("#company_name").val(data.company_name);
                $("#commission_percentage").val(data.commission_percentage);

                $("#formHeaderTitle").html(`<i class="fa-solid fa-user-pen text-warning"></i> Editing SR Record: <span class="text-dark">${data.name}</span>`);
                $("#saveBtn").text("💾 Update SR Record").removeClass("btn-primary").addClass("btn-warning");
                toastr.info("🎯 Data logs loaded into workspace grid layout panel.");
            },
            error: function() {
                $("#formHeaderTitle").text("New SR Registration....");
                toastr.error("⚠️ Failed to parse remote data logs registry identifiers!");
            }
        });
    });

    // 🚨 4. INTERCEPTOR & DELETION MODAL TRIGGER
    $(document).on('click', '.open-delete-modal-btn', function() {
        const currentTargetId = $(this).attr('data-id') || $(this).data('id');
        const currentTargetName = $(this).attr('data-name') || $(this).data('name');
        $("#modalExecuteDeleteBtn").attr('data-id', currentTargetId);
        $("#targetSRNameDisplay").text(`Target Registry Profile: "${currentTargetName}"`);
    });

    // 🗑️ 5. SECURE AJAX DELETE MASTER SYSTEM STREAM CHANNELS
    $(document).on('click', '#modalExecuteDeleteBtn', function(e) {
        e.preventDefault();
        const runtimeTargetId = $(this).attr('data-id');
        const systemicCsrfToken = $("#global_csrf").val() || $("input[name=csrfmiddlewaretoken]").val();

        if (!runtimeTargetId) {
            toastr.error("⚠️ System Failure: Target identity identifier tracking missing!");
            return;
        }

        $.ajax({
            url: `/representatives/sr/delete/${runtimeTargetId}/`,
            type: "POST",
            data: { "csrfmiddlewaretoken": systemicCsrfToken },
            success: function(response) {
                $("#deleteConfirmModal").modal('hide');
                if (response.success) {
                    toastr.success("🗑️ Record dropped out from active database schema!");
                    $(`#row${runtimeTargetId}`).fadeOut(400, function() {
                        $(this).remove();
                        recalculateSerialNumbers();
                    });
                } else {
                    toastr.error("❌ Operations Conflict Exception: " + response.error);
                }
            },
            error: function() {
                $("#deleteConfirmModal").modal('hide');
                toastr.error("⚠️ Application gateway validation path mapping crashed.");
            }
        });
    });

    // 🔢 6. RUNTIME RE-INDEX SERIAL NUMBERS HELPER
    function recalculateSerialNumbers() {
        let activeRows = $("#srTableBody tr").not(".no-data-row");
        if (activeRows.length === 0) {
            $("#srTableBody").html(`
                <tr class="no-data-row">
                    <td colspan="6" class="text-center py-4 text-muted">No sales representative records found.</td>
                </tr>
            `);
        } else {
            activeRows.each(function(index) {
                $(this).find("td:first").text(index + 1);
            });
        }
    }
});