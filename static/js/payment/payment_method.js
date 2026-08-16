$(document).ready(function(){

// ADD
$("#addForm").submit(function(e){
    e.preventDefault();
    $.post("/payment-method/store/", $(this).serialize(), function(){
        toastr.success("Payment Method Added");
        $("#addModal").modal("hide");
        location.reload();
    });
});

// FETCH
$(".editBtn").click(function(){
    let id=$(this).data("id");
    $.get("/payment-method/fetch/",{id:id},function(res){
        $("#edit_id").val(res.id);
        $("#edit_name").val(res.name);
        $("#editModal").modal("show");
    });
});

// UPDATE
$("#editForm").submit(function(e){
    e.preventDefault();
    $.post("/payment-method/update/", $(this).serialize(), function(){
        toastr.success("Payment Method Updated");
        $("#editModal").modal("hide");
        location.reload();
    });
});

// DELETE
$(".deleteBtn").click(function(){
    let id=$(this).data("id");
    if(confirm("Delete this payment method?")){
        $.post("/payment-method/delete/",{
            id:id,
            csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val()
        },function(){
            toastr.warning("Payment Method Deleted");
            $("#row"+id).fadeOut();
        });
    }
});

});
