$(document).ready(function(){

    // Add Store
    $("#addForm").submit(function(e){
        e.preventDefault();
        $.ajax({
            url: "/store/store/",
            type: "POST",
            data: $(this).serialize(),
            success: function(res){
                if(res.success){
                    toastr.success("Store Added Successfully");
                    $("#addModal").modal("hide");
                    $("#addForm")[0].reset();
                    location.reload();
                }
            }
        });
    });

    // Edit modal open
    $(".editBtn").click(function(){
        let id = $(this).data("id");
        $.ajax({
            url: "/store/fetch/",
            type: "GET",
            data: {id:id},
            success: function(res){
                $("#edit_id").val(res.id);
                $("#edit_name").val(res.store_name);
                $("#edit_division").val(res.division);
                $("#edit_location").val(res.location_id);
                $("#edit_address").val(res.address);
                $("#editModal").modal("show");
            }
        });
    });

    // Update Store
    $("#editForm").submit(function(e){
        e.preventDefault();
        $.ajax({
            url: "/store/update/",
            type: "POST",
            data: $(this).serialize(),
            success: function(res){
                if(res.success){
                    toastr.success("Store Updated Successfully");
                    $("#editModal").modal("hide");
                    location.reload();
                }
            }
        });
    });

    // Delete Store
    $(".deleteBtn").click(function(){
        let id = $(this).data("id");
        if(confirm("Delete this store?")){
            $.ajax({
                url:"/store/delete/",
                type:"POST",
                data:{
                    id:id,
                    csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
                },
                success:function(res){
                    if(res.success){
                        toastr.warning("Store Deleted");
                        $("#row"+id).fadeOut();
                    }
                }
            });
        }
    });

});
