define(['jquery', 'bootstrap', 'ui', 'ui_sortable'], function ($) {
    $(document).ready(function () { 
        console.log("chargement JS ajax-check_fill.js  OKK");

 
 
//*************************************************************************************************************  
// Correction des réponses à compléter
//************************************************************************************************************* 
  
    $(document).on('click', ".show_these_inputs_correction" , function (event) {
 


            var div_width = $('#body_zone_exercise').width() ;
            var div_height = $('#body_zone_exercise').height() ;
            var slideWidth  = Math.floor(div_width);
            var slideHeight = Math.floor(div_height);

            $(".show_correction").width(slideWidth-40) ; 
            $(".show_correction").height(slideHeight) ;



            event.preventDefault();   
            my_form = document.querySelector("#all_types_form");
            var form_data = new FormData(my_form); 
 
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            form_data.append("csrfmiddlewaretoken" , csrf_token);

            let supportfile_id = $(this).data("supportfile_id") ;
            let loop           = $(this).data("loop") ;
            let choice_id      = $(this).data("choice_id") ;
            form_data.append("supportfile_id" , supportfile_id); 
            form_data.append("loop" , loop); 
            form_data.append("choice_id" , choice_id); 

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    traditional : true,
                    data: form_data,
                    url: "../../check_solution_answers",
                    success: function (data) {
                        $("#score").val(data.score);
                        $("#numexo").val(data.numexo);
                        $("#score_span").html(data.score);
                        $("#numexo_span").html(data.numexo);
                        //********** Gestion de la div de solution ********************
                        $("#show_correction"+loop).show(500);
                        $("#this_correction_text"+loop).html(data.this_correction_text);
                        $("#message_correction"+loop).html(data.msg);
                        //*************************************************************
                        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);    
                    },
                        cache: false,
                        contentType: false,
                        processData: false
                }
            )
         });





    });

});

 
