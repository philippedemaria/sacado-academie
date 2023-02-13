define(['jquery', 'bootstrap', 'ui', 'ui_sortable'], function ($) {
    $(document).ready(function () { 
        console.log("chargement JS ajax-check_vf.js  OKK");





//*************************************************************************************************************  
// Récupération des Vrai/Faux
//************************************************************************************************************* 

    $(document).on('click', ".show_this_vf_correction" , function () {

            let supportfile_id = $(this).data("supportfile_id") ;
            let csrf_token     = $("input[name='csrfmiddlewaretoken']").val();
            let choice_ids     = $(this).data("choice_ids") ;
            let score          = $("#score").val();
            let numexo         = $("#numexo").val();
            let is_correct     = $(this).data("is_correct") ;
            let loop           = $(this).data("loop") ;


            var div_width = $('#body_zone_exercise').width() ;
            var div_height = $('#body_zone_exercise').height() ;
            var slideWidth  = Math.floor(div_width);
            var slideHeight = Math.floor(div_height);

            $(".show_correction").width(slideWidth-40) ; 
            $(".show_correction").height(slideHeight) ;

            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    traditional : true,
                    data: {
                        'supportfile_id' : supportfile_id, 
                        'is_correct'     : is_correct,
                        'choice_ids'     : choice_ids, 
                        'numexo'         : numexo,
                        'score'          : score, 
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../../check_solution_vf",
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
                    }
                }
            )
         });









    });

});

 
