$(document).ready(function(){

    // ADD
    $("#addForm").submit(function(e){
        e.preventDefault();
        $.post("/transaction-groupe/store/", $(this).serialize(), function(){
            toastr.success("Transaction Groupe Added");
            $("#addModal").modal("hide");
            location.reload();
        });
    });

    // FETCH
    $(".editBtn").click(function(){
        let id=$(this).data("id");
        $.get("/transaction-groupe/fetch/",{id:id},function(res){
            $("#edit_id").val(res.id);
            $("#edit_name").val(res.tran_groupe_name);
            $("#edit_type").val(res.tran_groupe_type);
            $("#edit_method").val(res.tran_method);
            $("#edit_company").val(res.company);
            $("#editModal").modal("show");
        });
    });

    // UPDATE
    $("#editForm").submit(function(e){
        e.preventDefault();
        $.post("/transaction-groupe/update/", $(this).serialize(), function(){
            toastr.success("Transaction Groupe Updated");
            $("#editModal").modal("hide");
            location.reload();
        });
    });

    // DELETE
    $(".deleteBtn").click(function(){
        let id=$(this).data("id");
        if(confirm("Delete this groupe?")){
            $.post("/transaction-groupe/delete/",{
                id:id,
                csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
            },function(){
                toastr.warning("Transaction Groupe Deleted");
                $("#row"+id).fadeOut();
            });
        }
    });

});
