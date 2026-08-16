$(document).ready(function(){

// ADD
$("#addForm").on("submit", function(e){
    e.preventDefault();

    $.ajax({
        url: "/location/store/",
        type: "POST",
        data: $(this).serialize(),
        success:function(){
            toastr.success("Location Added Successfully");
            $("#addModal").modal("hide");
            setTimeout(()=>location.reload(), 800);
        },
        error:function(){
            toastr.error("Failed to Add Location");
        }
    });
});

// OPEN EDIT MODAL
$(document).on("click",".editBtn",function(){
    let id = $(this).data("id");  // must exist in button

    if(!id) return toastr.error("No ID found!");

    $.ajax({
        url:"/location/fetch/",
        type:"GET",
        data:{id:id},   // <-- this is critical
        success:function(res){
            $("#edit_id").val(res.id);
            $("#edit_division").val(res.division);
            $("#edit_district").val(res.district);
            $("#edit_upazila").val(res.upazila);
            $("#editModal").modal("show");
        }
    });
});
// UPDATE
$("#editForm").on("submit",function(e){
    e.preventDefault();

    $.ajax({
        url:"/location/update/",
        type:"POST",
        data:$(this).serialize(),
        success:function(){
            toastr.success("Location Updated Successfully");
            $("#editModal").modal("hide");
            setTimeout(()=>location.reload(), 800);
        }
    });
});

// DELETE
$(document).on("click",".deleteBtn",function(){
    let id=$(this).data("id");

    if(confirm("Delete this location?")){
        $.ajax({
            url:"/location/delete/",
            type:"POST",
            data:{
                id:id,
                csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
            },
            success:function(){
                toastr.warning("Location Deleted");
                $("#row"+id).fadeOut();
            }
        });
    }
});

});
