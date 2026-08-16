$(document).ready(function() {

    // ================= CSRF HELPER =================
    function csrfToken() {
        return $('input[name="csrfmiddlewaretoken"]').val() || $("meta[name='csrf-token']").attr("content");
    }

    // ================= ADD COMPANY =================
    $("#addSaveBtn").off("click").on("click", function() {
        let name = $("#addName").val().trim();
        let type = $("#addType").val();

        if (!name) { alert("Company name is required"); return; }
        if (!type) { alert("Company type is required"); return; }

        let formData = new FormData();
        formData.append("company_name", name);
        formData.append("company_email", $("#addEmail").val().trim());
        formData.append("company_phone", $("#addPhone").val().trim());
        formData.append("company_type", type);
        formData.append("address", $("#addAddress").val().trim());
        formData.append("domain", $("#addDomain").val().trim());
        if ($("#addLogo")[0].files[0]) {
            formData.append("logo", $("#addLogo")[0].files[0]);
        }
        formData.append("csrfmiddlewaretoken", csrfToken());

        $.ajax({
            url: "/company-details/create/",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function(res) {
                if (res.success) {
                    $("#companyTableBody").append(`
                        <tr data-id="${res.id}">
                            <td>${res.sl}</td>
                            <td class="cd-company-id">${res.company_id}</td>
                            <td class="cd-name">${res.company_name}</td>
                            <td class="cd-type" data-type-id="${res.company_type_id}">${res.company_type_name}</td>
                            <td class="cd-email">${res.company_email || ""}</td>
                            <td class="cd-phone">${res.company_phone || ""}</td>
                            <td class="cd-address">${res.address || ""}</td>
                            <td class="cd-domain">${res.domain || ""}</td>
                            <td class="cd-logo">${res.logo_url ? `<img src="${res.logo_url}" width="50">` : ""}</td>
                            <td>
                                <button class="btn btn-sm btn-info edit-btn" data-bs-toggle="modal" data-bs-target="#editModal">Edit</button>
                                <button class="btn btn-sm btn-danger delete-btn">Delete</button>
                            </td>
                        </tr>
                    `);
                    $("#addModal").modal('hide');
                    $("#addModal input, #addModal select").val("");
                } else {
                    alert(res.error || "Failed to create company");
                }
            }
        });
    });

    // ================= EDIT MODAL =================
    $(document).off("click", ".edit-btn").on("click", ".edit-btn", function() {
        let row = $(this).closest("tr");

        $("#editId").val(row.data("id"));
        $("#editName").val(row.find(".cd-name").text());
        $("#editEmail").val(row.find(".cd-email").text());
        $("#editPhone").val(row.find(".cd-phone").text());
        $("#editType").val(row.find(".cd-type").data("type-id"));
        $("#editAddress").val(row.find(".cd-address").text());
        $("#editDomain").val(row.find(".cd-domain").text());
        $("#editLogo").val(""); // cannot prefill file inputs
    });

    // ================= UPDATE COMPANY =================
    $("#editSaveBtn").off("click").on("click", function() {
        let id = $("#editId").val();
        let name = $("#editName").val().trim();
        let type = $("#editType").val();

        if (!name) { alert("Company name is required"); return; }
        if (!type) { alert("Company type is required"); return; }

        let formData = new FormData();
        formData.append("company_name", name);
        formData.append("company_email", $("#editEmail").val().trim());
        formData.append("company_phone", $("#editPhone").val().trim());
        formData.append("company_type", type);
        formData.append("address", $("#editAddress").val().trim());
        formData.append("domain", $("#editDomain").val().trim());
        if ($("#editLogo")[0].files[0]) {
            formData.append("logo", $("#editLogo")[0].files[0]);
        }
        formData.append("csrfmiddlewaretoken", csrfToken());

        $.ajax({
            url: `/company-details/update/${id}/`,
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function(res) {
                if (res.success) {
                    let row = $(`tr[data-id='${id}']`);
                    row.find(".cd-name").text(name);
                    row.find(".cd-email").text($("#editEmail").val().trim() || "");
                    row.find(".cd-phone").text($("#editPhone").val().trim() || "");
                    row.find(".cd-type").text($("#editType option:selected").text()).data("type-id", type);
                    row.find(".cd-address").text($("#editAddress").val().trim() || "");
                    row.find(".cd-domain").text($("#editDomain").val().trim() || "");
                    if (res.logo_url) {
                        row.find(".cd-logo").html(`<img src="${res.logo_url}" width="50">`);
                    }
                    $("#editModal").modal('hide');
                } else {
                    alert(res.error || "Update failed");
                }
            }
        });
    });

    // ================= DELETE COMPANY =================
    $(document).off("click", ".delete-btn").on("click", ".delete-btn", function() {
        if (!confirm("Are you sure you want to delete this company?")) return;

        let row = $(this).closest("tr");
        let id = row.data("id");

        $.post(`/company-details/delete/${id}/`, {
            csrfmiddlewaretoken: csrfToken()
        }, function(res) {
            if (res.success) {
                row.remove();
            } else {
                alert(res.error || "Delete failed");
            }
        });
    });

});
