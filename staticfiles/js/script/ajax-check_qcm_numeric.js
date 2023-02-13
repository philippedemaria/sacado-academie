define(['jquery', 'bootstrap', 'ui', 'ui_sortable'], function ($) {
    $(document).ready(function () { 
        console.log("chargement JS ajax-check_qcm_numeric.js  OKK");

 
//*************************************************************************************************************  
// Correction des QCM
//************************************************************************************************************* 
    $(document).on('click', ".show_this_qcm_correction" , function () {


            var div_width = $('#body_zone_exercise').width() ;
            var div_height = $('#body_zone_exercise').height() ;
            var slideWidth  = Math.floor(div_width);
            var slideHeight = Math.floor(div_height);

            $(".show_correction").width(slideWidth-40) ; 
            $(".show_correction").height(slideHeight) ;
        

            let csrf_token     = $("input[name='csrfmiddlewaretoken']").val();
            let supportfile_id = $(this).data("supportfile_id") ;
            let choice_ids     = $(this).data("choice_ids") ;
            let loop           = $(this).data("loop") ;
            let score          = $("#score").val();
            let numexo         = $("#numexo").val();


            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    traditional : true,
                    data: {
                        'supportfile_id': supportfile_id,
                        'choice_ids'       : choice_ids, 
                        'numexo'           : numexo,
                        'score'            : score, 
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "../../check_solution_qcm_numeric",
                    success: function (data) {

                        $("#show_correction"+loop).show(500);
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

 
