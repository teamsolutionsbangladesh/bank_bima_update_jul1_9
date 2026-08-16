$(document).ready(function() {

    // ================= CSRF HELPER =================
    function csrfToken() {
        return $('input[name="csrfmiddlewaretoken"]').val() || $("meta[name='csrf-token']").attr("content");
    }

    // ================= ADD ROLE =================
    $("#addSaveBtn").off("click").on("click", function() {
        let name = $("#addName").val().trim();
        let status = $("#addStatus").val();

        if (!name) {
            alert("Name is required");
            return;
        }

        $.ajax({
            url: "/users/roles/create/",
            type: "POST",
            data: {
                name: name,
                status: status,
                csrfmiddlewaretoken: csrfToken()
            },
            success: function(res) {
                if (res.success) {
                    $("#rolesTableBody").append(`
                        <tr data-id="${res.id}">
                            <td>${res.id}</td>
                            <td class="role-name">${res.name}</td>
                            <td class="role-status">${status == 1 ? "Active" : "Inactive"}</td>
                            <td>
                                <button class="btn btn-sm btn-info edit-btn" data-bs-toggle="modal" data-bs-target="#editModal">Edit</button>
                                <button class="btn btn-sm btn-danger delete-btn">Delete</button>
                            </td>
                        </tr>
                    `);
                    $("#addModal").modal('hide');
                    $("#addName").val("");
                    $("#addStatus").val("1");
                } else {
                    alert(res.message || res.error || "Failed to create role");
                }
            },
            error: function(xhr) {
                alert("CSRF token missing or invalid. Please refresh the page.");
            }
        });
    });

    // ================= EDIT MODAL =================
    $(document).off("click", ".edit-btn").on("click", ".edit-btn", function() {
        let row = $(this).closest("tr");
        let id = row.data("id");
        let name = row.find(".role-name").text();
        let status = row.find(".role-status").text().trim() === "Active" ? 1 : 0;

        $("#editId").val(id);
        $("#editName").val(name);
        $("#editStatus").val(status);
    });

    // ================= UPDATE ROLE =================
    $("#editSaveBtn").off("click").on("click", function() {
        let id = $("#editId").val();
        let name = $("#editName").val().trim();
        let status = $("#editStatus").val();

        if (!name) {
            alert("Name is required");
            return;
        }

        $.ajax({
            url: `/users/roles/update/${id}/`,
            type: "POST",
            data: {
                name: name,
                status: status,
                csrfmiddlewaretoken: csrfToken()
            },
            success: function(res) {
                if (res.success) {
                    let row = $(`tr[data-id='${id}']`);
                    row.find(".role-name").text(name);
                    row.find(".role-status").text(status == 1 ? "Active" : "Inactive");
                    $("#editModal").modal('hide');
                } else {
                    alert(res.message || res.error || "Update failed");
                }
            },
            error: function(xhr) {
                alert("CSRF token missing or invalid. Please refresh the page.");
            }
        });
    });

    // ================= DELETE ROLE =================
    $(document).off("click", ".delete-btn").on("click", ".delete-btn", function() {
        if (!confirm("Are you sure you want to delete this role?")) return;

        let row = $(this).closest("tr");
        let id = row.data("id");

        $.ajax({
            url: `/users/roles/delete/${id}/`,
            type: "POST",
            data: {
                csrfmiddlewaretoken: csrfToken()
            },
            success: function(res) {
                if (res.success) {
                    row.remove();
                } else {
                    alert(res.message || res.error || "Delete failed");
                }
            },
            error: function(xhr) {
                alert("CSRF token missing or invalid. Please refresh the page.");
            }
        });
    });

});
