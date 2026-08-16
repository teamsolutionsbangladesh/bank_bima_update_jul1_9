$(document).ready(function() {

    function csrfToken() {
        return $('input[name="csrfmiddlewaretoken"]').val() || $("meta[name='csrf-token']").attr("content");
    }

    function buildTranWithOptions(items, selectedId = "") {
        let html = `<option value="">Select Transaction With</option>`;
        items.forEach(function(item) {
            let selected = String(item.id) === String(selectedId) ? "selected" : "";
            html += `<option value="${item.id}" ${selected}>${item.tran_with_name} (${item.tran_method})</option>`;
        });
        return html;
    }

    function loadTranWithOptions(tranTypeId, targetSelect, selectedId = "") {
        if (!tranTypeId) {
            $(targetSelect).html(`<option value="">Select Transaction With</option>`);
            return;
        }

        $.ajax({
            url: "/users/admin/get-transaction-withs/",
            type: "GET",
            data: { tran_type_id: tranTypeId },
            success: function(res) {
                if (res.success) {
                    $(targetSelect).html(buildTranWithOptions(res.items, selectedId));
                } else {
                    $(targetSelect).html(`<option value="">Select Transaction With</option>`);
                    alert(res.message || "Failed to load Transaction With list");
                }
            },
            error: function(err) {
                console.error(err);
                $(targetSelect).html(`<option value="">Select Transaction With</option>`);
                alert("Failed to load Transaction With list");
            }
        });
    }

    // ============== ADD: tran type change ==============
    $("#addTranType").on("change", function() {
        loadTranWithOptions($(this).val(), "#addTranWith");
    });

    // ============== EDIT: tran type change ==============
    $("#editTranType").on("change", function() {
        loadTranWithOptions($(this).val(), "#editTranWith");
    });

    // ================= ADD ADMIN =================
    $("#addSaveBtn").off("click").on("click", function() {
        let name = $("#addName").val().trim();
        let email = $("#addEmail").val().trim();
        let phone = $("#addPhone").val().trim();
        let tranTypeId = $("#addTranType").val();
        let tranWithId = $("#addTranWith").val();
        let password = $("#addPassword").val();
        let confirmPassword = $("#addConfirmPassword").val();
        let image = $("#addImage")[0].files[0];

        if (!name || !email || !phone || !tranTypeId || !tranWithId || !password || !confirmPassword) {
            alert("All fields are required");
            return;
        }

        if (password !== confirmPassword) {
            alert("Passwords do not match");
            return;
        }

        let formData = new FormData();
        formData.append("name", name);
        formData.append("email", email);
        formData.append("phone", phone);
        formData.append("tran_type_id", tranTypeId);
        formData.append("tran_with_id", tranWithId);
        formData.append("password", password);
        formData.append("confirm_password", confirmPassword);
        if (image) formData.append("logo", image);
        formData.append("csrfmiddlewaretoken", csrfToken());

        $.ajax({
            url: "/users/admin/create/",
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function(res) {
                if (res.success) {
                    let imgTag = res.logo_url ? `<img src="${res.logo_url}" style="height:40px;">` : "No Image";
                    $("#adminTableBody").append(`
                        <tr data-id="${res.id}"
                            data-tran-type-id="${res.tran_type_id || ''}"
                            data-tran-with-id="${res.tran_with_id || ''}">
                            <td>${$("#adminTableBody tr").length + 1}</td>
                            <td class="ad-user-id">${res.user_id}</td>
                            <td class="ad-name">${res.name}</td>
                            <td class="ad-email">${res.email}</td>
                            <td class="ad-phone">${res.phone}</td>
                            <td class="ad-tran-type">${res.tran_type_name || ''}</td>
                            <td class="ad-tran-with">${res.tran_with_name || ''}</td>
                            <td class="ad-image">${imgTag}</td>
                            <td>
                                <button class="btn btn-sm btn-info edit-btn" data-bs-toggle="modal" data-bs-target="#editModal">Edit</button>
                                <button class="btn btn-sm btn-danger delete-btn">Delete</button>
                            </td>
                        </tr>
                    `);

                    $("#addModal").modal('hide');
                    $("#addName, #addEmail, #addPhone, #addPassword, #addConfirmPassword").val("");
                    $("#addTranType").val("");
                    $("#addTranWith").html(`<option value="">Select Transaction With</option>`);
                    $("#addImage").val(null);
                } else {
                    alert(res.message || "Failed to create admin");
                }
            },
            error: function(err) {
                console.error(err);
                alert("AJAX error. Check console.");
            }
        });
    });

    // ================= OPEN EDIT MODAL =================
    $(document).off("click", ".edit-btn").on("click", ".edit-btn", function() {
        let row = $(this).closest("tr");
        let id = row.data("id");
        let name = row.find(".ad-name").text();
        let email = row.find(".ad-email").text();
        let phone = row.find(".ad-phone").text();
        let tranTypeId = row.attr("data-tran-type-id");
        let tranWithId = row.attr("data-tran-with-id");

        $("#editId").val(id);
        $("#editName").val(name);
        $("#editEmail").val(email);
        $("#editPhone").val(phone);
        $("#editPassword, #editConfirmPassword").val("");
        $("#editImage").val(null);
        $("#editTranType").val(tranTypeId || "");

        loadTranWithOptions(tranTypeId, "#editTranWith", tranWithId);
    });

    // ================= UPDATE ADMIN =================
    $("#editSaveBtn").off("click").on("click", function() {
        let id = $("#editId").val();
        let name = $("#editName").val().trim();
        let email = $("#editEmail").val().trim();
        let phone = $("#editPhone").val().trim();
        let tranTypeId = $("#editTranType").val();
        let tranWithId = $("#editTranWith").val();
        let password = $("#editPassword").val();
        let confirmPassword = $("#editConfirmPassword").val();
        let image = $("#editImage")[0].files[0];

        if (!name || !email || !phone || !tranTypeId || !tranWithId) {
            alert("Name, Email, Phone, Tran Type and Transaction With are required");
            return;
        }

        if (password && password !== confirmPassword) {
            alert("Passwords do not match");
            return;
        }

        let formData = new FormData();
        formData.append("name", name);
        formData.append("email", email);
        formData.append("phone", phone);
        formData.append("tran_type_id", tranTypeId);
        formData.append("tran_with_id", tranWithId);
        if (password) formData.append("password", password);
        if (confirmPassword) formData.append("confirm_password", confirmPassword);
        if (image) formData.append("logo", image);
        formData.append("csrfmiddlewaretoken", csrfToken());

        $.ajax({
            url: `/users/admin/update/${id}/`,
            type: "POST",
            data: formData,
            contentType: false,
            processData: false,
            success: function(res) {
                if (res.success) {
                    let row = $(`tr[data-id='${id}']`);
                    row.find(".ad-name").text(res.name);
                    row.find(".ad-email").text(res.email);
                    row.find(".ad-phone").text(res.phone);
                    row.find(".ad-tran-type").text(res.tran_type_name || "");
                    row.find(".ad-tran-with").text(res.tran_with_name || "");
                    row.find(".ad-image").html(res.logo_url ? `<img src="${res.logo_url}" style="height:40px;">` : "No Image");
                    row.attr("data-tran-type-id", res.tran_type_id || "");
                    row.attr("data-tran-with-id", res.tran_with_id || "");

                    $("#editModal").modal('hide');
                } else {
                    alert(res.message || "Update failed");
                }
            },
            error: function(err) {
                console.error(err);
                alert("AJAX error. Check console.");
            }
        });
    });

    // ================= DELETE ADMIN =================
    $(document).off("click", ".delete-btn").on("click", ".delete-btn", function() {
        if (!confirm("Are you sure you want to delete this admin?")) return;

        let row = $(this).closest("tr");
        let id = row.data("id");

        $.ajax({
            url: `/users/admin/delete/${id}/`,
            type: "POST",
            data: { csrfmiddlewaretoken: csrfToken() },
            success: function(res) {
                if (res.success) {
                    row.remove();
                } else {
                    alert(res.message || "Delete failed");
                }
            },
            error: function(err) {
                console.error(err);
                alert("AJAX error. Check console.");
            }
        });
    });

});