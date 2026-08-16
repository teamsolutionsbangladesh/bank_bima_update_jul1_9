/**
 * 🩺 ERP Core System: Diagnosis Doctors Registry Operational Master Workflow Script
 * Targets: Real-time Form Processing, Field Mapping Sync, Dynamic Search Filter, & Smooth AJAX Data Drop
 */
$(document).ready(function() {

    // =========================================================================
    // 📋 1. LIVE FRONTEND SEARCH CONTROLLER (LIST REPOSITORY FILTER)
    // =========================================================================
    if ($("#doctorSearchInput").length) {
        $("#doctorSearchInput").on("keyup", function() {
            const incomingQuery = $(this).val().toLowerCase().trim();
            $("#doctorTableBody tr").filter(function() {
                $(this).toggle($(this).text().toLowerCase().indexOf(incomingQuery) > -1);
            });
        });
    }

    // =========================================================================
    // 💾 2. FORM EXECUTION MANAGER (SAVE / UPDATE MULTIPLEXER PIPELINE)
    // =========================================================================
    $("#addForm").on("submit", function(e) {
        e.preventDefault(); 

        // Clear ongoing interface field error trackers validation traces
        $(".name_error, .type_error").text("");
        $("#saveBtn").prop("disabled", true).text("⏳ Processing Operations...");

        const currentCapturedId = $("#doctor_id").val();
        let targetExecutionUrl = "/doctors/add/"; // Aligned with the project routing scope
        
        // Dynamic toggle runtime router pathway for Update
        if (currentCapturedId) {
            targetExecutionUrl = `/doctors/edit/${currentCapturedId}/`; 
        }

        const compiledFormData = $(this).serialize();

        $.ajax({
            url: targetExecutionUrl,
            type: "POST",
            data: compiledFormData,
            success: function(response) {
                $("#saveBtn").prop("disabled", false);
                
                if (response.success) {
                    toastr.success(currentCapturedId ? "🎉 Doctor profiles updated successfully!" : "🌟 Doctor profile registered successfully!");
                    
                    // Flush active input frames to fresh native context
                    $("#addForm")[0].reset();
                    $("#doctor_id").val("");
                    $("#formHeaderTitle").text("New Doctor Registration....");
                    $("#saveBtn").text("💾 Save Doctor").removeClass("btn-warning").addClass("btn-primary");
                    
                    // Sync backend dataset structure reload map delay
                    setTimeout(function() {
                        window.location.reload(); 
                    }, 1000);
                } else {
                    toastr.error(response.error || "❌ Backend processing rejected query.");
                    $("#saveBtn").text(currentCapturedId ? "💾 Update Doctor Profile" : "💾 Save Doctor");
                }
            },
            error: function(xhr) {
                const currentCapturedId = $("#doctor_id").val();
                $("#saveBtn").prop("disabled", false).text(currentCapturedId ? "💾 Update Doctor Profile" : "💾 Save Doctor");
                const errorPayload = xhr.responseJSON;
                
                if (errorPayload && errorPayload.error) {
                    toastr.error(errorPayload.error);
                    // Specific contextual target validation log catch assignment
                    if (errorPayload.error.toLowerCase().includes("name")) {
                        $(".name_error").text(errorPayload.error);
                    } else if (errorPayload.error.toLowerCase().includes("type")) {
                        $(".type_error").text(errorPayload.error);
                    }
                } else {
                    toastr.error(`⚠️ Network interface pipeline fault. Protocol code: ${xhr.status}`);
                }
            }
        });
    });

    // =========================================================================
    // 🔍 3. DYNAMIC INLINE FETCH MANAGER (LOAD RECORD MATRIX INTO FIELDS FOR EDITING)
    // =========================================================================
    $(document).on("click", ".inlineEditBtn, .editBtn", function(e) {
        // Prevent path jump jodi table anchors execution override context throw kore
        if ($(this).is('a') && !$(this).hasClass('inlineEditBtn')) {
            // Standard route path allowed shortcut bypass sequence skip rule matrix
            return;
        }
        e.preventDefault();

        const targetedFetchId = $(this).attr('data-id') || $(this).data('id');
        $("#formHeaderTitle").html('<span class="text-muted">⏳ Injecting remote doctor profile registry logs...</span>');
        
        $.ajax({
            url: "/api/fetch-profile/", // Direct precise endpoint alignment
            type: "GET",
            data: { "id": targetedFetchId },
            success: function(data) {
                // Precision variable mapping matching direct Python Django system layer fields
                $("#doctor_id").val(data.id);
                $("#name").val(data.name);
                $("#specialization").val(data.specialization);
                $("#chamber").val(data.chamber);
                $("#doctor_type").val(data.doctor_type);

                // Re-align structural design parameters mapping layer to Warning State modification state
                $("#formHeaderTitle").html(`<i class="fa-solid fa-user-pen text-warning"></i> Editing Doctor Record: <span class="text-dark">${data.name}</span>`);
                $("#saveBtn").text("💾 Update Doctor Profile").removeClass("btn-primary").addClass("btn-warning");
                
                toastr.info("🎯 Data logs loaded into entry layout component matrix workspace.");
            },
            error: function() {
                $("#formHeaderTitle").text("New Doctor Registration....");
                toastr.error("⚠️ Failed to parse remote data logs registry matrix token identifiers!");
            }
        });
    });

    // =========================================================================
    // 🚨 4. BOOTSTRAP DELETION MODAL INTERCEPTOR & TRIGGER DISPATCHER 
    // =========================================================================
    $(document).on('click', '.open-delete-modal-btn', function() {
        const currentTargetId = $(this).attr('data-id') || $(this).data('id');
        const currentTargetName = $(this).attr('data-name') || $(this).data('name');
        
        // Pass targeted identity metrics safely onto confirmation destination block layers
        $("#modalExecuteDeleteBtn").attr('data-id', currentTargetId);
        $("#targetDoctorNameDisplay").text(`Target Registry Profile: "${currentTargetName}"`);
    });

    // =========================================================================
    // 🗑️ 5. SECURE AJAX DELETE MASTER SYSTEM STREAM CHANNELS (MODAL TRACE TRIGGER)
    // =========================================================================
    $(document).on('click', '#modalExecuteDeleteBtn', function(e) {
        e.preventDefault();
        
        const runtimeTargetId = $(this).attr('data-id');
        // Fallback catch to retrieve the token safely
        const systemicCsrfToken = $("#global_csrf").val() || $("input[name=csrfmiddlewaretoken]").val();

        if (!runtimeTargetId) {
            toastr.error("⚠️ System Failure: Operation execution blocked, target identity missing!");
            return;
        }

        $.ajax({
            url: `/doctors/delete/${runtimeTargetId}/`,
            type: "POST",
            data: {
                "csrfmiddlewaretoken": systemicCsrfToken
            },
            success: function(response) {
                // Shut down active overlay template component trace
                $("#deleteConfirmModal").modal('hide');
                
                if (response.success) {
                    toastr.success("🗑️ Record dropped out from active database schema!");
                    
                    // Smoothly dissolve the selected line configuration component array container 
                    $(`#row${runtimeTargetId}`).fadeOut(400, function() {
                        $(this).remove();
                        recalculateSerialNumbers(); // Serial tracker sync reset
                    });
                } else {
                    toastr.error("❌ Operations Conflict Exception: " + response.error);
                }
            },
            error: function(xhr) {
                $("#deleteConfirmModal").modal('hide');
                toastr.error("⚠️ Application gateway execution error, validation path mapping crashed.");
            }
        });
    });

    // 🔢 6. RUNTIME RE-INDEX SERIAL NUMBERS HELPER
    function recalculateSerialNumbers() {
        let activeRows = $("#doctorTableBody tr").not(".no-data-row");
        if (activeRows.length === 0) {
            $("#doctorTableBody").html(`
                <tr class="no-data-row">
                    <td colspan="6" class="text-center py-4 text-muted">
                        <i class="fa-solid fa-triangle-exclamation"></i> No doctor records found in database.
                    </td>
                </tr>
            `);
        } else {
            activeRows.each(function(index) {
                $(this).find("td:first").text(index + 1);
            });
        }
    }

});