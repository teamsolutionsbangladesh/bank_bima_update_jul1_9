$(document).on("keyup change", ".column-filter, .column-filter-select", function () {

    let filters = [];

    $(".column-filter, .column-filter-select").each(function () {
        let col = $(this).data("col");
        let val = $(this).val().toLowerCase();
        filters.push({col, val});
    });

    $("tbody tr").each(function () {
        let row = $(this);
        let show = true;

        filters.forEach(f => {
            if (f.val !== "") {
                let cellText = row.find("td:eq(" + f.col + ")").text().toLowerCase();
                if (!cellText.includes(f.val)) {
                    show = false;
                }
            }
        });

        show ? row.show() : row.hide();
    });
});

// Clear Button
$(document).on("click", ".clearFilter", function () {
    $(".column-filter, .column-filter-select").val("");
    $("tbody tr").show();
});
