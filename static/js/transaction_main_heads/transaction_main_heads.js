$(document).ready(function(){

    // FETCH
    $(".editBtn").click(function(){
        let id=$(this).data("id");
        $.get("/transaction-head/fetch/",{id:id},function(res){
            $("#edit_id").val(res.id);
            $("#edit_name").val(res.type_name);
            $("#editModal").modal("show");
        });
    });

    // UPDATE
    $("#editForm").submit(function(e){
        e.preventDefault();
        $.post("/transaction-head/update/", $(this).serialize(), function(){
            toastr.success("Main Head Updated");
            $("#editModal").modal("hide");
            location.reload();
        });
    });

    // DELETE
    $(".deleteBtn").click(function(){
        let id=$(this).data("id");
        if(confirm("Delete this head?")){
            $.post("/transaction-head/delete/",{
                id:id,
                csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
            },function(){
                toastr.warning("Main Head Deleted");
                $("#row"+id).fadeOut();
            });
        }
    });
    
    

    
});
