// Add Corporate
$("#addForm").on("submit", function(e){
    e.preventDefault();
    $.ajax({
        url: "/corporate/store/",
        type: "POST",
        data: $(this).serialize(),
        headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()},
        success: function(res){
            if(res.success){
                toastr.success("Corporate Added Successfully");
                $("#addModal").modal("hide");
                $("#addForm")[0].reset();
                setTimeout(()=>location.reload(), 600);
            }
        }
    });
});

// Edit button click
$(".editBtn").click(function(){
    let id = $(this).data("id");
    $.ajax({
        url: "/corporate/fetch/",
        type: "GET",
        data: {id:id},
        success: function(res){
            $("#edit_id").val(res.id);
            $("#edit_name").val(res.name);
            $("#edit_discount").val(res.discount);
            $("#editModal").modal("show");
        }
    });
});

// Update
$("#editForm").on("submit", function(e){
    e.preventDefault();
    $.ajax({
        url: "/corporate/update/",
        type: "POST",
        data: $(this).serialize(),
        headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()},
        success: function(res){
            toastr.success("Corporate Updated Successfully");
            $("#editModal").modal("hide");
            setTimeout(()=>location.reload(),600);
        }
    });
});

// Delete
$(document).on("click",".deleteBtn", function(){
    let id = $(this).data("id");
    if(confirm("Delete this corporate?")){
        $.ajax({
            url: "/corporate/delete/",
            type: "POST",
            data: {id:id, csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()},
            success: function(){
                toastr.warning("Corporate Deleted");
                $("#row"+id).fadeOut();
            }
        });
    }
});
