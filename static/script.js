window.onload = function () {
  $('[data-toggle="tooltip"]').tooltip();

  function formatDate(date) {
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();
    return `${day}/${month}/${year}`; // For label
  }

  function formatDateForInput(date) {
    // Format to YYYY-MM-DD for Flask
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();
    return `${year}-${month}-${day}`;
  }

  var currentDate = formatDate(new Date());

  $(".due-date-button").datepicker({
    format: "dd/mm/yyyy",
    autoclose: true,
    todayHighlight: true,
    startDate: currentDate,
    orientation: "bottom right",
  });

  $(".due-date-button").on("click", function (event) {
    $(".due-date-button")
      .datepicker("show")
      .on("changeDate", function (dateChangeEvent) {
        const selectedDate = dateChangeEvent.date;
        $(".due-date-button").datepicker("hide");

        // Show in label
        $(".due-date-label").text("Due: " + formatDate(selectedDate));

        // Set hidden input for Flask
        $("#dueDateHidden").val(formatDateForInput(selectedDate));

        // Show clear button
        $("#clearDueDate").removeClass("d-none");
      });
  });

  $("#clearDueDate").on("click", function () {
    $(".due-date-label").text("Not set");
    $("#dueDateHidden").val("");
    $(this).addClass("d-none");
  });
};
