$(document).ready(function(){

function getCSRF(){
    return $('meta[name="csrf-token"]').attr('content');
}

// ADD
 $("#addForm").on("submit", function(e){
        e.preventDefault();
        $.ajax({
            url: "/bank/store/",  // Django view url
            type: "POST",
            data: $(this).serialize(),
            success: function(res){
                if(res.success){
                    // Show alert with Bank ID
                    alert("Bank Created!\nBank ID: " + res.bank_id);

                    // Hide Add Modal
                    $("#addModal").modal("hide");

                    // Reset form
                    $("#addForm")[0].reset();

                    // Reload table/page to show new bank
                    location.reload();
                } else {
                    alert(res.message || "Something went wrong!");
                }
            },
            error: function(err){
                console.log(err);
                alert("Server Error!");
            }
        });
    });

// FETCH EDIT
$(".editBtn").click(function(){
    var id = $(this).data("id");

    $.ajax({
        url: "/bank/fetch/",
        type: "GET",
        data: {id: id},
        success: function(res){
            $("#edit_id").val(res.id);
            $("#edit_name").val(res.name);
            $("#edit_email").val(res.email);
            $("#edit_phone").val(res.phone);
            $("#edit_address").val(res.address);
            $("#edit_loc").val(res.loc);       // location id
            $("#edit_division").val(res.division);  // <-- set division

            $("#editModal").modal("show");
        }
    });
});


// UPDATE
$("#editForm").on("submit", function(e){
    e.preventDefault();
    $.ajax({
        url: "/bank/update/",
        type: "POST",
        data: $(this).serialize(),
        headers: {'X-CSRFToken': getCSRF()},
        success: function(){
            toastr.success("Bank Updated Successfully");
            $("#editModal").modal("hide");
            setTimeout(() => location.reload(), 600);
        }
    });
});
// DELETE
$(document).on("click",".deleteBtn",function(){
    let id=$(this).data("id");

    if(confirm("Delete this bank?")){
        $.ajax({
            url:"/bank/delete/",
            type:"POST",
            data:{
                id: id,
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()  // <-- CSRF here
            },
            success:function(){
                toastr.warning("Bank Deleted");
                $("#row"+id).fadeOut();
            }
        });
    }
});
});
