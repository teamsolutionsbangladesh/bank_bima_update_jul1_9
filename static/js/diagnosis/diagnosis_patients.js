/**
 * 🩺 ERP Core System: Diagnosis Patients Registry Operational Master Workflow Script
 * Targets: Real-time Form Processing, Auto BMI, Dynamic Search Filter, & Smooth AJAX Data Drop
 */
$(document).ready(function() {

    // =========================================================================
    // 📋 1. LIVE FRONTEND SEARCH CONTROLLER (LIST REPOSITORY FILTER)
    // =========================================================================
    if ($("#patientSearchInput").length) {
        $("#patientSearchInput").on("keyup", function() {
            const incomingQuery = $(this).val().toLowerCase();
            $("#patientTableBody tr").filter(function() {
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
        $(".name_error, .mobile_error").text("");
        $("#saveBtn").prop("disabled", true).text("⏳ Processing Operations...");

        const currentCapturedId = $("#patient_id").val();
        let targetExecutionUrl = "/diagnosis/patients/store/"; 
        
        // Dynamic toggle runtime router pathway
        if (currentCapturedId) {
            targetExecutionUrl = `/diagnosis/patients/${currentCapturedId}/update/`; 
        }

        const compiledFormData = $(this).serialize();

        $.ajax({
            url: targetExecutionUrl,
            type: "POST",
            data: compiledFormData,
            success: function(response) {
                $("#saveBtn").prop("disabled", false);
                
                if (response.success) {
                    toastr.success(currentCapturedId ? "🎉 Patient logs updated successfully!" : "🌟 Patient profile registered successfully!");
                    
                    // Flush active input frames to fresh native context
                    $("#addForm")[0].reset();
                    $("#patient_id").val("");
                    $("#formHeaderTitle").text("New Patient Registration....");
                    $("#saveBtn").text("💾 Save Patient").removeClass("btn-warning").addClass("btn-primary");
                    
                    // Sync backend dataset structure reload map delay
                    setTimeout(function() {
                        window.location.reload(); 
                    }, 1000);
                } else {
                    toastr.error(response.error || "❌ Backend processing rejected query.");
                    $("#saveBtn").text("💾 Save Patient");
                }
            },
            error: function(xhr) {
                $("#saveBtn").prop("disabled", false).text("💾 Save Patient");
                const errorPayload = xhr.responseJSON;
                
                if (errorPayload && errorPayload.error) {
                    toastr.error(errorPayload.error);
                    // Specific contextual target validation log catch assignment
                    if (errorPayload.error.toLowerCase().includes("name")) {
                        $(".name_error").text(errorPayload.error);
                    } else if (errorPayload.error.toLowerCase().includes("mobile")) {
                        $(".mobile_error").text(errorPayload.error);
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
        $("#formHeaderTitle").html('<span class="text-muted">⏳ Injecting remote patient profile registry logs...</span>');
        
        $.ajax({
            url: "/diagnosis/patients/fetch/",
            type: "GET",
            data: { "id": targetedFetchId },
            success: function(data) {
                // Precision variable mapping matching direct Python Django system layer dictionary keys
                $("#patient_id").val(data.id);
                $("#patient_name").val(data.patient_name);
                $("#father_husband_name").val(data.father_husband_name);
                $("#mother_name").val(data.mother_name);
                $("#dob").val(data.dob);
                $("#age").val(data.age);
                $("#gender").val(data.gender);
                $("#blood_group").val(data.blood_group);
                $("#religion").val(data.religion);
                $("#present_mobile").val(data.present_mobile);
                $("#present_email").val(data.present_email);
                $("#present_address").val(data.present_address);
                $("#weight").val(data.weight);
                $("#height").val(data.height);
                $("#bmi").val(data.bmi);
                $("#cause_visit_dcc").val(data.cause_visit_dcc);

                // Re-align structural design parameters mapping layer to Warning State modification state
                $("#formHeaderTitle").html(`<i class="fa-solid fa-user-pen text-warning"></i> Editing Patient Record: <span class="text-dark">${data.patient_name}</span>`);
                $("#saveBtn").text("💾 Update Patient Profile").removeClass("btn-primary").addClass("btn-warning");
                
                toastr.info("🎯 Data logs loaded into entry layout component matrix workspace.");
            },
            error: function() {
                $("#formHeaderTitle").text("New Patient Registration....");
                toastr.error("⚠️ Failed to parse remote data logs registry matrix token identifiers!");
            }
        });
    });

    // =========================================================================
    // 🧮 4. BMI COMPUTER CORE ARCHITECTURE (AUTOMATED TRACKER MECHANISM)
    // =========================================================================
    $("#weight, #height").on("input", function() {
        const structuralWeight = parseFloat($("#weight").val());
        const structuralHeightCm = parseFloat($("#height").val());

        if (structuralWeight > 0 && structuralHeightCm > 0) {
            const scaleMetersConverted = structuralHeightCm / 100;
            const absoluteComputedBmi = structuralWeight / (scaleMetersConverted * scaleMetersConverted);
            $("#bmi").val(absoluteComputedBmi.toFixed(2)); 
        } else {
            $("#bmi").val("");
        }
    });

    // =========================================================================
    // 🚨 5. BOOTSTRAP DELETION MODAL INTERCEPTOR & TRIGGER DISPATCHER 
    // =========================================================================
    $(document).on('click', '.open-delete-modal-btn', function() {
        const currentTargetId = $(this).attr('data-id') || $(this).data('id');
        const currentTargetName = $(this).attr('data-name') || $(this).data('name');
        
        // Pass targeted identity metrics safely onto confirmation destination block layers
        $("#modalExecuteDeleteBtn").attr('data-id', currentTargetId);
        $("#targetPatientNameDisplay").text(`Target Registry Profile: "${currentTargetName}"`);
    });

    // =========================================================================
    // 🗑️ 6. SECURE AJAX DELETE MASTER SYSTEM STREAM CHANNELS (MODAL TRACE TRIGGER)
    // =========================================================================
    $("#modalExecuteDeleteBtn").on('click', function(e) {
        e.preventDefault();
        
        const runtimeTargetId = $(this).attr('data-id');
        const systemicCsrfToken = $("#global_csrf").val() || $("input[name=csrfmiddlewaretoken]").val();

        if (!runtimeTargetId) {
            toastr.error("⚠️ System Failure: Operation execution blocked, target identity missing!");
            return;
        }

        $.ajax({
            url: `/diagnosis/patients/${runtimeTargetId}/delete/`,
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

});

