define(['jquery','bootstrap_popover', 'bootstrap'], function ($) {
$(document).ready(function () {
 
 
        console.log("---- NEW details_graph_bar.js ---") ;  

 

        // Affiche dans la modal la liste des élèves du groupe sélectionné
        $('.get_details_bar').on('click', function (event) {
            let date    = $(this).attr("data-date");
            let student    = $(this).attr("data-student_id");
            let month       = $(this).attr("data-month");
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();



            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'student_id': student,
                        'date'      : date,
                        'month'     : month,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../ajax_get_details_graph/",
                    success: function (data) {
                        $('#body_detail_bar').html(data.html);
                        $('#title_detail_bar').html(data.this_date);
                    }
                }
            )
        });
 
 




    });
});
 
