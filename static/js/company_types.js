$(document).ready(function() {

    // ================= CSRF HELPER =================
    function csrfToken() {
        return $('input[name="csrfmiddlewaretoken"]').val() || $("meta[name='csrf-token']").attr("content");
    }

    // ================= ADD =================
    $("#addSaveBtn").off("click").on("click", function() {
        let name = $("#addName").val().trim();
        let status = $("#addStatus").val();

        if (!name) {
            alert("Name is required");
            return;
        }

        $.post("/company-types/create/", {
            name: name,
            status: status,
            csrfmiddlewaretoken: csrfToken()
        }, function(res) {
            if (res.success) {
                $("#companyTypeTableBody").append(`
                    <tr data-id="${res.id}">
                        <td>${res.id}</td>
                        <td class="ct-name">${res.name}</td>
                        <td class="ct-status">${status == 1 ? "Active" : "Inactive"}</td>
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
                alert(res.message || res.error || "Failed to create company type");
            }
        });
    });

    // ================= EDIT MODAL =================
    $(document).off("click", ".edit-btn").on("click", ".edit-btn", function() {
        let row = $(this).closest("tr");
        let id = row.data("id");
        let name = row.find(".ct-name").text();
        let status = row.find(".ct-status").text().trim() === "Active" ? 1 : 0;

        $("#editId").val(id);
        $("#editName").val(name);
        $("#editStatus").val(status);
    });

    // ================= UPDATE =================
    $("#editSaveBtn").off("click").on("click", function() {
        let id = $("#editId").val();
        let name = $("#editName").val().trim();
        let status = $("#editStatus").val();

        if (!name) {
            alert("Name is required");
            return;
        }

        $.post(`/company-types/update/${id}/`, {
            name: name,
            status: status,
            csrfmiddlewaretoken: csrfToken()
        }, function(res) {
            if (res.success) {
                let row = $(`tr[data-id='${id}']`);
                row.find(".ct-name").text(name);
                row.find(".ct-status").text(status == 1 ? "Active" : "Inactive");
                $("#editModal").modal('hide');
            } else {
                alert(res.message || res.error || "Update failed");
            }
        });
    });

    // ================= DELETE =================
    $(document).off("click", ".delete-btn").on("click", ".delete-btn", function() {
        if (!confirm("Are you sure you want to delete this company type?")) return;

        let row = $(this).closest("tr");
        let id = row.data("id");

        $.post(`/company-types/delete/${id}/`, {
            csrfmiddlewaretoken: csrfToken()
        }, function(res) {
            if (res.success) {
                row.remove();
            } else {
                alert(res.message || res.error || "Delete failed");
            }
        });
    });

});
